#!/usr/bin/env python3

import calc_lib
import numpy


class MaxPowerWasteFreeCalculator(calc_lib.ProductionCalculator):
	def calc_max_raw_power(self,
		# True to allow plutonium fuel rods to be sinked
		# False to force plutonium fuel rods to be used for power
		allow_plutonium_sink: bool = True,
	) -> numpy.ndarray:
		coef_matrix = self.recipe_matrix.coef_matrix
		global_limit = self.recipe_matrix.global_limit
		# prep linprog
		A = self.constraint_matrix_base_
		b = self.constraint_vector_base_
		# split A, b into _ub and _eq
		# force non-sinkable items to be strictly zero
		# otherwise the solver may try to make surplus
		eq_index = self.net_zero_items_base_
		if not allow_plutonium_sink:
			eq_index.append("Desc_PlutoniumFuelRod_C")
		A_eq = A.loc[eq_index].values
		b_eq = b.loc[eq_index].values
		A_ub = A.drop(index=eq_index).values
		b_ub = b.drop(index=eq_index).values
		# bounds
		bounds = [(0, gl) for gl in global_limit.values]
		# coef, optimize over raw_power @ x
		c = A.loc["raw_power"].values
		# run linprog
		res = self.calculate(
			c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds
		)
		return res


if __name__ == "__main__":
	for with_somersloop in [True, False]:
		recipe_matrix = calc_lib.RecipeMatrix.from_curated_recipe_dataset_json(
			"curated/recipe_dataset.zh-Hans.json",
			production_clock_speed=250,
			resource_extraction_clock_speed=250,
			with_somersloop=with_somersloop,
		)

		for allow_plutonium_sink in [True, False]:
			calculator = MaxPowerWasteFreeCalculator(recipe_matrix)
			calculator.calc_max_raw_power(allow_plutonium_sink)
			fname = ("output/calc.max_power.waste_free.{}.{}.txt").format(
				"sink_pluto" if allow_plutonium_sink else "ficsonium",
				"with_sloop" if with_somersloop else "wo_sloop",
			)
			with open(fname, "w") as fp:
				calculator.report(fp)
