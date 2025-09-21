#!/usr/bin/env python3

import itertools

import calc_lib
import numpy


class MaxPointCalculator(calc_lib.ProductionCalculator):
	def calculate(self) -> numpy.ndarray:
		# prep linprog
		A = self.get_default_constraint_matrix()
		b = self.get_default_constraint_vector()
		# split A, b into _ub and _eq
		# force non-sinkable items to be strictly zero
		# otherwise the solver may try to make surplus
		eq_index = self.get_default_net_zero_item_list()
		A_eq = A.loc[eq_index].values
		b_eq = b.loc[eq_index].values
		A_ub = A.drop(index=eq_index).values
		b_ub = b.drop(index=eq_index).values
		# bounds
		bounds = self.get_default_bounds()
		# coef, optimize over points_gain_rate @ x
		c = A.loc["points_gain_rate"].values
		# run linprog
		return super().calculate(
			c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds
		)


if __name__ == "__main__":
	for with_somersloop, clock_speed in itertools.product(
		[False, True], [1, 100, 250]
	):
		calculator = MaxPointCalculator.from_recipe_dataset_json(
			"curated/recipe_dataset.zh-Hans.json",
			production_clock_speed=clock_speed,
			resource_extraction_clock_speed=250,
			enable_resource_conversion=True,
			enable_somersloop_amplification=with_somersloop,
			unfueled_apa_count=0,
			fueled_apa_count=0,
		)

		calculator.calculate()
		fname = ("output/calc.max_point.oc_{}.{}.txt").format(
			clock_speed,
			"with_sloop" if with_somersloop else "wo_sloop",
		)
		with open(fname, "w") as fp:
			calculator.report(fp)
