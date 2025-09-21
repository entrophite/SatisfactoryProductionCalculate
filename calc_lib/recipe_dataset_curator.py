#!/usr/bin/env python3

import json
import pdb
import re
from typing import Self

from . import config
from .elements import Recipe, Item, Building
from .recipe_dataset import RecipeDataset


class RecipeDatasetCurator(RecipeDataset):
	@staticmethod
	def _strip_classname_prefix(s: str) -> str:
		return s.split("'")[-2].split(".")[-1]

	@staticmethod
	def _parse_enclosed_array(s: str) -> list[str]:
		m = re.match(config.CURATOR_ENCLOSED_ARRAY_REGEX, s)
		if not m:
			raise ValueError(f"failed to parse enclosed array: {s}")
		ret = [v.strip("\"") for v in m.groups()]
		return ret

	@staticmethod
	def _parse_item_amount_pair_array(s: str) -> dict:
		# m = re.match(r"^\(?(\(ItemClass=\"([^()]+)\",Amount=(\d+)\),?)*\)?$", s)
		# if m is None:
		# raise ValueError(f"failed to parse item-amount pair array: {s}")
		ret = dict()
		for itemclass, amount in re.findall(config.CURATOR_ITEM_AMOUNT_PAIR_REGEX, s):
			itemclass = RecipeDatasetCurator._strip_classname_prefix(itemclass)
			ret[itemclass] = int(amount)

		if (not ret) and s.strip():
			raise ValueError(f"likely failed to parse item-amount pair array: {s}")
		return ret

	class CuratedItem(Item):
		@classmethod
		def curate_from(cls, d: dict, category: str = None) -> Self:
			new = cls(
				classname=d["ClassName"],
				display_name=d["mDisplayName"],
				form=d["mForm"],
				energy_value=float(d["mEnergyValue"]),
				resource_sink_points=int(d["mResourceSinkPoints"]),
				category=category,
			)
			return new

	class CuratedBuilding(Building):
		@classmethod
		def curate_from(cls, d: dict) -> Self:
			new = cls(
				classname=d["ClassName"],
				display_name=d["mDisplayName"],
				variable_power_consumption=("mEstimatedMininumPowerConsumption" in d),
				power_production=float(d.get("mPowerProduction", 0)),
				power_consumption=float(d["mPowerConsumption"]),
				power_consumption_exponent=float(d["mPowerConsumptionExponent"]),
				production_shard_slot_size=int(d.get("mProductionShardSlotSize", 0)),
				production_shard_boost_multiplier=float(
					d.get("mProductionShardBoostMultiplier", 0.0)),
				production_boost_power_consumption_exponent=float(
					d.get("mProductionBoostPowerConsumptionExponent", 0.0)),
				extract_cycle_time=float(d.get("mExtractCycleTime", 0.0)),
				items_per_cycle=int(d.get("mItemsPerCycle", 0)),
			)
			return new

	class CuratedRecipe(Recipe):
		@classmethod
		def curate_from(cls, d: dict, items: dict[str, Item]) -> Self:
			# parse ingredients & products
			new = cls(
				classname=d["ClassName"],
				display_name=d["mDisplayName"],
				ingredients=RecipeDatasetCurator._parse_item_amount_pair_array(
					d["mIngredients"]),
				products=RecipeDatasetCurator._parse_item_amount_pair_array(
					d["mProduct"]),
				manufacturing_duration=float(d["mManufactoringDuration"]),
				produced_in=[v.split(".")[-1].strip("\"") for v in
					d["mProducedIn"].strip("()").split(",")],
				global_limit=int(d.get("mGlobalLimit", -1)),
				variable_power_consumption_constant=float(
					d["mVariablePowerConsumptionConstant"]
				),
				variable_power_consumption_factor=float(
					d["mVariablePowerConsumptionFactor"]
				),
				raw_sink_points_gain=0,  # later by .calculate_sink_points()
				sinkable_points_gain=0,  # later by .calculate_sink_points()
			)
			return new

	@classmethod
	def _dictize(cls, data: list[dict[str]]) -> dict[str, dict[str]]:
		ret = {d["NativeClass"]: d for d in data}
		return ret

	@classmethod
	def curate_from_docs_json(cls, fname: str, *, encoding="utf-16") -> Self:
		# load data
		with open(fname, "r", encoding=encoding) as fp:
			data = cls._dictize(json.load(fp))
		ret = cls()
		# item & building before recipe
		ret._curate_items(data)
		ret._curate_buildings(data)
		# recipe needs item data to calculate points gain
		ret._curate_recipes(data)
		# these must be called after the above three
		# some already-parsed data might be used to create these recipes
		ret._add_apa_building_and_proxy_recipes(data)
		ret._add_generator_proxy_recipes(data)
		ret._add_resource_proxy_recipes(data)
		# calculate sink points gain for all recipes
		ret._fill_sink_points_gain()
		return ret

	def _curate_items(self, data: dict[str, dict[str]]) -> None:
		for d in config.CURATOR_NATIVE_CLASSNAME_LIST_ITEM:
			category = self._strip_classname_prefix(d)
			for item in data[d]["Classes"]:
				self.add(self.CuratedItem.curate_from(item, category=category))
		return

	def _curate_buildings(self, data: dict[str, dict[str]]) -> None:
		for d in config.CURATOR_NATIVE_CLASSNAME_LIST_BUILDING:
			for building in data[d]["Classes"]:
				self.add(self.CuratedBuilding.curate_from(building))
		return

	def _curate_recipes(self, data: dict[str, dict[str]]) -> None:
		for d in config.CURATOR_NATIVE_CLASSNAME_LIST_RECIPE:
			for recipe in data[d]["Classes"]:
				self.add(self.CuratedRecipe.curate_from(recipe, self.items))
		return

	def _add_generator_proxy_recipes(self, data: dict[str, dict[str]]) -> None:
		# treat generator functionalities as standard 'recipes' and add them to
		# the recipe collection
		for d in config.CURATOR_NATIVE_CLASSNAME_LIST_GENERATOR:
			for generator in data[d]["Classes"]:

				power_prod = float(generator["mPowerProduction"])
				for fuel in generator["mFuel"]:

					fuel_itemclass = fuel["mFuelClass"]
					fuel_amount = 1  # always 1
					cycle_time = self.items[fuel_itemclass].energy_value / power_prod

					# add fuel to ingredients
					ingredients = {fuel_itemclass: fuel_amount}
					# add supplemental resource (water)
					if generator["mRequiresSupplementalResource"] == "True":
						supple_itemclass = fuel["mSupplementalResourceClass"]
						supple_to_power_ratio = float(generator["mSupplementalToPowerRatio"])
						supple_amount = power_prod * supple_to_power_ratio * cycle_time
						ingredients[supple_itemclass] = int(supple_amount)

					# byproducts as product
					products = dict()
					if (byproduct_itemclass := fuel["mByproduct"]):
						byproduct_amount = int(fuel["mByproductAmount"])
						products[byproduct_itemclass] = byproduct_amount

					# recipe object
					recipe = self.CuratedRecipe(
						classname=f"{generator['ClassName']}-{fuel_itemclass}",
						display_name=f"{generator['mDisplayName']} ({self.items[fuel_itemclass].display_name})",
						ingredients=ingredients,
						products=products,
						manufacturing_duration=cycle_time,
						produced_in=[generator["ClassName"]],
					)

					self.add(recipe)
		return

	def _add_apa_building_and_proxy_recipes(self, data: dict[str, dict[str]]
	) -> None:
		for d in config.CURATOR_NATIVE_CLASSNAME_LIST_POWERBOOSTER:
			for powerbooster in data[d]["Classes"]:
				# building object
				building = self.CuratedBuilding(
					classname=powerbooster["ClassName"],
					display_name=powerbooster["mDisplayName"],
					power_production=float(powerbooster["mBasePowerProduction"]),
					base_power_boost=float(powerbooster["mBaseBoostPercentage"]),
					# not in docs.json, or i don't know how to calculate it
					fueled_power_boost=0.3,  # so hard-codede
				)
				self.add(building)

				# unfueled recipe
				recipe = self.CuratedRecipe(
					classname=f"{powerbooster['ClassName']}-Unfueled",
					display_name=f"{powerbooster['mDisplayName']} (Unfueled)",
					ingredients=dict(),
					products=dict(),
					manufacturing_duration=1.0,
					produced_in=[powerbooster["ClassName"]],
					global_limit=0,
					overclockable=False,
				)
				self.add(recipe)

				# fueled recipe
				fuel_classes = [s.split(".")[1] for s in
					self._parse_enclosed_array(powerbooster["mDefaultFuelClasses"])]

				for itemclass in fuel_classes:
					item = self.items[itemclass]
					recipe = self.CuratedRecipe(
						classname=f"{powerbooster['ClassName']}-{itemclass}",
						display_name=f"{powerbooster['mDisplayName']} ({item.display_name})",
						ingredients={itemclass: 1},
						products=dict(),
						# not in docs.json, or i don't know how to calculate it
						manufacturing_duration=12.0,  # so hard-codede
						produced_in=[powerbooster["ClassName"]],
						global_limit=0,
						overclockable=False,
					)
					self.add(recipe)

		return

	def _add_resource_proxy_recipes(self, data: dict[str, dict[str]]) -> None:
		# add resource extraction as 'recipes' to the recipe collection
		self._add_resource_node_proxy_recipes()
		self._add_resource_well_proxy_recipes()
		self._add_unrestrained_resource_proxy_recipes()
		self._add_geothermal_proxy_recipes()
		return

	def _add_resource_node_proxy_recipes(self) -> None:
		for itemclass, purity_counts in config.RESOURCE_NODE_CONFIG.items():
			item = self.items[itemclass]
			for b in config.RESOURCE_NODE_EXTRACTOR_CONFIG[itemclass]:
				# extractor object
				extractor = self.buildings[b]
				#
				# add per purity, count as recipe global limit
				for purity, count in purity_counts.items():
					purity_config = config.RESOURCE_NODE_PURITY_CONFIG[purity]

					if count <= 0:
						continue  # skip if no node at this purity level

					recipe = self.CuratedRecipe(
						classname=("ResourceNode-{}-{}-{}").format(
							extractor.classname, item.classname, purity_config["label"],
						),
						display_name=("{} ({}, {})").format(
							extractor.display_name, item.display_name, purity_config["label"],
						),
						ingredients=dict(),
						products={item.classname: extractor.items_per_cycle
							* purity_config["multiplier"]
						},
						manufacturing_duration=extractor.extract_cycle_time,
						produced_in=[extractor.classname],
						global_limit=count,
						is_resource_proxy=True,
					)

					self.add(recipe)
		return

	def _add_resource_well_proxy_recipes(self) -> None:
		for itemclass, well_clusters in config.RESOURCE_WELL_CONFIG.items():
			item = self.items[itemclass]
			for b in config.RESOURCE_WELL_ACTIVATOR_LIST:
				# activator object
				activator = self.buildings[b]
				#
				# add by location, in well clusters
				for location, cluster_sum_rate in well_clusters.items():

					recipe = self.CuratedRecipe(
						classname=("ResourceWell-{}-{}-{}").format(
							activator.classname, item.classname, location,
						),
						display_name=("{} ({}, {})").format(
							activator.display_name, item.display_name, location,
						),
						ingredients=dict(),
						products={item.classname: cluster_sum_rate},
						manufacturing_duration=1,  # always 1
						produced_in=[activator.classname],
						global_limit=1,  # always 1
						is_resource_proxy=True,
					)

					self.add(recipe)
		return

	def _add_unrestrained_resource_proxy_recipes(self) -> None:
		for itemclass, buildings in config.UNRESTRAINED_RESOURCE_CONFIG.items():
			item = self.items[itemclass]
			for b in buildings:
				# extractor object
				extractor = self.buildings[b]
				#
				recipe = self.CuratedRecipe(
					classname=("ResourceMisc-{}-{}").format(
						extractor.classname, item.classname,
					),
					display_name=("{} ({})").format(
						extractor.display_name, item.display_name,
					),
					ingredients=dict(),
					products={item.classname: extractor.items_per_cycle},
					manufacturing_duration=extractor.extract_cycle_time,
					produced_in=[extractor.classname],
					is_resource_proxy=True,
				)

				self.add(recipe)
		return

	def _add_geothermal_proxy_recipes(self) -> None:
		generator = self.buildings[config.RESOURCE_NODE_GEYSER_GENERATOR]
		for purity, count in config.RESOURCE_NODE_GEYSER_CONFIG.items():
			purity_config = config.RESOURCE_NODE_PURITY_CONFIG[purity]
			#
			recipe = self.CuratedRecipe(
				classname=("ResourceNode-{}-{}").format(
					generator.classname, purity_config["label"],
				),
				display_name=("{} ({})").format(
					generator.display_name, purity_config["label"],
				),
				ingredients=dict(),
				products=dict(),
				manufacturing_duration=1,
				produced_in=[generator.classname],
				global_limit=count,
				is_resource_proxy=True,
				overclockable=False,
			)

			self.add(recipe)
		return

	def _fill_sink_points_gain(self) -> None:
		for r in self.recipes.values():
			r.calculate_sink_points(self.items)
		return
