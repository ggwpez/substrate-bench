# The cost of a unique transfer

## What is a unique transfer?

A transfer to an account that does not exist.  
If the transferred amount is at least the *existential deposit*, a new account will be created.  
Creating a new account is more costly than transferring to an existing account, therefore this case is of special interest.  


## The setup

This works on any Substrate chain and has the following steps:

1. Start the chain in `--dev` mode, granting *Alice* 10k tokens
2. Use *Alice* to fund 10k new *Bob* accounts
3. Use *Bob* accounts to transfer funds to 10k new *Charlie* accounts, called unique transfer
4. Stop the chain
5. Use the `benchmark-block` command to re-execute the full block and compare it to its weight.

## Walk through

I use [Polkadot] as example here, but you can also use just plain [Substrate].

1. Start the node in dev mode:  

```sh
# Make sure /tmp/dot-dev does not already exist from a previous run
polkadot --dev --base-path /tmp/dot-dev --pool-limit 100000
```
We do not need to use the wasm executor here, only in the benchmark run later.

The base path is important as is otherwise uses a temporary directory. The pool limit prepares the node
for the massive amount of extrinsics.

2,3. Use the [sender.py](sender.py) script to send all the transactions:
```sh
pip install substrate-interface # only needeed once
python sender.py
```
Wait until the script finishes, which can take a while since it is deriving a log of accounts.

4. Have a look at the chain, you should be seeing blocks being imported with lots of extrinsics:  
```pre

```

On ref hardware:
```pre
$ ./target/production/polkadot benchmark-block --chain dot-spec-1M-accs.json --repeat 1 --from 39 --to 49 --execution wasm --wasm-execution compiled --pruning archive -d uniques/

# 10.8k transfers from //Alice to //Bob/i (endowed)
Block 39 with  4315 tx used  56.01% of its weight (   689,243,081 of  1,230,606,763 ns)
Block 40 with  5299 tx used  53.82% of its weight (   812,306,104 of  1,509,238,171 ns)
Block 41 with  1192 tx used  52.93% of its weight (   183,292,975 of    346,291,837 ns)

# 10.8k transfers from //Bob/i (dies) to //Charlie/i (endowed)
Block 46 with  5299 tx used  67.04% of its weight ( 1,011,772,407 of  1,509,238,171 ns)
Block 47 with  5299 tx used  65.75% of its weight (   992,298,518 of  1,509,238,171 ns)
Block 48 with   208 tx used  69.95% of its weight (    47,328,881 of     67,660,429 ns)
Block 49 with     2 tx used  69.93% of its weight (     6,524,096 of      9,329,057 ns)
```

A rerun with `--repeat 10` looks very similar, so those are not outliers.


```pre
$ ./target/production/polkadot benchmark-block --base-path uniques/ --chain dot-1M-accs-spec.json --execution wasm --wasm-execution compiled --from 35 --to 54 --pruning archive --repeat 1

# transfer Alice to Bob/i (endowed)
Block 36 with  1633 tx used  72.27% of its weight (   265,170,096 of    366,929,821 ns)
Block 37 with  6134 tx used  71.78% of its weight (   974,131,450 of  1,357,091,308 ns)
Block 38 with  6233 tx used  68.84% of its weight (   949,168,572 of  1,378,870,021 ns)
Block 39 with  2008 tx used  66.62% of its weight (   299,416,588 of    449,424,946 ns)

# transfer_keep_alive Bob/i to Charlie/i (endowed)
ns)
Block 44 with  5453 tx used  87.24% of its weight ( 1,013,646,507 of  1,161,856,978 ns)
Block 45 with  6412 tx used  85.03% of its weight ( 1,160,527,493 of  1,364,833,164 ns)
Block 46 with  4141 tx used  84.28% of its weight (   745,168,967 of    884,166,930 ns)

# transfer Bob/i (dies) to Dora/i (endowed)
Block 51 with  5839 tx used  84.62% of its weight ( 1,093,420,986 of  1,292,195,143 ns)
Block 52 with  5648 tx used  84.27% of its weight ( 1,053,525,815 of  1,250,177,626 ns)
Block 53 with  4519 tx used  84.66% of its weight (   848,160,349 of  1,001,812,303 ns)
```

[Polkadot]: https://github.com/paritytech/polkadot
[Substrate]: https://github.com/paritytech/substrate
