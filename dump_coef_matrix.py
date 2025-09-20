#!/usr/bin/env python3

import argparse

import calc_lib


def main() -> None:
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--input", type=str, required=True,
		metavar="json",
		help="input curated json file (required)")
	parser.add_argument("-o", "--output", type=str, required=True,
		metavar="txt",
		help="output matrix as tsv file (required)")
	parser.add_argument("-c", "--production-clock-speed",
		type=calc_lib.ClockSpeed, default=100, metavar="1-250",
		help="Set the production clock speed (1-250) [100]")
	parser.add_argument("-r", "--resource-extraction-clock-speed",
		type=calc_lib.ClockSpeed, default=250, metavar="1-250",
		help="Set the resource extraction clock speed (1-250) [250]")
	parser.add_argument("-s", "--with-somersloop", action="store_true",
		help="Consider production-boosted recipes with Somersloop [no]")

	args = parser.parse_args()

	recipe_matrix = calc_lib.RecipeMatrix.from_curated_recipe_dataset_json(
		args.input,
		production_clock_speed=args.production_clock_speed,
		resource_extraction_clock_speed=args.resource_extraction_clock_speed,
		with_somersloop=args.with_somersloop,
	)

	recipe_matrix.coef_matrix.to_csv(args.output, sep="\t", index=True)
	return


if __name__ == "__main__":
	main()
