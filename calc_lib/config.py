#!/usr/bin/env python3


################################################################################
# curator configs, related to game's docs.json specifically
# may need update after game updates
CURATOR_ITEM_AMOUNT_PAIR_REGEX = r"\(ItemClass=\"([^()]+)\",Amount=(\d+)\)"
CURATOR_ENCLOSED_ARRAY_REGEX = r"\(([^,]*,?)\)"

CURATOR_NATIVE_CLASSNAME_LIST_RECIPE = [
	"/Script/CoreUObject.Class'/Script/FactoryGame.FGRecipe'"
]

CURATOR_NATIVE_CLASSNAME_LIST_ITEM = [
	"/Script/CoreUObject.Class'/Script/FactoryGame.FGItemDescriptor'",
	"/Script/CoreUObject.Class'/Script/FactoryGame.FGResourceDescriptor'",
	"/Script/CoreUObject.Class'/Script/FactoryGame.FGItemDescriptorBiomass'",
	"/Script/CoreUObject.Class'/Script/FactoryGame.FGItemDescriptorNuclearFuel'",
	"/Script/CoreUObject.Class'/Script/FactoryGame.FGAmmoTypeInstantHit'",
	"/Script/CoreUObject.Class'/Script/FactoryGame.FGAmmoTypeProjectile'",
	"/Script/CoreUObject.Class'/Script/FactoryGame.FGEquipmentDescriptor'",
	"/Script/CoreUObject.Class'/Script/FactoryGame.FGPowerShardDescriptor'",
	"/Script/CoreUObject.Class'/Script/FactoryGame.FGAmmoTypeSpreadshot'",
	"/Script/CoreUObject.Class'/Script/FactoryGame.FGItemDescriptorPowerBoosterFuel'",
]

CURATOR_NATIVE_CLASSNAME_LIST_BUILDING = [
	"/Script/CoreUObject.Class'/Script/FactoryGame.FGBuildableGeneratorFuel'",
	"/Script/CoreUObject.Class'/Script/FactoryGame.FGBuildableResourceExtractor'",
	"/Script/CoreUObject.Class'/Script/FactoryGame.FGBuildableManufacturer'",
	"/Script/CoreUObject.Class'/Script/FactoryGame.FGBuildableGeneratorNuclear'",
	"/Script/CoreUObject.Class'/Script/FactoryGame.FGBuildableFrackingExtractor'",
	"/Script/CoreUObject.Class'/Script/FactoryGame.FGBuildableFrackingActivator'",
	"/Script/CoreUObject.Class'/Script/FactoryGame.FGBuildableGeneratorGeoThermal'",
	"/Script/CoreUObject.Class'/Script/FactoryGame.FGBuildableWaterPump'",
	"/Script/CoreUObject.Class'/Script/FactoryGame.FGBuildableManufacturerVariablePower'",
]

CURATOR_NATIVE_CLASSNAME_LIST_GENERATOR = [
	"/Script/CoreUObject.Class'/Script/FactoryGame.FGBuildableGeneratorFuel'",
	"/Script/CoreUObject.Class'/Script/FactoryGame.FGBuildableGeneratorNuclear'",
]

CURATOR_NATIVE_CLASSNAME_LIST_POWERBOOSTER = [
	"/Script/CoreUObject.Class'/Script/FactoryGame.FGBuildablePowerBooster'",
]

CURATOR_NATIVE_CLASSNAME_RESOURCE_SHORT = "FGResourceDescriptor"

################################################################################
# resource global limit can be found at:
# https://satisfactory.wiki.gg/wiki/Resource_Node
# https://satisfactory.wiki.gg/wiki/Resource_Well
# all values are in items/min
# these values can be calculated from the node/well count and building data,
# however it's a bit complicated so just put the numbers here
RESOURCE_GLOBAL_LIMIT = {
	"Desc_OreIron_C": 92100,
	"Desc_OreGold_C": 15000,
	"Desc_OreCopper_C": 36900,
	"Desc_Stone_C": 69300,
	"Desc_Coal_C": 42300,
	"Desc_RawQuartz_C": 13500,
	"Desc_Sulfur_C": 10800,
	"Desc_OreUranium_C": 2100,
	"Desc_OreBauxite_C": 12300,
	"Desc_SAM_C": 10200,
	"Desc_LiquidOil_C": 12600,
	"Desc_NitrogenGas_C": 12000,
	"Desc_Water_C": -1,  # infinite
}

