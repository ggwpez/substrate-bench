import argparse
import subprocess
import sys

base_cmd="cargo run --profile=%s --features=runtime-benchmarks --manifest-path=bin/node/cli/Cargo.toml --quiet -- benchmark --chain=dev --execution=wasm --wasm-execution=compiled --steps=50 --repeat=20 --raw"

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--profiles', nargs='+', help='Rust profiles to use')
	parser.add_argument('--pallets', nargs='+', help='Pallets to run')
	parser.add_argument('--cwd', type=str, help='Substrate root directory', default=".")
	return parser.parse_args()

def list_benches(cmd):
	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = p.communicate()
	print(" " + "\n ".join(stdout.decode('utf-8').splitlines()[1:]))

def run_benches(cmd, f, cwd):
	print(cmd)
	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, , cwd=cwd)
	for line in p.stderr:
		line = line.decode('utf-8')
		if "Running Benchmark:" in line:
			sys.stdout.write("\r%s" % line)

	stdout = p.communicate()[0]
	f.write(stdout.decode('utf-8'))

def run_pallet(pallet, profile, f, cwd):
	cmd = (base_cmd % profile) + " --pallet=%s --extrinsic='*'" % pallet
	print("%s: %s.*" % (profile, pallet))
	list_benches(cmd + " --list")
	run_benches(cmd, f, cwd)

def main():
	subprocess.run("mkdir -p results", shell=True)
	args = parse_args()
	for profile in args.profiles:
		fname = "results/%s.txt" % profile
		with open(fname, 'w') as f:
			for pallet in args.pallets:
				run_pallet(pallet, profile, f, args.root)
			print("Wrote to: %s\n" % fname)

if __name__ == '__main__':
	main()
