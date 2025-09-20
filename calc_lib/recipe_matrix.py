#!/usr/bin/env python3

import itertools
import pdb
from typing import Self

import pandas

from .elements import ClockSpeed, Recipe, Building, Item
from .recipe_dataset import RecipeDataset
from . import config


class RecipeMatrix(object):
	def __init__(self, recipe_dataset: RecipeDataset, *ka,
		production_clock_speed: ClockSpeed = ClockSpeed(100),
		resource_extraction_clock_speed: ClockSpeed = ClockSpeed(250),
		with_somersloop: bool = False, **kw,
	) -> None:
		super().__init__(*ka, **kw)
		# basic data attributes
		self.recipe_dataset: RecipeDataset = recipe_dataset
		self.production_clock_speed: ClockSpeed = ClockSpeed(production_clock_speed)
		self.resource_extraction_clock_speed: ClockSpeed = ClockSpeed(
			resource_extraction_clock_speed)
		self.with_somersloop: bool = with_somersloop
		# the coefficient matrix for the recipes
		# coefs are in units of items/second
		self.coef_matrix: pandas.DataFrame = None
		# the global production limit for each recipe
		# may be used for resource extraction limits
		self.global_limit: pandas.Series = None
		# construct .coef_matrix and .global_limit
		self._construct_matrices()
		return

	def _construct_matrices(self) -> None:
		# these are updated in-place by related methods
		coef_rows = list[pandas.Series]()  # rows in coef matrix
		global_limit = pandas.Series(dtype=float)

		# fill-in regular recipes
		for recipe in self.recipe_dataset.recipes.values():
			self._append_regular_recipe(coef_rows, global_limit, recipe=recipe)

		# concat coef matrix rows into a matrix
		# take transpose so that each row is a recipe
		coef_matrix = pandas.concat(coef_rows, axis=1).T
		# fill NaNs with 0
		coef_matrix = coef_matrix.fillna(0)

		# update attributes
		self.coef_matrix = coef_matrix
		self.global_limit = global_limit
		return

	@classmethod
	def from_curated_recipe_dataset_json(cls, fname: str, *,
		production_clock_speed: ClockSpeed = ClockSpeed(100),
		resource_extraction_clock_speed: ClockSpeed = ClockSpeed(250),
		with_somersloop: bool = False,
	) -> Self:
		ret = cls(RecipeDataset.from_json(fname),
			production_clock_speed=production_clock_speed,
			resource_extraction_clock_speed=resource_extraction_clock_speed,
			with_somersloop=with_somersloop,
		)
		return ret

	@staticmethod
	def _basic_coef_matrix_row(name: str, *, somersloop: int = 0,
		power: float = 0.0, sink_points_rate: float = 0.0
	) -> pandas.Series:
		# somersloop: for somersloop count
		# power: for net power
		# raw_power: for raw power production
		row = pandas.Series(0.0, name=name,
			index=["somersloop", "power", "raw_power", "points_gain_rate",],
		)
		row["somersloop"] = somersloop
		row["power"] = power
		if power > 0:
			row["raw_power"] = power
		row["points_gain_rate"] = sink_points_rate
		return row

	def _append_regular_recipe(self, coef_rows_extern: list[pandas.Series],
		global_limit_extern: pandas.Series, *, recipe: Recipe,
		# allow temporary change below settings
		production_clock_speed: ClockSpeed = None,
		resource_clock_speed: ClockSpeed = None,
		with_somersloop: bool = None,
	) -> None:
		if production_clock_speed is None:
			production_clock_speed = self.production_clock_speed
		if resource_clock_speed is None:
			resource_clock_speed = self.resource_extraction_clock_speed
		if with_somersloop is None:
			with_somersloop = self.with_somersloop

		# find a building that can run this recipe
		building = recipe.get_manufacturer(self.recipe_dataset.buildings)
		if building is None:
			# no need to do anything if no building can run this recipe
			return

		# list of #somersloops that can be installed
		somersloops = range(0, building.production_shard_slot_size + 1) \
			if with_somersloop else range(0, 1)  # essentially only [0]

		# list of clock speed to consider
		if recipe.is_resource_proxy:
			clock_speeds = [resource_clock_speed]
		else:
			# always consider 250%
			clock_speeds = list({production_clock_speed, ClockSpeed(250)})

		# add a row for each somersloop count
		for somersloop, clock_speed in itertools.product(somersloops, clock_speeds):
			cycles_per_second = (clock_speed / 100) / recipe.manufacturing_duration
			prod_multiplier = building.get_production_multiplier(somersloop)
			# use the recipe in-game classname as index postfixed by
			# somersloop count
			index = f"{recipe.classname}/S{somersloop}_OC{clock_speed}"

			# construct the row
			row = self._basic_coef_matrix_row(index, somersloop=somersloop,
				power=building.get_adjusted_power(clock_speed, somersloop,
					recipe=recipe,
				),
				sink_points_rate=recipe.get_production_sink_points_gain(
					items=self.recipe_dataset.items,
					prod_multiplier=prod_multiplier,
					cycles_per_second=cycles_per_second,
					sinkable_only=True,
				)
			)
			# add ingredients and products
			for k, v in recipe.ingredients.items():
				row[k] = -v * cycles_per_second  # ingredients not affected by boost
			for k, v in recipe.products.items():
				row[k] = v * prod_multiplier * cycles_per_second

			# append to coef matrix rows
			coef_rows_extern.append(row)
			# global limit related
			recipe_global_limit = recipe.global_limit
			global_limit_extern[index] = float("inf") \
				if recipe_global_limit < 0 else recipe_global_limit

		return