################################################################################
# resource node counts data can be found at:
# get the data from: https://satisfactory.wiki.gg/wiki/Resource_Node
RESOURCE_NODE_PURITY_CONFIG = {
	"impure": {"label": "Impure", "multiplier": 0.5},
	"normal": {"label": "Normal", "multiplier": 1.0},
	"pure": {"label": "Pure", "multiplier": 2.0},
}

RESOURCE_NODE_CONFIG = {
	"Desc_OreIron_C": {"impure": 39, "normal": 42, "pure": 46},
	"Desc_OreGold_C": {"impure": 0, "normal": 9, "pure": 8},
	"Desc_OreCopper_C": {"impure": 13, "normal": 29, "pure": 13},
	"Desc_Stone_C": {"impure": 15, "normal": 50, "pure": 29},
	"Desc_Coal_C": {"impure": 15, "normal": 31, "pure": 16},
	"Desc_RawQuartz_C": {"impure": 3, "normal": 7, "pure": 7},
	"Desc_Sulfur_C": {"impure": 6, "normal": 5, "pure": 5},
	"Desc_OreUranium_C": {"impure": 3, "normal": 2, "pure": 0},
	"Desc_OreBauxite_C": {"impure": 5, "normal": 6, "pure": 6},
	"Desc_SAM_C": {"impure": 10, "normal": 6, "pure": 3},
	"Desc_LiquidOil_C": {"impure": 10, "normal": 12, "pure": 8},
}

RESOURCE_NODE_EXTRACTOR_LIST_SOLID = [
	# "Build_MinerMk1_C",  # disabled to avoid duplicate nodes
	# "Build_MinerMk2_C",  # disabled to avoid duplicate nodes
	"Build_MinerMk3_C",
]

RESOURCE_NODE_EXTRACTOR_LIST_CRUDE_OIL = [
	"Build_OilPump_C",
]

RESOURCE_NODE_EXTRACTOR_CONFIG = {
	"Desc_OreIron_C": RESOURCE_NODE_EXTRACTOR_LIST_SOLID,
	"Desc_OreGold_C": RESOURCE_NODE_EXTRACTOR_LIST_SOLID,
	"Desc_OreCopper_C": RESOURCE_NODE_EXTRACTOR_LIST_SOLID,
	"Desc_Stone_C": RESOURCE_NODE_EXTRACTOR_LIST_SOLID,
	"Desc_Coal_C": RESOURCE_NODE_EXTRACTOR_LIST_SOLID,
	"Desc_RawQuartz_C": RESOURCE_NODE_EXTRACTOR_LIST_SOLID,
	"Desc_Sulfur_C": RESOURCE_NODE_EXTRACTOR_LIST_SOLID,
	"Desc_OreUranium_C": RESOURCE_NODE_EXTRACTOR_LIST_SOLID,
	"Desc_OreBauxite_C": RESOURCE_NODE_EXTRACTOR_LIST_SOLID,
	"Desc_SAM_C": RESOURCE_NODE_EXTRACTOR_LIST_SOLID,
	"Desc_LiquidOil_C": RESOURCE_NODE_EXTRACTOR_LIST_CRUDE_OIL,
}

RESOURCE_NODE_GEYSER_CONFIG = {
	"impure": 9,
	"normal": 13,
	"pure": 9,
}

RESOURCE_NODE_GEYSER_GENERATOR = "Build_GeneratorGeoThermal_C"

# this value is empirical; get it from the game once it changes
RESOURCE_NODE_GEYSER_POWER_NORMAL = 200  # MW

