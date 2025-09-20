#!/usr/bin/env python3

import calc_lib
import numpy


class MaxPointCalculator(calc_lib.ProductionCalculator):
	def calculate(self) -> numpy.ndarray:
		coef_matrix = self.recipe_matrix.coef_matrix
		global_limit = self.recipe_matrix.global_limit
		# prep linprog
		A = self.constraint_matrix_base_
		b = self.constraint_vector_base_
		# split A, b into _ub and _eq
		# force non-sinkable items to be strictly zero
		# otherwise the solver may try to make surplus
		eq_index = self.net_zero_items_base_
		A_eq = A.loc[eq_index].values
		b_eq = b.loc[eq_index].values
		A_ub = A.drop(index=eq_index).values
		b_ub = b.drop(index=eq_index).values
		# bounds
		bounds = [(0, gl) for gl in global_limit.values]
		# coef, optimize over points_gain_rate @ x
		c = A.loc["points_gain_rate"].values
		# run linprog
		return super().calculate(
			c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds
		)


if __name__ == "__main__":
	for clock_speed in [1, 100, 250]:
		recipe_matrix = calc_lib.RecipeMatrix.from_curated_recipe_dataset_json(
			"curated/recipe_dataset.zh-Hans.json",
			production_clock_speed=clock_speed,
			resource_extraction_clock_speed=250,
			with_somersloop=True,
		)

		calculator = MaxPointCalculator(recipe_matrix)
		calculator.calculate()
		fname = ("output/calc.max_point.oc_{}.with_sloop.txt").format(
			clock_speed
		)
		with open(fname, "w") as fp:
			calculator.report(fp)
