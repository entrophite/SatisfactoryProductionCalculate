#!/usr/bin/env python3

import calc_lib
import numpy


class MaxPowerWasteProneCalculator(calc_lib.ProductionCalculator):
	def calculate(self) -> numpy.ndarray:
		coef_matrix = self.recipe_matrix.coef_matrix
		global_limit = self.recipe_matrix.global_limit
		# prep linprog
		A = self.constraint_matrix_base_
		b = self.constraint_vector_base_
		# bounds
		bounds = [(0, gl) for gl in global_limit.values]
		# coef, optimize over raw_power @ x
		c = A.loc["raw_power"].values
		# run linprog
		return super().calculate(
			c, A_ub=A, b_ub=b, bounds=bounds
		)


if __name__ == "__main__":
	for with_somersloop in [True, False]:
		recipe_matrix = calc_lib.RecipeMatrix.from_curated_recipe_dataset_json(
			"curated/recipe_dataset.zh-Hans.json",
			production_clock_speed=250,
			resource_extraction_clock_speed=250,
			with_somersloop=with_somersloop,
		)

		calculator = MaxPowerWasteProneCalculator(recipe_matrix)
		calculator.calculate()
		fname = ("output/calc.max_power.waste_prone.{}.txt").format(
			"with_sloop" if with_somersloop else "wo_sloop",
		)
		with open(fname, "w") as fp:
			calculator.report(fp)
