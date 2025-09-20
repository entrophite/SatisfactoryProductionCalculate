#!/usr/bin/env python3

import argparse
import pdb
from typing import Self

import calc_lib


def get_args():
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--input", type=str, metavar="json", required=True,
		help="the game's original docs.json dump to parse [required]")
	ap.add_argument("-o", "--output", type=str, metavar="json", required=True,
		help="output json (required)")

	# parse and refine args
	args = ap.parse_args()

	return args


def main():
	args = get_args()
	dataset = calc_lib.RecipeDatasetCurator.curate_from_docs_json(args.input)
	dataset.to_json(args.output)
	return


if __name__ == "__main__":
	main()
