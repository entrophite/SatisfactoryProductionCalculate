#!/usr/bin/env python3

import functools
import io
import pdb
import sys
from typing import Self

import numpy
import scipy.optimize  # linprog
import pandas

from . import util
from . import config
from .recipe_matrix import RecipeMatrix


class ProductionCalculator(object):
	def __init__(self, recipe_matrix: RecipeMatrix) -> None:
		self.recipe_matrix = recipe_matrix
		# the results of the last calculation
		self._result = None
		return

	@property
	def constraint_matrix_base_(self) -> pandas.DataFrame:
		# take the negative transpose of the coef matrix, while keep the
		# somersloop row not negated
		ret = -self.recipe_matrix.coef_matrix.copy()
		ret["somersloop"] *= -1
		return ret.T

	@property
	def constraint_vector_base_(self) -> pandas.Series:
		# a zero vector with index the same as the coef matrix columns
		# somersloop is pre-filled with global limit
		ret = pandas.Series(0.0, index=self.recipe_matrix.coef_matrix.columns)
		ret["somersloop"] = config.SOMERSLOOP_GLOBAL_LIMIT
		return ret

	@property
	def net_zero_items_base_(self) -> list[str]:
		# returna list of itemclass for intermediate parts
		# intermediate parts have 0 net output (neither input nor output)
		items = self.recipe_matrix.recipe_dataset.items
		matrix_items = self.recipe_matrix.coef_matrix.columns
		ret = list()
		for v in items.values():
			if v.classname not in matrix_items:
				continue
			if (not v.is_sinkable) or (v.category == config.CURATOR_NATIVE_CLASSNAME_RESOURCE_SHORT):
				ret.append(v.classname)
		return ret

	@property
	def result(self) -> scipy.optimize.OptimizeResult | None:
		if self._result is None:
			raise RuntimeError("no result available")
		return self._result

	@functools.wraps(scipy.optimize.linprog)
	def calculate(self, *ka, **kw) -> scipy.optimize.OptimizeResult:
		res = scipy.optimize.linprog(*ka, **kw)
		self._result = res
		if res.success is not True:
			print("linear programming calculating failed.", file=sys.stderr)
			print(f"reason: {res.message}", file=sys.stderr)
			sys.exit(1)
		return res

	def report(self, fp: io.TextIOBase = None) -> None:
		if fp is None:
			fp = sys.stdout
		#
		self._report_recipe_details(fp)
		self._report_net_products(fp)
		self._report_resource_summary(fp)
		return

	def _report_recipe_details(self, fp: io.TextIOBase) -> None:
		items = self.recipe_matrix.recipe_dataset.items
		recipes = self.recipe_matrix.recipe_dataset.recipes
		buildings = self.recipe_matrix.recipe_dataset.buildings

		print(">> Recipe detail", file=fp)
		print("=" * 80, file=fp)
		print(("\t").join(["Recipe", "Machine/count", "Somersloop", "Power",
			"Power production", "Ingredients", "Products"]), file=fp)
		print("=" * 80, file=fp)

		total_power = 0.0
		total_raw_power = 0.0
		total_somersloop = 0.0

		for ix, x in enumerate(self.result.x):
			if x > 1e-8:  # ignore tiny values
				recipe_coef: pandas.Series = self.recipe_matrix.coef_matrix.iloc[ix]
				recipe_classname = recipe_coef.name.split("/")[0]
				if recipe_classname not in recipes:
					continue
				# manufacturer name
				building = recipes[recipe_classname].get_manufacturer(buildings)
				if building is None:
					print(f"warning: recipe '{recipe_classname}' appeared in "
		   				"calculation without a valid manufacturer",
						file=sys.stderr
					)
					building_name = "N/A"
				else:
					building_name = building.display_name
				# somersloop, power and raw power
				total_somersloop += (somersloop := recipe_coef["somersloop"] * x)
				total_power += (power := recipe_coef["power"] * x)
				total_raw_power += (raw_power := recipe_coef["raw_power"] * x)
				# products
				ingredients = list()
				products = list()
				for field, value in recipe_coef.items():
					if field not in items:
						continue
					item = items[field]
					if value < -1e-8:
						ingredients.append(item.item_flux_repr(value * x, decimal=3))
					elif value > 1e-8:
						products.append(item.item_flux_repr(value * x, decimal=3))
				# print row
				lines = [
					recipes[recipe_classname].display_name,
					building_name + " x " + util.simplify_decimal(x, decimal=3),
					util.simplify_decimal(somersloop, decimal=3),
					util.simplify_decimal(power, decimal=1) + "MW",
					util.simplify_decimal(raw_power, decimal=1) + "MW",
					("; ").join(ingredients),
					("; ").join(products),
				]
				print(("\t").join(lines), file=fp)

		print("-" * 80, file=fp)
		# somersloop and power summary
		print(f"Total Somersloop\t{util.simplify_decimal(total_somersloop, decimal=1)}",
			file=fp)
		print(f"Total Power\t\t{util.simplify_decimal(total_power, decimal=1)}MW",
			file=fp)
		print(f"Total Raw Power\t\t\t{util.simplify_decimal(total_raw_power, decimal=1)}MW",
			file=fp)

		print("=" * 80, file=fp)
		return

	def _report_net_products(self, fp: io.TextIOBase) -> None:
		items = self.recipe_matrix.recipe_dataset.items

		print("\n>> Net products", file=fp)
		print("=" * 80, file=fp)
		print(("\t").join(["Item", "Net production", "Sinkpoints"]), file=fp)
		print("-" * 80, file=fp)

		prod = self.recipe_matrix.coef_matrix.T @ self.result.x
		total_sinkpoints = 0
		for itemclass, amount in prod.items():
			if itemclass not in items:
				continue
			if amount < 1e-8:
				continue
			item = items[itemclass]
			if item.is_sinkable:
				sinkpoints = item.rescaled_sink_points(amount * 60)
				total_sinkpoints += sinkpoints
			else:
				sinkpoints = None

			fields = [
				item.display_name,
				util.simplify_decimal(item.rescale_amount(amount * 60)) + "/min.",
				(f"{int(sinkpoints)} pts/min.") if item.is_sinkable else "N/A",
			]
			print(("\t").join(fields), file=fp)

		print("-" * 80, file=fp)
		# total sinkpoints
		line = ("\t").join(["Total sinkpoints", "",
			util.simplify_decimal(total_sinkpoints)])
		print(line, file=fp)
		print("=" * 80, file=fp)
		return

	def _report_resource_summary(self, fp: io.TextIOBase) -> None:
		items = self.recipe_matrix.recipe_dataset.items
		recipes = self.recipe_matrix.recipe_dataset.recipes
		coef_matrix = self.recipe_matrix.coef_matrix

		print("\n>> Resource summary", file=fp)
		print("=" * 80, file=fp)
		print(("\t").join(["Item", "Consumption", "Utilized%"]), file=fp)
		print("-" * 80, file=fp)

		# identify recipe (row) and item (column) names
		resource_proxy_recipes = list()
		for i in coef_matrix.index:
			r, *_ = i.split("/")
			if recipes[r].is_resource_proxy:
				resource_proxy_recipes.append(i)
		resource_itemclass_list = list(config.RESOURCE_GLOBAL_LIMIT.keys())
		# select x
		positions = coef_matrix.index.get_indexer(resource_proxy_recipes)
		x = self.result.x[positions]
		# select coef matrix
		resource_coef_matrix = coef_matrix.reindex(
			index=resource_proxy_recipes,
			columns=resource_itemclass_list,
		)
		resource_consump: pandas.Series = resource_coef_matrix.T @ x

		for itemclass, rate in resource_consump.items():
			if itemclass not in items:
				continue
			item = items[itemclass]
			rate_per_minute = item.rescale_amount(rate) * 60
			global_limit = config.RESOURCE_GLOBAL_LIMIT[itemclass]
			if global_limit > 0:
				perc = rate_per_minute / global_limit * 100
				perc_str = util.simplify_decimal(perc, decimal=1) + "%"
			else:
				perc_str = "N/A"
			fields = [
				item.display_name,
				util.simplify_decimal(rate_per_minute) + "/min.",
				perc_str,
			]
			print(("\t").join(fields), file=fp)
		print("=" * 80, file=fp)

		return
