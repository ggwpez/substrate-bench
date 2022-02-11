import argparse
import numpy as np
import matplotlib.pyplot as plt
import json
from scipy.cluster.vq import vq, kmeans, whiten

def plot(x, y, ax, label):
	ax.scatter(x, y, alpha=0.33, label=label)
	ax.set_xscale("log")
	ax.set_yscale("log")
	ax.set_xlabel("lg Size [byte]")
	ax.set_ylabel("lg Time [µs]")

def formula(x):
	CUTOFF = 10000.0
	CHEAP = 80.0
	SLOPE = 0.001

	return CHEAP + max(0, SLOPE * (x - CUTOFF))

def draw_formula(len, ax):
	x = np.arange(len)
	y = np.vectorize(formula)(x)
	ax.set_xscale("log")
	ax.set_yscale("log")
	ax.plot(x, y, c='black', label="80 + max(0, (x - 10000) / 1000)")
	ax.legend()

def main(paths):
	l = 0
	for path in paths:
		(s, t) = parse_json(path)
		print("Plotting {}".format(path))
		s_median = np.median(s)
		t_median = np.median(t)
		l = max(s)

		# Put a title.
		if len(paths) == 1:
			plt.title("Reading all %d top storage values from Kusama\nTotal read %.1f MB (median %.0f Byte), Total elapsed %.3f s (median %.2f µs)" % (len(s), sum(s) / 1000000.0, s_median, sum(t) / 1000000.0, t_median))
		else:
			plt.title("Comparing {}. (lower is better)".format(", ".join(paths)))

		# Create a new axis.
		ax = plt.subplot(111)
		plot(s, t, ax, path.split("/")[-1].split(".")[0])
		ax.legend()

	ax = plt.subplot(111)
	draw_formula(l, ax)

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

		return x, y

def parse_args():
	parser = argparse.ArgumentParser(description="Plot the results of the benchmark.")
	parser.add_argument("-i", nargs="+", help="Path to the json files.")
	args = parser.parse_args()
	return args

if __name__ == "__main__":
    main(parse_args().i)
