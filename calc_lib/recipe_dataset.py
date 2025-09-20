#!/usr/bin/env python3

import dataclasses
import functools
import json
import pdb
from typing import Self

from .elements import Recipe, Building, Item


@dataclasses.dataclass
class RecipeDataset(object):
	recipes: dict[str, Recipe] = dataclasses.field(default_factory=dict)
	buildings: dict[str, Building] = dataclasses.field(default_factory=dict)
	items: dict[str, Item] = dataclasses.field(default_factory=dict)

	def add(self, obj: Recipe | Building | Item) -> None:
		if isinstance(obj, Recipe):
			self.recipes[obj.classname] = obj
		elif isinstance(obj, Building):
			self.buildings[obj.classname] = obj
		elif isinstance(obj, Item):
			self.items[obj.classname] = obj
		else:
			raise TypeError(f"unsupported type: {type(obj).__name__}")
		return

	def to_json(self, fname: str) -> None:
		with open(fname, "w") as fp:
			json.dump(dataclasses.asdict(self), fp, indent="\t", sort_keys=True)
		return

	@classmethod
	def from_json(cls, fname: str) -> Self:
		with open(fname, "r") as fp:
			data = json.load(fp)
		new = cls()
		for r in data["recipes"].values():
			new.add(Recipe(**r))
		for b in data["buildings"].values():
			new.add(Building(**b))
		for i in data["items"].values():
			new.add(Item(**i))
		return new

	@functools.cached_property
	def raw_resources(self) -> set[str]:
		# raw resources are items that cannot be produced by recipes
		products = set()
		for r in self.recipes.values():
			products.update(r.products.keys())
		all_items = set(self.items.keys())
		return all_items - products
