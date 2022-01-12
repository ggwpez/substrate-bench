import sys
import re
import csv
import numpy as np
import argparse
import matplotlib.pyplot as plt
from itertools import islice

class Result:
	def __init__(self, meta, timing):
		self.meta = meta
		self.timing = timing

	# Can create plots for functions with 0, 1 and 2 params.
	def plot(self, ax, label):
		params = self.meta.params
		arity = len(params)
		# Assume that xyz exist, may or may not be valid.
		x = self.timing.matrix[:, 0]
		y = self.timing.matrix[:, 1]
		z = self.timing.matrix[:, 2]

		if arity == 0:
			ax.hist(x, label=label, bins=200, alpha=1)
			#hist, bins = np.histogram(x, bins=200)
			#ax.plot(bins[:-1], hist, label=label)
			ax.set_ylabel('Occurences')
			ax.set_xlabel('Weight (further left is better)')
		elif arity == 1:
			ax.scatter(x, y, label=label, alpha=.5)
			ax.set_ylabel('Weight (lower is better)')
		elif arity == 2:
			ax.scatter(x, y, z, label=label, alpha=.5)
			ax.set_zlabel('Weight (lower is better)')
		else:
			raise Exception("Cannot show functions with arity > 2")
		
class Meta:
	def __init__(self, pallet, ext, steps, reps, params):
		self.pallet = pallet
		self.ext = ext
		self.steps = steps
		self.reps = reps
		self.params = params

	def title(self):
		return "%s.%s(%s), [s=%s, r=%s]" % (self.pallet, self.ext, ",".join(self.params), self.steps, self.reps)

class Timing:
	def __init__(self):
		self.matrix = None

	def append_row(self, row):
		if self.matrix is None:
			self.matrix = np.empty((0, len(row)))
		self.matrix = np.vstack((self.matrix, row))

def main():
	args = parse_args()
	files = args.files
	# Build a map that maps title x filename => results.
	results = {}
	for filename in files:
		for r in parse_file(filename, args):
			if r.meta.title() not in results:
				results[r.meta.title()] = {}
			results[r.meta.title()][filename] = r		


	print("Baseline is %s." % files[0])
	many = args.rows * args.cols
	for chunk in chunks(results, many):
		fig = plt.figure()
		fig.set_size_inches(38.4, 21.6, forward=True)
		fig.tight_layout()
		fig.subplots_adjust(top=.95, bottom=.05, left=.05, right=.95, hspace=.2, wspace=.1)
		for (i, title) in enumerate(chunk):
			# Metadata is the same in all files, so just take 0.
			meta = results[title][files[0]].meta
			if len(results[title]) != len(files):
				raise Exception("Extrinsic %s missing some file." % title)

			if len(meta.params) == 2:
				ax = fig.add_subplot(args.rows, args.cols, i+1, projection="3d")
			else:
				ax = fig.add_subplot(args.rows, args.cols, i+1)
			ax.set_title(meta.title())
			for i, file in enumerate(results[title]):
				r = results[title][file]
				#ax = fig.add_subplot(1, len(files), i+1, projection='3d')
				r.plot(ax, file.split("/")[-1].split(".")[0])
			# Auto-generate legend for ax.
			ax.legend()

		fig.text(0.5, 0.01, "source at github.com/ggwpez/substrate-bench", ha='center')
		# Show plt as full screen without toolbar.
		#mng = plt.get_current_fig_manager()
		#mng.window.showMaximized()

		plt.savefig("out.png")
		return
		#plt.show()
		

def parse_file(filename, args):
	lines = read_file_lines(filename)
	# Walk through the lines starting with "Pallet" and print their line-number.
	results = []
	for i, line in enumerate(lines):
		if line.startswith("Pallet"):
			meta = parse_meta(i, lines)
			if not re.match(args.title, meta.title()) or len(meta.params) not in args.arity:
				continue
			timings = parse_timings(i+2, lines, meta)
			results.append(Result(meta, timings))
	print("%s: parsed %d extrinsics." % (filename, len(results)))
	return results

def parse_meta(i, lines) -> Meta:
	# Extract result meta-data.
	pallet = re.search(r"Pallet: \"([^\"]*)\"", lines[i]).group(1)
	ext = re.search(r"Extrinsic: \"([^\"]*)\"", lines[i]).group(1)
	steps = re.search(r"Steps: (\d*)", lines[i]).group(1)
	reps = re.search(r"Repeat: (\d*)", lines[i]).group(1)
	# Check CVS header.
	header = "extrinsic_time_ns,storage_root_time_ns,reads,repeat_reads,writes,repeat_writes,proof_size_bytes"
	if not lines[i+1].endswith(header):
		raise Exception("CSV header wrong.", header)
	# Parse CSV.
	res = Meta(pallet, ext, steps, reps, [])
	if not lines[i+1].startswith(header):
		params = re.search(r"^((\w),)*", lines[i+1])
		for param in params.group(0).split(","):
			if param == "":
				continue
			res.params.append(param)
	return res

def parse_timings(i, lines, meta) -> Timing:
	# Parse all lines as CSV.
	res = Timing()
	while lines[i] != "":
		data = [float(i) for i in lines[i].split(",")]
		res.append_row(data)
		i += 1
	return res

def read_file_lines(filename):
	with open(filename, "r") as f:
		return f.read().splitlines()

def parse_args():
	parser = argparse.ArgumentParser(description='Visualize benchmark results.')
	parser.add_argument('files', nargs='+', help='Raw benchmark .txt files')
	parser.add_argument('--title', type=str, default=".*", help='Regex for bench title')
	parser.add_argument('--arity', nargs='+', default=[0,1,2], type=int, help='Filter for function arity')
	parser.add_argument('--grid', default='1x1', type=str, help='Grid of how many plots to show at once')

	args = parser.parse_args()
	print("Filtering for '%s' bench title" % args.title)
	print("Filtering for '%s' bench arity" % ", ".join(map(str, args.arity)))
	print("Analyzing files %d files: %s" % (len(args.files), ", ".join(args.files)))
	args.cols, args.rows = map(int, args.grid.split("x"))
	return args

def chunks(data, size):
    it = iter(data)
    for i in range(0, len(data), size):
        yield {k:data[k] for k in islice(it, size)}

if __name__ == "__main__":
	main()
