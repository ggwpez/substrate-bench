import argparse
import subprocess
import datetime

base_compile = "cargo build --profile=%s --locked --features=runtime-benchmarks --features=runtime-benchmarks --manifest-path=bin/node/cli/Cargo.toml"
bench = "./target/%s/substrate benchmark --chain=dev --steps=50 --repeat=20 --pallet='%s' --extrinsic='%s' --execution=wasm --wasm-execution compiled --output=%s/weights.rs --template=.maintain/frame-weight-template.hbs --header=HEADER-APACHE2 --raw"

def main(args):
	subprocess.run("mkdir -p %s" % args.raw_dir, shell=True)

	# Compile all pallets. Otherwise `cargo run` would re-compile each pallet.
	if args.no_compile:
		log("Compiling ... SKIPPED")
	else:
		log("Compiling ...")
		compile(args)		
	
	# List all available benchmarks.	
	log("Listing ...")
	per_pallet = list_benches(args)
	pallets = per_pallet.keys()
	
	# Run all benchmarks.
	for i, pallet in enumerate(pallets):
		msg = "[%d/%d] %s: %d cases" % (i+1, len(pallets), pallet, len(per_pallet[pallet]))
		if pallet in args.skip:
			log(msg + " ... SKIPPED")
			continue
		log(msg + " ...")
		run_cases(pallet, args)
	
	log("🎉 Raws written to '%s', weights to '%s'" % (args.raw_dir, args.weight_dir))
	log("You can enact the new weights with\ncp -RT %s/frame %s/frame" % (args.weight_dir, args.cwd))

def run_cases(pallet, args):
	# Create the weight output directory.
	name = "-".join(pallet.split("_")[1:])	# Cut off the `frame_` or `pallet_` prefix.
	out_dir = "%s/frame/%s/src/" % (args.weight_dir, name)
	subprocess.run("mkdir -p %s" % out_dir, shell=True)
	
	# Run all the cases for this pallet.gs
	cmd = bench % (args.profile, pallet, "*", out_dir)
	with open("%s/%s.csv" % (args.raw_dir, pallet), "w") as f:
		p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=args.cwd)
		stdout, stderr = p.communicate()
		# check the exit code of the process.
		if p.returncode != 0:
			raise Exception("Rust:\n\n%s\nfrom:%s" % (stderr.decode('utf-8'), cmd))
		f.write(stdout.decode('utf-8'))

def compile(args):
	cmd = base_compile % args.profile
	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=args.cwd)
	stdout, stderr = p.communicate()
	# check the exit code of the process.
	if p.returncode != 0:
		raise Exception("Rust:\n\n%s" % stderr.decode('utf-8'))

def list_benches(args):
	cmd = bench % (args.profile, "*", "*", ".")  + " --list"
	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=args.cwd)
	stdout, stderr = p.communicate()
	# check the exit code of the process.
	if p.returncode != 0:
		raise Exception("Rust:\n\n%s" % stderr.decode('utf-8'))
	cases = stdout.decode('utf-8').splitlines()[1:] # Cut off the CSV header.
	# Find which cases are there per pallet.
	per_pallet = {}
	for case in cases:
		pallet, _, _ = case.partition(",")
		if pallet not in per_pallet:
			per_pallet[pallet] = [case]
		else:
			per_pallet[pallet].append(case)
	log("Running %d cases across %d pallets. Skipping %d pallets." % (len(cases), len(per_pallet), len(args.skip)))
	# Check that skip is a subset of the per_pallet.keys.
	for pallet in args.skip:
		if pallet not in per_pallet:
			raise Exception("Pallet %s is not found in the benchmark list." % pallet)
	return per_pallet

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--profile', type=str, help='Rust profile')
	parser.add_argument('--cwd', type=str, help='Substrate root directory', default=".")
	parser.add_argument('--skip', nargs='+', help='Comma-separated list of pallets to skip.', default="")
	parser.add_argument('--no-compile', action='store_true', help='Skip compilation.')
	parser.add_argument('--weight-dir', type=str, help='Weight output directory', default=None)
	parser.add_argument('--raw-dir', type=str, help='Raw output directory', default=None)
	args = parser.parse_args()
	if args.weight_dir is None:
		args.weight_dir = "weights-%s" % args.profile
	if args.raw_dir is None:
		args.raw_dir = "raw-%s" % args.profile
	return args

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

def log(msg):
	print("%s: %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))

if __name__ == '__main__':
	main(parse_args())
