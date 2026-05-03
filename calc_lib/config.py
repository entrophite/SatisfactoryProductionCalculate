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
# resource node counts data can be found at:
# get the data from: https://satisfactory.wiki.gg/wiki/Resource_Node
RESOURCE_NODE_PURITY_CONFIG = {
	"impure": {"label": "Impure", "multiplier": 0.5},
	"normal": {"label": "Normal", "multiplier": 1.0},
	"pure": {"label": "Pure", "multiplier": 2.0},
}

RESOURCE_NODE_CONFIG = {
	"Desc_OreIron_C": {"extractor": "Build_MinerMk3_C", "impure": 39, "normal": 42, "pure": 46, "base_rate": 120},
	"Desc_OreGold_C": {"extractor": "Build_MinerMk3_C", "impure": 0, "normal": 9, "pure": 8, "base_rate": 120},
	"Desc_OreCopper_C": {"extractor": "Build_MinerMk3_C", "impure": 13, "normal": 29, "pure": 13, "base_rate": 120},
	"Desc_Stone_C": {"extractor": "Build_MinerMk3_C", "impure": 15, "normal": 50, "pure": 29, "base_rate": 120},
	"Desc_Coal_C": {"extractor": "Build_MinerMk3_C", "impure": 15, "normal": 31, "pure": 16, "base_rate": 120},
	"Desc_RawQuartz_C": {"extractor": "Build_MinerMk3_C", "impure": 3, "normal": 7, "pure": 7, "base_rate": 120},
	"Desc_Sulfur_C": {"extractor": "Build_MinerMk3_C", "impure": 6, "normal": 5, "pure": 5, "base_rate": 120},
	"Desc_OreUranium_C": {"extractor": "Build_MinerMk3_C", "impure": 3, "normal": 2, "pure": 0, "base_rate": 120},
	"Desc_OreBauxite_C": {"extractor": "Build_MinerMk3_C", "impure": 5, "normal": 6, "pure": 6, "base_rate": 120},
	"Desc_SAM_C": {"extractor": "Build_MinerMk3_C", "impure": 10, "normal": 6, "pure": 3, "base_rate": 120},
	"Desc_LiquidOil_C": {"extractor": "Build_OilPump_C", "impure": 10, "normal": 12, "pure": 8, "base_rate": 120},
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
		"Islands": {"impure": 2, "normal": 3, "pure": 1},
		"RedBambooFields": {"impure": 0, "normal": 3, "pure": 3},
		"Swamp": {"impure": 6, "normal": 0, "pure": 0},
	},
	"Desc_NitrogenGas_C": {
		"DuneDesert": {"impure": 0, "normal": 2, "pure": 5},
		"AbyssCliff": {"impure": 2, "normal": 2, "pure": 4},
		"EasternDuneForest": {"impure": 0, "normal": 0, "pure": 10},
		"BlueCrater": {"impure": 0, "normal": 2, "pure": 4},
		"JungleSpires": {"impure": 0, "normal": 0, "pure": 7},
		"RockyDesert": {"impure": 0, "normal": 1, "pure": 6},
	},
	"Desc_Water_C": {
		"DuneDesertNorth": {"impure": 2, "normal": 1, "pure": 4},
		"DuneDesertSouth": {"impure": 0, "normal": 2, "pure": 4},
		"DesertCanyons": {"impure": 1, "normal": 2, "pure": 4},
		"TitanForest": {"impure": 0, "normal": 0, "pure": 6},
		"EasternDuneForest": {"impure": 2, "normal": 6, "pure": 0},
		"GrassField": {"impure": 2, "normal": 0, "pure": 5},
		"SnaketreeForest": {"impure": 0, "normal": 1, "pure": 6},
		"WesternDuneForest": {"impure": 0, "normal": 0, "pure": 7},
	},
}

RESOURCE_WELL_ACTIVATOR = "Build_FrackingSmasher_C"

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

################################################################################
# buildings that subject to ingredient multiplier
INGREDIENT_MULTIPLIER_EXCLUDE_RECIPES = {
	"Build_AlienPowerBuilding_C-Desc_AlienPowerFuel_C",
	"Build_AlienPowerBuilding_C-Unfueled",
	"Build_GeneratorBiomass_Automated_C-Desc_Biofuel_C",
	"Build_GeneratorBiomass_Automated_C-Desc_GenericBiomass_C",
	"Build_GeneratorBiomass_Automated_C-Desc_Leaves_C",
	"Build_GeneratorBiomass_Automated_C-Desc_Mycelia_C",
	"Build_GeneratorBiomass_Automated_C-Desc_PackagedBiofuel_C",
	"Build_GeneratorBiomass_Automated_C-Desc_Wood_C",
	"Build_GeneratorCoal_C-Desc_Coal_C",
	"Build_GeneratorCoal_C-Desc_CompactedCoal_C",
	"Build_GeneratorCoal_C-Desc_PetroleumCoke_C",
	"Build_GeneratorFuel_C-Desc_IonizedFuel_C",
	"Build_GeneratorFuel_C-Desc_LiquidBiofuel_C",
	"Build_GeneratorFuel_C-Desc_LiquidFuel_C",
	"Build_GeneratorFuel_C-Desc_LiquidTurboFuel_C",
	"Build_GeneratorFuel_C-Desc_RocketFuel_C",
	"Build_GeneratorNuclear_C-Desc_FicsoniumFuelRod_C",
	"Build_GeneratorNuclear_C-Desc_NuclearFuelRod_C",
	"Build_GeneratorNuclear_C-Desc_PlutoniumFuelRod_C",
	"Recipe_Alternate_DilutedPackagedFuel_C",
	"Recipe_PackagedAlumina_C",
	"Recipe_PackagedBiofuel_C",
	"Recipe_PackagedCrudeOil_C",
	"Recipe_PackagedIonizedFuel_C",
	"Recipe_PackagedNitricAcid_C",
	"Recipe_PackagedNitrogen_C",
	"Recipe_PackagedOilResidue_C",
	"Recipe_PackagedRocketFuel_C",
	"Recipe_PackagedSulfuricAcid_C",
	"Recipe_PackagedTurboFuel_C",
	"Recipe_PackagedWater_C",
	"Recipe_UnpackageAlumina_C",
	"Recipe_UnpackageBioFuel_C",
	"Recipe_UnpackageFuel_C",
	"Recipe_UnpackageIonizedFuel_C",
	"Recipe_UnpackageNitricAcid_C",
	"Recipe_UnpackageNitrogen_C",
	"Recipe_UnpackageOil_C",
	"Recipe_UnpackageOilResidue_C",
	"Recipe_UnpackageRocketFuel_C",
	"Recipe_UnpackageSulfuricAcid_C",
	"Recipe_UnpackageTurboFuel_C",
	"Recipe_UnpackageWater_C",
}
