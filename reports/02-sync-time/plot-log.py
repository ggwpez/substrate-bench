import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d

import re
import argparse
import datetime

class Timing:
	def __init__(self, time, block):
		self.time = time
		self.block = block
	
	def __str__(self):
		return "%s: %s" % (self.time, self.block)

def main():
	args = parse_args()
	files = args.files
	
	#plt.style.use('dark_background')
	fig, ax1 = plt.subplots()
	# Set the background color to gray.
	ax2 = ax1.twinx()

	for filename in files:
		x = []
		y = []
	
		timings = parse_file(filename)
		# Save the first timing as starting time.
		start = next(timings).time
		for timing in timings:
			# Subtract the start time from the timing.
			timing.time = timing.time - start
			# Convert the timing to seconds.
			x.append(timing.time.total_seconds())
			y.append(timing.block)

		# Plot the derivative.
		diff = np.diff(y)/np.diff(x)
		#diff = gaussian_filter1d(diff, 6)

		title = filename.split("/")[-1].split(".")[0]
		ax1.plot(x[:-1], diff, linewidth=1, label=title)		
		# Plot value.
		ax2.plot(x, y, linewidth=1, label=title)

	# Config and show the plot.
	plt.subplots_adjust(left=0.1, right=.9, top=0.9, bottom=0.1)
	plt.title("Polkadot import-blocks time and speed.\nThe shaky graph is the speed.")
	ax1.set_xlabel("Sync time [s]")
	ax1.set_ylabel("Sync speed [bps] (higher is better)")
	ax2.set_ylabel("Blocks (higher is better)")
	plt.legend()
	#plt.show()
	plt.savefig("import-blocks.png")

def parse_file(filename):
	with open(filename) as f:
		for line in f:
			timing = parse_line(line)
			if timing:
				yield timing
			

def parse_line(line) -> Timing:
	# Extract the date and time with milliseconds.
	match = re.search(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line).group(0)
	# Convert the datetime to a python type.
	time = datetime.datetime.strptime(match, "%Y-%m-%d %H:%M:%S")
	# Extract thee "Current best block: <int>".
	maybe_block = re.search(r"Current best block: (\d+)", line)
	if maybe_block:
		return Timing(time, int(maybe_block.group(1)))
	else:
		return None

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("files", nargs="+")
	return parser.parse_args()

if __name__ == "__main__":
	main()