################################################################################
# resource well data can be found at:
# get the data from: https://satisfactory-calculator.com/en/interactive-map
# a.k.a. you have to count them manually from the map!
# data:
# (key) itemclass: extracted resources
# (key) location [str]: a label to uniquely identify the well cluster
# (value) rate [float]: overall extraction rate of the well cluster
RESOURCE_WELL_CONFIG = {
	"Desc_LiquidOil_C": {
		"Islands": 6000,
		"RedBambooFields": 9000,
		"Swamp": 3000,
	},
	"Desc_NitrogenGas_C": {
		"DuneDesert": 12000,
		"AbyssCliff": 11000,
		"TitanForest": 20000,
		"BlueCrater": 10000,
		"JungleSpires": 14000,
		"RockyDesert": 13000,
	},
	"Desc_Water_C": {
		"DuneDesertNorth": 10000,
		"DuneDesertSouth": 10000,
		"DesertCanyons": 10500,
		"TitanForest": 12000,
		"EasternDuneForest": 7000,
		"Grassfield": 11000,
		"SnaketreeForest": 13000,
		"WestDuneForest": 14000,
	},
}

RESOURCE_WELL_ACTIVATOR_LIST = [
	"Build_FrackingSmasher_C",
]

################################################################################
#
UNRESTRAINED_RESOURCE_CONFIG = {
	"Desc_Water_C": ["Build_WaterPump_C"],
}

################################################################################
# used in calculators to determine the resource weights
# summed production rates are @game version 1.0/1.1
# these values can be tuned - for updates
DEFAULT_RESOURCE_WEIGHT_CONFIG = {
	# rich, cheap resources
	"Desc_OreIron_C": 1.0,  # 92100/min (iron)
	"Desc_Stone_C": 1.0,  # 69300/min (limestone)
	# medium-rich resources
	"Desc_Coal_C": 2.0,  # 42300/min (coal)
	"Desc_OreCopper_C": 2.0,  # 36900/min (copper)
	"Desc_LiquidOil_C": 4.0,  # 12600/min (crude oil)
	# rare resources, versatile use
	"Desc_OreGold_C": 5.0,  # 15000/min (caterium)
	"Desc_RawQuartz_C": 7.0,  # 13500/min (raw quartz)
	"Desc_OreBauxite_C": 7.0,  # 12300/min (bauxite)
	"Desc_NitrogenGas_C": 7.0,  # 12000/min (nitrogen gas)
	# rare resources, limited use
	"Desc_Sulfur_C": 5.0,  # 10800/min (sulfur)
	"Desc_OreUranium_C": 8.0,  # 2100/min (uranium)
	"Desc_SAM_C": 8.0,  # 10200/min (SAM)
	# trivial resources
	"Desc_Water_C": 0.0,  # infinite/min (water)
}

# total amount of somersloop in the game, can get from:
# https://satisfactory.wiki.gg/wiki/Somersloop
SOMERSLOOP_GLOBAL_LIMIT = 106

POWER_BOOST_BUILDING_LIST = [
	"Build_AlienPowerBuilding_C",
]

################################################################################
# resource converter recipes
RESOURCE_CONVERTER_RECIPE_LIST = [
	"Recipe_Bauxite_Caterium_C",
	"Recipe_Bauxite_Copper_C",
	"Recipe_Caterium_Copper_C",
	"Recipe_Caterium_Quartz_C",
	"Recipe_Coal_Iron_C",
	"Recipe_Coal_Limestone_C",
	"Recipe_Copper_Quartz_C",
	"Recipe_Copper_Sulfur_C",
	"Recipe_Iron_Limestone_C",
	"Recipe_Limestone_Sulfur_C",
	"Recipe_Nitrogen_Bauxite_C",
	"Recipe_Nitrogen_Caterium_C",
	"Recipe_Quartz_Bauxite_C",
	"Recipe_Quartz_Coal_C",
	"Recipe_Sulfur_Coal_C",
	"Recipe_Sulfur_Iron_C",
	"Recipe_Uranium_Bauxite_C",
]
