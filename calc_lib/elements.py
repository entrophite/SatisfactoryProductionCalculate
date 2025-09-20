#!/usr/bin/env python3

import dataclasses
import pdb
from typing import Optional

from . import util
from . import config


class ClockSpeed(int):
	def __new__(cls, x=100):
		new = super().__new__(cls, x)
		if new < 1 or new > 250:
			raise ValueError("ClockSpeed must be between 0 and 250")
		return new


@dataclasses.dataclass
class Item(object):
	classname: str
	display_name: str
	form: str
	energy_value: float = 0.0
	resource_sink_points: int = 0
	category: str = None

	@property
	def is_solid(self) -> bool:
		return self.form == "RF_SOLID"

	@property
	def is_liquid(self) -> bool:
		return self.form == "RF_LIQUID"

	@property
	def is_gas(self) -> bool:
		return self.form == "RF_GAS"

	@property
	def is_fluid(self) -> bool:
		return self.is_liquid or self.is_gas

	def rescale_amount(self, amount: float) -> float:
		# liquid/gas amount is 1000x larger as it appears
		if self.is_liquid or self.is_gas:
			amount /= 1000
		return amount

	def rescaled_sink_points(self, amount: float, *, sinkable_only: bool = False,
	) -> float:
		if (not self.is_sinkable) and sinkable_only:
			ret = 0.0
		else:
			ret = self.resource_sink_points * self.rescale_amount(amount)
		return ret

	@property
	def is_sinkable(self) -> bool:
		return self.is_solid and (self.resource_sink_points > 0)

	def item_flux_repr(self, amout_per_second: float, *, decimal: int = 3) -> str:
		# return a string representation of the item flux in /min
		amount_per_minute = self.rescale_amount(amout_per_second * 60)
		amount_str = util.simplify_decimal(amount_per_minute, decimal)
		return f"{self.display_name} [{amount_str}/min]"


@dataclasses.dataclass
class Recipe(object):
	classname: str
	display_name: str
	ingredients: dict[str, int]
	products: dict[str, int]
	manufacturing_duration: float
	produced_in: list[str]
	global_limit: int = -1
	variable_power_consumption_constant: float = 0.0
	variable_power_consumption_factor: float = 0.0
	raw_sink_points_gain: float = 0.0
	sinkable_points_gain: float = 0.0
	is_resource_proxy: bool = False

	def get_manufacturer(self, buildings: dict[str, "Building"],
	) -> Optional["Building"]:
		for b in self.produced_in:
			if b in buildings:
				ret = buildings[b]
				break
		else:
			ret = None
		return ret

	def calculate_sink_points(self, items: dict[str, Item]):
		self.raw_sink_points_gain = self.get_production_sink_points_gain(
			items, prod_multiplier=1.0, cycles_per_second=1.0, sinkable_only=False)
		self.sinkable_points_gain = self.get_production_sink_points_gain(
			items, prod_multiplier=1.0, cycles_per_second=1.0, sinkable_only=True)
		return

	def get_production_sink_points_gain(self, items: dict[str, Item],
		prod_multiplier: float, cycles_per_second: float, *,
		sinkable_only: bool = False,
	) -> float:
		points_per_cycle = 0.0
		# coef = prod_multiplier (products)
		# coef = -1 (ingredients)
		for category, coef in [(self.ingredients, -1), (self.products, prod_multiplier)]:
			for itemclass, amount in category.items():
				if itemclass not in items:
					continue
				item = items[itemclass]
				p = item.rescaled_sink_points(amount, sinkable_only=sinkable_only) * coef
				points_per_cycle += p

		return points_per_cycle * cycles_per_second


@dataclasses.dataclass
class Building(object):
	classname: str
	display_name: str
	# power basic
	variable_power_consumption: bool = False
	power_production: float = 0.0
	power_consumption: float = 0.0
	# overclock
	power_consumption_exponent: float = 1.321929
	# somersloop (production boost)
	production_shard_slot_size: int = 0
	production_shard_boost_multiplier: float = 0.0
	production_boost_power_consumption_exponent: float = 0.0
	# these are for resource extractors only
	extract_cycle_time: float = 0.0
	items_per_cycle: int = 0

	def get_base_power(self, recipe: Recipe = None) -> float:
		# report negative = consumption, positive = production
		if self.variable_power_consumption:
			if recipe is None:
				raise ValueError("recipe must be provided for variable power "
					"consumption buildings")
			ret = -recipe.variable_power_consumption_constant \
				- recipe.variable_power_consumption_factor / 2
		elif self.power_consumption > 0:
			ret = -self.power_consumption
		elif self.power_production > 0:
			ret = self.power_production
		else:
			ret = 0.0
		return ret

	def get_overclock_power_multiplier(self, clock_speed: ClockSpeed) -> float:
		if not isinstance(clock_speed, ClockSpeed):
			clock_speed = ClockSpeed(clock_speed)
		if self.power_consumption > 0:
			ret = (clock_speed / 100) ** self.power_consumption_exponent
		elif self.power_production > 0:
			# original value = 1.6 for generators, but we want linear to be in
			# line with game behavior
			ret = clock_speed / 100
		else:
			ret = 1.0
		return ret

	def get_production_multiplier(self, somersloop: int):
		if somersloop < 0 or somersloop > self.production_shard_slot_size:
			raise ValueError("somersloop must be between 0 and slot size "
				f"{self.production_shard_slot_size}, got {somersloop}")
		return somersloop * self.production_shard_boost_multiplier + 1.0

	def get_production_boost_power_multiplier(self, somersloop: int) -> float:
		if self.power_consumption == 0:
			# skip if is not a power-consumption building
			# logic may change in the future
			return 1.0
		multiplier = self.get_production_multiplier(somersloop)
		return multiplier ** self.production_boost_power_consumption_exponent

	def get_adjusted_power(self, clock_speed: ClockSpeed, somersloop: int,
		recipe: Recipe = None,
	) -> float:
		# deal with geothermal generator magic
		if self.classname == config.RESOURCE_NODE_GEYSER_GENERATOR:
			for purity_config in config.RESOURCE_NODE_PURITY_CONFIG.values():
				if recipe.classname.endswith(purity_config["label"]):
					ret = config.RESOURCE_NODE_GEYSER_POWER_NORMAL * \
						purity_config["multiplier"]
					break
			else:
				raise ValueError(f"{config.RESOURCE_NODE_GEYSER_GENERATOR} "
					f"cannot work with recipe {recipe.classname}")
		else:
			base_power = self.get_base_power(recipe)
			if base_power > 0:
				ret = base_power \
					* self.get_overclock_power_multiplier(clock_speed)
			elif base_power < 0:
				ret = base_power \
					* self.get_overclock_power_multiplier(clock_speed) \
					* self.get_production_boost_power_multiplier(somersloop)
			else:
				ret = base_power
		return ret
