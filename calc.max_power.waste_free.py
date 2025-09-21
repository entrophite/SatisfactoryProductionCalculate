#!/usr/bin/env python3

import itertools

import calc_lib
import numpy


class MaxPowerWasteFreeCalculator(calc_lib.ProductionCalculator):
	def calculate(self,
		# True to allow plutonium fuel rods to be sinked
		# False to force plutonium fuel rods to be used for power
		allow_plutonium_sink: bool = True,
	) -> numpy.ndarray:
		# prep linprog
		A = self.get_default_constraint_matrix()
		b = self.get_default_constraint_vector()
		# split A, b into _ub and _eq
		# force non-sinkable items to be strictly zero
		# otherwise the solver may try to make surplus
		eq_index = self.get_default_net_zero_item_list()
		if not allow_plutonium_sink:
			eq_index.append("Desc_PlutoniumFuelRod_C")
		A_eq = A.loc[eq_index].values
		b_eq = b.loc[eq_index].values
		A_ub = A.drop(index=eq_index).values
		b_ub = b.drop(index=eq_index).values
		# bounds
		bounds = self.get_default_bounds()
		# coef, optimize over raw_power @ x
		c = A.loc["raw_power"].values
		# run linprog
		return super().calculate(
			c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds
		)


if __name__ == "__main__":
	for with_somersloop, enable_conversion, allow_plutonium_sink in itertools.product(
		[False, True], [False, True], [False, True]
	):
		calculator = MaxPowerWasteFreeCalculator.from_recipe_dataset_json(
			"curated/recipe_dataset.zh-Hans.json",
			production_clock_speed=250,
			resource_extraction_clock_speed=250,
			enable_resource_conversion=enable_conversion,
			enable_somersloop_amplification=with_somersloop,
			unfueled_apa_count=0,
			fueled_apa_count=0,
		)

		calculator.calculate(allow_plutonium_sink)
		fname = ("output/calc.max_power.waste_free.{}{}.{}.txt").format(
			"" if enable_conversion else "wo_conv.",
			"sink_pluto" if allow_plutonium_sink else "ficsonium",
			"with_sloop" if with_somersloop else "wo_sloop",
		)
		with open(fname, "w") as fp:
			calculator.report(fp)
