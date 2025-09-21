#!/usr/bin/env python3

import gzip
import pickle

import matplotlib
import matplotlib.pyplot
import matplotlib.patches
import numpy

matplotlib.pyplot.rcParams["font.family"] = "Hei"


def plot_apa_grid(fname: str, upper_data: dict, lower_data: dict, *,
	upper_label: str, lower_label: str, suptitle: str = None,
) -> None:
	figure = matplotlib.pyplot.figure(figsize=(6, 7), dpi=300)
	axes = figure.add_subplot(1, 1, 1)

	# lower triangle
	lower_cmap = matplotlib.colormaps["Reds"]
	values = numpy.full((13, 13), numpy.nan)
	for (unfueled, fueled), result in lower_data.items():
		values[unfueled, fueled] = -result["result"].fun / 1e6
	vmax = numpy.nanmax(values)
	axes.pcolor(values, cmap=lower_cmap, vmin=0, vmax=vmax)
	# add text
	for i, j in numpy.ndindex(values.shape):
		if numpy.isnan(v := values[i, j]):
			continue
		axes.text(j + 0.5, i + 0.5, f"{v:.1f}", fontsize=6,
			color=("#000000" if v < vmax / 2 else "#ffffff"),
			ha="center", va="center",
		)
		# add box for the maximum value
		if v == vmax:
			p = matplotlib.patches.Rectangle((j, i), 1, 1,
				fill=False, edgecolor="#ffd500", linewidth=1.5,
			)
			axes.add_patch(p)

	# upper triangle
	upper_cmap = matplotlib.colormaps["Blues"]
	values = numpy.full((13, 13), numpy.nan)
	for (unfueled, fueled), result in upper_data.items():
		values[12 - unfueled, 12 - fueled] = -result["result"].fun / 1e6
	vmax = numpy.nanmax(values)
	axes.pcolor(values, cmap=upper_cmap, vmin=0, vmax=vmax)
	# add text
	for i, j in numpy.ndindex(values.shape):
		if numpy.isnan(v := values[i, j]):
			continue
		axes.text(j + 0.5, i + 0.5, f"{v:.1f}", fontsize=6,
			color=("#000000" if v < vmax / 2 else "#ffffff"),
			ha="center", va="center",
		)
		# add box for the maximum value
		if v == vmax:
			p = matplotlib.patches.Rectangle((j, i), 1, 1,
				fill=False, edgecolor="#00fbff", linewidth=1.5,
			)
			axes.add_patch(p)

	# legends
	handles = [
		matplotlib.patches.Patch(color=lower_cmap(0.5), label=lower_label),
		matplotlib.patches.Patch(color=upper_cmap(0.5), label=upper_label),
	]
	axes.legend(handles=handles, loc="upper center", fontsize=12,
		bbox_to_anchor=(0.5, -0.10), ncol=2,
		handlelength=0.8,
	)

	#
	for sp in axes.spines.values():
		sp.set_visible(False)
	axes.tick_params(
		left=False, right=False, top=False, bottom=False,
	)
	axes.set(
		xlim=(0, 13), ylim=(0, 13),
		xticks=numpy.arange(11) + 0.5,
		yticks=numpy.arange(11) + 0.5,
		xticklabels=numpy.arange(11),
		yticklabels=numpy.arange(11),
		xlabel="APA (有矩阵)",
		ylabel="APA (无矩阵)",
	)
	# pseudo-labels for the upper triangle
	for i in range(0, 11):
		axes.text(12.5 - i, 13.4, str(i), fontsize=10,
			ha="center", va="center",
		)
		axes.text(13.2, 12.5 - i, str(i), fontsize=10,
			ha="left", va="center",
		)
	axes.text(6.5, 14.0, "APA (有矩阵)", fontsize=10,
		ha="center", va="center",
	)
	axes.text(14.0, 6.5, "APA (无矩阵)", fontsize=10, rotation=270,
		ha="center", va="center",
	)

	figure.suptitle(suptitle, fontsize=16)
	figure.tight_layout()

	figure.savefig(fname, dpi=300)
	matplotlib.pyplot.close(figure)
	return


if __name__ == "__main__":
	with gzip.open("large_output/apa_grid.max_power.waste_free.pkl.gz", "rb") as fp:
		data = pickle.load(fp)

	plot_apa_grid("large_output/apa_grid.max_power.wate_free.conv.sink_ploto.plot.png",
		# with_somersloop, enable_conversion, sink plutonium
		upper_data=data[(False, True, True)],
		upper_label="无红石",
		lower_data=data[(True, True, True)],
		lower_label="有红石",
		suptitle="无废料，有转化，钚回收",
	)

	plot_apa_grid("large_output/apa_grid.max_power.wate_free.conv.ficsonium.png",
		# with_somersloop, enable_conversion, sink plutonium
		upper_data=data[(False, True, False)],
		upper_label="无红石",
		lower_data=data[(True, True, False)],
		lower_label="有红石",
		suptitle="无废料，有转化，铀钚镄",
	)

	plot_apa_grid("large_output/apa_grid.max_power.wate_free.no_conv.sink_ploto.plot.png",
		# with_somersloop, enable_conversion, sink plutonium
		upper_data=data[(False, False, True)],
		upper_label="无红石",
		lower_data=data[(True, False, True)],
		lower_label="有红石",
		suptitle="无废料，无转化，钚回收",
	)

	plot_apa_grid("large_output/apa_grid.max_power.wate_free.no_conv.ficsonium.png",
		# with_somersloop, enable_conversion, sink plutonium
		upper_data=data[(False, False, False)],
		upper_label="无红石",
		lower_data=data[(True, False, False)],
		lower_label="有红石",
		suptitle="无废料，无转化，铀钚镄",
	)

	with gzip.open("large_output/apa_grid.max_power.waste_prone.pkl.gz", "rb") as fp:
		data = pickle.load(fp)

	plot_apa_grid("large_output/apa_grid.max_power.waste_prone.no_conv.comp.png",
		# with_somersloop, enable_conversion
		upper_data=data[(False, False)],
		upper_label="无红石",
		lower_data=data[(True, False)],
		lower_label="有红石",
		suptitle="允许钚废料，禁用转化"
	)

	plot_apa_grid("large_output/apa_grid.max_power.waste_prone.conv.comp.png",
		# with_somersloop, enable_conversion
		upper_data=data[(False, True)],
		upper_label="无红石",
		lower_data=data[(True, True)],
		lower_label="有红石",
		suptitle="允许钚废料，允许转化"
	)
