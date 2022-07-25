from substrateinterface import SubstrateInterface, Keypair
from substrateinterface.exceptions import StorageFunctionNotFound, SubstrateRequestException
import time

substrate = SubstrateInterface(
	url="ws://127.0.0.1:9944",
)

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def balance_of(acc):
    result = substrate.query(
        module='System',
        storage_function='Account',
        params=[acc.ss58_address]
    )
    return result.value['data']['free']

def send_all(extrinsics):
    print("Sending %s extrinsics to the node" % len(extrinsics))
    
    for chunk in chunks(extrinsics[:-1], 128):
        for extrinsic in chunk:
            try:
                substrate.submit_extrinsic(extrinsic)

            except SubstrateRequestException as e:
                print("Failed to send: {}".format(e))

    # Wait for the last one.
    last = extrinsics[len(extrinsics) - 1]
    receipt = substrate.submit_extrinsic(last, wait_for_finalization=True)
    print("Extrinsic finalized in block '{}'".format(receipt.block_hash))

ED = substrate.get_constant("Balances", "ExistentialDeposit").value
ED_MUL = 10
num = 5400*2
DOT = 10 ** 10
initial = 1_000_000 * DOT
balance = ED * ED_MUL
balance2 = ED * (ED_MUL - 1)

alice = Keypair.create_from_uri('//Alice')
bal = balance_of(alice)

if bal < initial:
    raise Exception("Wrong balance for alice")

print("Deriving accounts and signing transactions, this takes a while")
(extrinsics, extrinsics2) = ([], [])
for i in range(0, num):
    # Alice funds bob
    bob = Keypair.create_from_uri('//Bob/%s' % i)
    call = substrate.compose_call(
        call_module='Balances',
        call_function='transfer',
        call_params={
            'dest': bob.ss58_address,
            'value': balance
        }
    )
    extrinsics.append(substrate.create_signed_extrinsic(call=call, keypair=alice, nonce=i))

    # Bob unique funds Charlie
    charlie = Keypair.create_from_uri('//Charlie/%s' % i)
    call = substrate.compose_call(
        call_module='Balances',
        call_function='transfer',
        call_params={
            'dest': charlie.ss58_address,
            'value': balance2
        }
    )

    extrinsics2.append(substrate.create_signed_extrinsic(call=call, keypair=bob, nonce=0))

    if i % 1000 == 0 and i != 0:
        print("Progress i=%s/%s" % (i, num))

print("Sending %s unique transfers Alice -> Bob/i" % len(extrinsics))
send_all(extrinsics)
print("Alice has %s Plank" % balance_of(alice))
time.sleep(10)
print("Sending %s unique transfers Bob/i -> Charlie/i where Bob/i dies" % len(extrinsics))
send_all(extrinsics2)
