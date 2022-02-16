import argparse
import numpy as np
import matplotlib.pyplot as plt
import json
from scipy.cluster.vq import vq, kmeans, whiten
import scipy.stats as stats

def plot(x, y, ax, label):
	ax.scatter(x, y, alpha=.33, label=label)
	ax.set_xlabel("Size [byte]")
	ax.set_ylabel("Time [µs]")

def simple_formula(x):
	CUTOFF = 32786.0
	CHEAP = 80.0
	SLOPE = 0.001

	return CHEAP + max(0, SLOPE * (x - CUTOFF))

def calc_error(last, to):
	return np.sum((last - to) ** 2)

def find_slope(last_s, last_t):
	# Calculate the slope of the last part of the data.
	slope, intercept, r_value, p_value, std_err = stats.linregress(last_s, last_t)
	print("Slope: {}, p: {}".format(slope, p_value))
	return slope

def better_formula(s, t, p):
	CUTOFF = 32786.0

	# Find the index of the first element that is greater than the cutoff.
	i = 0
	while i < len(s) and s[i] < CUTOFF:
		i += 1
	i = len(s) -1
	first = t[:i]
	# Calculate the p percentile of the first part of the data.
	cheap = np.percentile(first, p)
	SLOPE = find_slope(s, t)

	print("Cheap {}%: {}. Slope: {}".format(p, cheap, SLOPE))
	return (cheap, lambda x: cheap + SLOPE * x)

def draw_formula(s, t, ax, label):
	x = np.arange(max(s))

	for (p, c) in [(99, 'red'), (95, 'orange')]:
		(cheap, f) = better_formula(s, t, p)
		y = np.vectorize(f)(x)
		ax.plot(x, y, c=c, label=("%.2dp: %.2f µs" % (p, cheap)))

def main(args):
	l = 0
	paths = args.i
	fig = plt.figure()
	fig.suptitle("Storage reads")
	
	for path in paths:
		(s, t) = parse_json(path)
		name = path.split("/")[-1].split(".")[0]
		print("Plotting {} with {} values".format(name, len(s)))
		print("99.99p: {}".format(np.percentile(t, 99.99)))

		# Put a title.
		#if len(paths) == 1:
		#	plt.title("Reading all %d top storage values from Kusama\nTotal read %.1f MB (median %.0f Byte), Total elapsed %.3f s (median %.2f µs)" % (len(s), sum(s) / 1000000.0, s_median, sum(t) / 1000000.0, t_median))
		#else:
		#	plt.title("Comparing {}. (lower is better)".format(", ".join(paths)))

		if args.hist:
			MIN, MAX = min(s), max(s)
			left, width = 0.05, 0.85
			bottom, height = 0.1, 0.65
			spacing = 0.005

			rect_scatter = [left, bottom, width, height]
			rect_histx = [left, bottom + height + spacing, width, 0.2]
			rect_histy = [left + width + spacing, bottom, 0.2, height]

			if path == paths[0]:
				ax = fig.add_axes(rect_scatter)
				ax_histx = fig.add_axes(rect_histx, sharex=ax)
			#ax_histx.set_yscale("log")
			#ax_histx.hist(s, bins=100)
			ax_histx.set_xscale("log")
			ax_histx.hist(s, bins=10 ** np.linspace(np.log10(MIN), np.log10(MAX), 100))
		elif path == paths[0]:
			ax = fig.add_subplot(111)

		if args.formula:
			draw_formula(s, t, ax, name.split("_")[-1])
		plot(s, t, ax, name)
		
		if args.log:
			ax.set_xscale("log")
			ax.set_yscale("log")
			ax.set_xlabel("lg {}".format(ax.xaxis.get_label().get_text()))
			ax.set_ylabel("lg {}".format(ax.yaxis.get_label().get_text()))
	ax.legend()
	#for l in range(9):
	#	ax.axvline(32768+4096*l, c='black', ls='--', label="32768 + 4096 * i")
	#	if l == 0:

	plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
	plt.show()

def parse_json(path):
	with open(path, "r") as f:
		data = json.load(f)

		x = []
		y = []
		for i in data["time_by_size"]:
			x.append(float(i[0]))
			y.append(i[1] / 1000.0)

		# Sort and return.
		return zip(*sorted(list(zip(x, y))))

def parse_args():
	parser = argparse.ArgumentParser(description="Plot the results of the benchmark.")
	parser.add_argument("-i", nargs="+", help="Path to the json files.")
	
	parser.add_argument('--hist', dest='hist', action='store_true')
	parser.add_argument('--no-hist', dest='hist', action='store_false')
	parser.set_defaults(hist=True)
	
	parser.add_argument('--formula', dest='formula', action='store_true')
	parser.add_argument('--no-formula', dest='formula', action='store_false')
	parser.set_defaults(formula=True)

	parser.add_argument('--log', dest='log', action='store_true')
	parser.add_argument('--no-log', dest='log', action='store_false')
	parser.set_defaults(log=True)

	return parser.parse_args()

if __name__ == "__main__":
    main(parse_args())
