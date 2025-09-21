#!/usr/bin/env python3

import itertools

import calc_lib
import numpy


class MaxPowerWasteProneCalculator(calc_lib.ProductionCalculator):
	def calculate(self) -> numpy.ndarray:
		# prep linprog
		A = self.get_default_constraint_matrix()
		b = self.get_default_constraint_vector()
		# bounds
		bounds = self.get_default_bounds()
		# coef, optimize over raw_power @ x
		c = A.loc["raw_power"].values
		# run linprog
		return super().calculate(c, A_ub=A, b_ub=b, bounds=bounds)


if __name__ == "__main__":
	for with_somersloop in [True, False]:
		calculator = MaxPowerWasteProneCalculator.from_recipe_dataset_json(
			"curated/recipe_dataset.zh-Hans.json",
			production_clock_speed=250,
			resource_extraction_clock_speed=250,
			enable_resource_conversion=True,
			enable_somersloop_amplification=with_somersloop,
			unfueled_apa_count=0,
			fueled_apa_count=0,
		)

		calculator.calculate()
		fname = ("output/calc.max_power.waste_prone.{}.txt").format(
			"with_sloop" if with_somersloop else "wo_sloop",
		)
		with open(fname, "w") as fp:
			calculator.report(fp)
