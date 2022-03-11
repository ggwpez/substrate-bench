import argparse
import subprocess
import datetime

base_compile = "cargo build --profile=%s --locked --features=runtime-benchmarks --features=runtime-benchmarks --manifest-path=bin/node/cli/Cargo.toml"
bench = "./target/%s/substrate benchmark --chain=%s --steps=%s --repeat=%s --pallet='%s' --extrinsic='%s' --execution=wasm --wasm-execution=compiled --heap-pages=4096 --output=%s/weights.rs --template=.maintain/frame-weight-template.hbs --header=HEADER-APACHE2 --json-file %s"

def main(args):
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
	
	log("🎉 Weights in '%s', json output in '%s'" % (args.weight_dir, args.json_dir))
	log("You can enact the new weights with\ncp -RT %s/frame %s/frame" % (args.weight_dir, args.cwd))

def run_cases(pallet, args):
	# Create the weight output directory.
	name = "-".join(pallet.split("_")[1:])	# Cut off the `frame_` or `pallet_` prefix.
	out_dir = "%s/frame/%s/src/" % (args.weight_dir, name)
	subprocess.run("mkdir -p %s" % out_dir, shell=True)
	
	# Run all the cases for this pallet.
	cmd = bench % (args.profile, args.runtime, args.steps, args.repeat, pallet, "*", out_dir, args.json_dir)
	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=args.cwd)
	# Wait for the process to finish.
	stdout, stderr = p.communicate()
	# check the exit code of the process.
	if p.returncode != 0:
		raise Exception("Rust:\n\n%s\nfrom:%s" % (stderr.decode('utf-8'), cmd))

def compile(args):
	cmd = base_compile % args.profile
	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=args.cwd)
	stdout, stderr = p.communicate()
	# check the exit code of the process.
	if p.returncode != 0:
		raise Exception("Rust:\n\n%s" % stderr.decode('utf-8'))

def list_benches(args):
	cmd = bench % (args.profile, args.runtime, "1", "1", "*", "*", ".", ".")  + " --list"
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
	parser.add_argument('--profile', type=str, help='Rust profile', default="production")
	parser.add_argument('--cwd', type=str, help='Substrate root directory', default=".")
	parser.add_argument('--runtime', type=str, help='Substrate runtime', default='dev')
	parser.add_argument('--skip', nargs='+', help='List of pallets to skip.', default="")
	parser.add_argument('--no-compile', action='store_true', help='Skip compilation.')
	parser.add_argument('--weight-dir', type=str, help='Relative weight output directory', default=None)
	parser.add_argument('--json-dir', type=str, help='Relative json output directory', default=None)
	parser.add_argument('--repeat', type=int, help='Repeat the benchmark this many times.', default=20)
	parser.add_argument('--steps', type=int, help='Number of resolution steps per benchmark.', default=50)
	parser.add_argument('--debug', action='store_true', help='Debug mode.')
	args = parser.parse_args()
	if args.debug:
		args.repeat = 1
		args.steps = 1
		args.profile = 'release'

	if args.weight_dir is None:
		args.weight_dir = "%s/weights-%s" % (args.cwd, args.profile)
	if args.json_dir is None:
		args.json_dir = "%s/json-%s" % (args.cwd, args.profile)
	if args.profile is None:
		parser.error("--profile is required. Use 'production' for real benchmarking results but takes forever to compile.")
	
	return args

def help():
	print("""
Usage:
  ./run.py [--cwd <path to substrate>] [--runtime <RUNTIME>] [--debug]

Options:
  --profile: Rust profile to use.
  --cwd: Substrate root directory.
  --runtime: Runtime to use.
  --skip: List of pallets to skip.
  --no-compile: Skip compilation.
  --weight-dir: Relative weight output directory.
  --json-dir: Relative json output directory.
  --repeat: Repeat the benchmark this many times.
  --steps: Number of resolution steps per benchmark.

Example for debugging the script (use this first):
  ./run.py --debug --cwd ~/substrate/

is equivalent to:
  python run.py --profile release --cwd ~/substrate/ --steps 1 --repeat 1

Example for real results on ref hardware:
  python run.py --cwd ~/substrate/
""")

def log(msg):
	print("%s: %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))

if __name__ == '__main__':
	main(parse_args())
