#!/usr/bin/env python3

import gzip
import itertools
import pickle

import numpy
import tqdm
import calc_lib


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


def apa_grid_waste_free_gen():
	all_res = dict()

	for with_somersloop, enable_conversion, allow_plutonium_sink in itertools.product(
		[False, True], [False, True], [False, True],
	):
		# grid search apa count
		args = list()
		for unfueled_apa in range(0, 11):  # max 10
			for fueled_apa in range(0, 11 - unfueled_apa):  # max 10 total
				args.append((unfueled_apa, fueled_apa))

		apa_res = dict()
		for unfueled_apa, fueled_apa in tqdm.tqdm(args):
			calculator = MaxPowerWasteFreeCalculator.from_recipe_dataset_json(
				"curated/recipe_dataset.zh-Hans.json",
				production_clock_speed=250,
				resource_extraction_clock_speed=250,
				enable_resource_conversion=enable_conversion,
				enable_somersloop_amplification=with_somersloop,
				unfueled_apa_count=unfueled_apa,
				fueled_apa_count=fueled_apa,
			)

			result = calculator.calculate(allow_plutonium_sink)

			apa_res[(unfueled_apa, fueled_apa)] = dict(
				result=result,
				coef_matrix=calculator.recipe_matrix.coef_matrix,
			)

		all_res[(with_somersloop, enable_conversion, allow_plutonium_sink)] = apa_res

	with gzip.open("large_output/apa_grid.max_power.waste_free.pkl.gz", "wb") as fp:
		pickle.dump(all_res, fp)

	return


def apa_grid_waste_prone_gen():
	all_res = dict()

	for with_somersloop, enable_conversion in itertools.product(
		[False, True], [False, True],
	):
		# grid search apa count
		args = list()
		for unfueled_apa in range(0, 11):  # max 10
			for fueled_apa in range(0, 11 - unfueled_apa):  # max 10 total
				args.append((unfueled_apa, fueled_apa))

		apa_res = dict()
		for unfueled_apa, fueled_apa in tqdm.tqdm(args):
			calculator = MaxPowerWasteProneCalculator.from_recipe_dataset_json(
				"curated/recipe_dataset.zh-Hans.json",
				production_clock_speed=250,
				resource_extraction_clock_speed=250,
				enable_resource_conversion=enable_conversion,
				enable_somersloop_amplification=with_somersloop,
				unfueled_apa_count=unfueled_apa,
				fueled_apa_count=fueled_apa,
			)
			result = calculator.calculate()
			apa_res[(unfueled_apa, fueled_apa)] = dict(
				result=result,
				coef_matrix=calculator.recipe_matrix.coef_matrix,
			)

		all_res[(with_somersloop, enable_conversion)] = apa_res

	with gzip.open("large_output/apa_grid.max_power.waste_prone.pkl.gz", "wb") as fp:
		pickle.dump(all_res, fp)

	return


if __name__ == "__main__":
	apa_grid_waste_free_gen()
	apa_grid_waste_prone_gen()
