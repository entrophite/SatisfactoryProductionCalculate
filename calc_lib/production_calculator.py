#!/usr/bin/env python3

import functools
import io
import pdb
import sys
from typing import Self

import scipy.optimize  # linprog
import pandas

from . import util
from . import config
from .elements import ClockSpeed
from .recipe_matrix import RecipeMatrix


class ProductionCalculator(object):
	@classmethod
	def from_recipe_dataset_json(cls, fname: str, *,
		production_clock_speed: int = ClockSpeed(250),
		resource_extraction_clock_speed: int = ClockSpeed(250),
		enable_resource_conversion: bool = False,
		enable_somersloop_amplification: bool = False,
		unfueled_apa_count: int = 0,
		fueled_apa_count: int = 0,
	) -> Self:
		recipe_matrix = RecipeMatrix.from_curated_recipe_dataset_json(fname,
			production_clock_speed=production_clock_speed,
			resource_extraction_clock_speed=resource_extraction_clock_speed,
			with_somersloop=enable_somersloop_amplification,
		)
		ret = cls(recipe_matrix,
			enable_resource_conversion=enable_resource_conversion,
			enable_somersloop_amplification=enable_somersloop_amplification,
			unfueled_apa_count=unfueled_apa_count,
			fueled_apa_count=fueled_apa_count,
		)
		return ret

	def __init__(self, recipe_matrix: RecipeMatrix, *,
		enable_resource_conversion: bool = False,
		enable_somersloop_amplification: bool = False,
		unfueled_apa_count: int = 0,
		fueled_apa_count: int = 0,
	) -> None:
		self.recipe_matrix = recipe_matrix
		# the results of the last calculation
		self._result = None
		self.enable_resource_conversion = enable_resource_conversion
		self.enable_somersloop_amplification = enable_somersloop_amplification
		self.unfueled_apa_count = unfueled_apa_count
		self.fueled_apa_count = fueled_apa_count
		if (self.unfueled_apa_count < 0) or (self.fueled_apa_count < 0):
			raise ValueError("APA count must be non-negative")
		if (self.fueled_apa_count + self.unfueled_apa_count) > 10:
			raise ValueError("the total APA count must be at most 10")
		self._update_recipe_matrix_power_boost()
		return

	@property
	def total_apa_count(self) -> int:
		return self.unfueled_apa_count + self.fueled_apa_count

	@property
	def total_apa_power_boost(self) -> float:
		building = self.recipe_matrix.recipe_dataset.buildings[config.POWER_BOOST_BUILDING_LIST[0]]
		ret = building.base_power_boost * self.unfueled_apa_count \
			+ building.fueled_power_boost * self.fueled_apa_count
		return ret

	def _update_recipe_matrix_power_boost(self) -> None:
		if self.total_apa_count == 0:
			return
		coef_matrix = self.recipe_matrix.coef_matrix
		mask = coef_matrix["power"] > 0
		coef_matrix.loc[mask, "power"] *= (1 + self.total_apa_power_boost)
		coef_matrix.loc[mask, "raw_power"] *= (1 + self.total_apa_power_boost)
		return

	def get_default_constraint_matrix(self) -> pandas.DataFrame:
		# take the negative transpose of the coef matrix
		ret = -self.recipe_matrix.coef_matrix.copy()
		# keep the somersloop row not negated
		ret["somersloop"] *= -1
		return ret.T

	def get_default_constraint_vector(self) -> pandas.Series:
		# a zero vector with index the same as the coef matrix columns
		# somersloop is pre-filled with global limit
		ret = pandas.Series(0.0, index=self.recipe_matrix.coef_matrix.columns)
		somersloop = config.SOMERSLOOP_GLOBAL_LIMIT
		total_apa = self.total_apa_count
		if self.enable_somersloop_amplification and (total_apa > 0):
			somersloop -= 3  # require 3 to unlock both in tech tree
		elif self.enable_somersloop_amplification or (total_apa > 0):
			somersloop -= 2  # require 2 to unlock either
		# each apa cotst 10 somersloops
		somersloop -= total_apa * 10
		if somersloop < 0:
			raise RuntimeError("somersloop limit is negative, cannot proceed")
		ret["somersloop"] = somersloop
		return ret

	def get_default_net_zero_item_list(self) -> list[str]:
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

	def get_default_bounds(self) -> list[tuple[float, float]]:
		# return a list of (min, max) for each recipe (row)
		# by default min is always 0, but can be changed for net production
		# max is global limit for resource proxy recipes, inf for others
		recipes = self.recipe_matrix.recipe_dataset.recipes
		buildings = self.recipe_matrix.recipe_dataset.buildings
		global_limit = self.recipe_matrix.global_limit
		ret = []
		for r, gl in global_limit.items():
			r_classname: str = r.split("/")[0]
			recipe = recipes[r_classname]
			if r_classname in config.RESOURCE_CONVERTER_RECIPE_LIST:
				# deal with resource conversion
				ret.append((0, gl if self.enable_resource_conversion else 0))
			elif recipe.get_manufacturer(buildings).classname in config.POWER_BOOST_BUILDING_LIST:
				# deal with power boost building (apa)
				v = self.unfueled_apa_count if r_classname.endswith("Unfueled") \
					else self.fueled_apa_count
				ret.append((v, v))  # force fixed value
			else:
				ret.append((0, gl))
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
			"Ingredients", "Products"]), file=fp)
		print("=" * 80, file=fp)

		ampli_somersloop = 0.0
		total_power_draw = 0.0
		total_power_prod = 0.0

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
				ampli_somersloop += (somersloop := recipe_coef["somersloop"] * x)
				if ((power := recipe_coef["power"] * x) > 0):
					total_power_prod += power
				else:
					total_power_draw += power
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
					("; ").join(ingredients),
					("; ").join(products),
				]
				print(("\t").join(lines), file=fp)

		print("-" * 80, file=fp)
		# somersloop and power summary
		print(f"Somersloops in amplification\t{util.simplify_decimal(ampli_somersloop, decimal=1)}",
			file=fp)
		print(f"Somersloops in APA\t{(self.unfueled_apa_count + self.fueled_apa_count) * 10}",
			file=fp)
		print(f"APA power boost\t+{int(self.total_apa_power_boost * 100)}%",
			file=fp)
		print(f"Total net power\t{util.simplify_decimal(total_power_prod + total_power_draw, decimal=1)}MW",
			file=fp)
		print(f"Total raw power\t{util.simplify_decimal(total_power_prod, decimal=1)}MW",
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
		print(("\t").join(["Item", "Consumption", "Utilized"]), file=fp)
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
