# ===============================================
# VEKTOR FÁJLOK
# ===============================================

# Dűlők fáljának elérési útja, rétegének neve és a neveket tartalmazó mező
VINEYARDS_FILE_PATH = r"data/raw/vector/test_vector_data.gpkg"
VINEYARDS_LAYER_NAME = "vineyards"
VINEYARDS_NAME_FIELD = "name"

# Települések fájljának elérési útja, rétegének neve és a neveket tartalmazó mező
SETTLEMENTS_FILE_PATH = r"data/raw/vector/test_vector_data.gpkg"
SETTLEMENTS_LAYER_NAME = "settlements"
SETTLEMENTS_NAME_FIELD = "name"

# Borvidékek fájljának elérési útja, rétegének neve és a neveket tartalmazó mező
WINE_DISTRICTS_FILE_PATH = r"data/raw/vector/test_vector_data.gpkg"
WINE_DISTRICTS_LAYER_NAME = "wine_districts"
WINE_DISTRICTS_NAME_FIELD = "name"

# Borrégiók fájljának elérési útja, rétegének neve és a neveket tartalmazó mező
WINE_REGIONS_FILE_PATH = r"data/raw/vector/test_vector_data.gpkg"
WINE_REGIONS_LAYER_NAME = "wine_regions"
WINE_REGIONS_NAME_FIELD = "name"

# Talajok fájljának elérési útja és rétegének neve
SOILS_FILE_PATH = r"data/raw/vector/test_vector_data.gpkg"
SOILS_LAYER_NAME = "soils"
SOILS_PROPERTY_FIELDS = ["soil_type", "soil_bedrock"]



# ===============================================
# RASZTER FÁJLOK
# ===============================================

# DEM fájl elérési útja
DEM_FILE_DIRECTORY_PATH = r"data/raw/raster/test_dem"

# Meteorológiai adatok mappájának elérési útja
METEOROLOGICAL_RASTER_DATA_DIRECTORY_PATH = r"data/raw/raster/test_meteo"



# ===============================================
# EREDMÉNY FÁJLOK MAPPÁI
# ===============================================

# Eredmény vektor fájlok mappája (nem baj, ha még nem létezik)
RESULT_VECTOR_FILES_DIRECTORY_PATH = r"data\processed\vector_example"

# Eredmény DEM-alapú fájlok mappája (nem baj, ha még nem létezik)
RESULT_DEM_FILES_DIRECTORY_PATH = r"data\processed\raster_example\example_dem"

# Eredmény meteorológiai fájlok mappája (nem baj, ha még nem létezik)
RESULT_METEOROLOGICAL_FILES_DIRECTORY_PATH = r"data\processed\raster_example\example_meteo"



# ===============================================
# A RASZTER ÚJRAOSZTÁLYOZÁS SZABÁLYAI
# ===============================================

# Az újraosztályozás a következőképpen működik: [minimum - maximum)
# Tehát balról zárt, jobbról nyitott intervallumok


# Magasság értékek újraosztályozása
ELEVATION_RECLASSIFICATION_RULES = {
        1: "0 - 100",
        2: "100 - 125",
        3: "125 - 150",
        4: "150 - 175",
        5: "175 - 200",
        6: "200 - 225",
        7: "225 - 250",
        8: "250 - 275",
        9: "275 - 300",
        10: "300 - 325",
        11: "325 - 350",
        12: "350 - 375",
        13: "375 - 400",
        14: "400 - 425",
        15: "425 - 450",
        16: "450 - 475",
        17: "475 - 500",
        18: "500 - 525",
        19: "525 - 550",
        20: "550 - 1014"
    }

# Lejtőszög értékek újraosztályozása
SLOPE_RECLASSIFICATION_RULES = {
        1: "0 - 2", # Sík vagy közel sík
        2: "2 - 5", # Enyhe lejtés
        3: "5 - 12", # Mérsékelt lejtés
        4: "12 - 25", # Meredek
        5: "25 - 90.1" # Nagyon meredek
    }

# Flow Accumulation értékek újraosztályozása
FLOW_ACCUMULATION_RECLASSIFICATION_RULES = {
        1: "0 - 10", # Nincs hozzáfolyás, minimális a vízerózió
        2: "10 - 100", # Leporlasztott lepedékes lefolyás (sheet wash)
        3: "100 - 1000", # Koncentrálódó lefolyás, meginduló mederképződés
        4: "1000 - 10000", # Állandó mederrel rendelkező  völgytalpak
        5: "10000 - 9999999999" # Jelentős vízszállítás és hordalékgyűjtés
    }

# Topográfiai Nedvesség Index (TWI) értékek újraosztályozása
TOPOGRAPHIC_WETNESS_INDEX_RECLASSIFICATION_RULES = {
        1: "0 - 6", # Nagyon száraz
        2: "6 - 9", # Mérsékelten száraz
        3: "9 - 12", # Mérsékelten nedves
        4: "12 - 15", # Nedves
        5: "15 - 100" # Nagyon nedves
    }

# Sediment Transport Index (STI) értékek újraosztályozása
SEDIMENT_TRANSPORT_INDEX_RECLASSIFICATION_RULES = {
        1: "0 - 5", # Alacsony erózió
        2: "5 - 15", # Közepes erózió
        3: "15 - 10000" # Magas erózió
    }

# Profil görvület értékek újraosztályozása
PROFIL_CURVATURE_RECLASSIFICATION_RULES = {
        1: "-10000 - -0.002", # Konvex (csökkenő vízsebesség)
        2: "-0.002 - 0.002", # Lineáris (konstans vízsebesség)
        3: "0.002 - 10000" # Konkáv (gyorsuló vízsebesség)
    }

# Plan görvület értékek újraosztályozása
PLAN_CURVATURE_RECLASSIFICATION_RULES = {
        30: '-10000 - -0.002', # Konkáv (konvergáló (összefutó) víz)
        20: "-0.002 - 0.002", # Lineáris
        10: "0.002 - 10000" # Konvex (divergens (szétágazó) víz)
    }

# Time in daylight értékek újraosztályozása
TIME_IN_DAYLIGHT_RECLASSIFICATION_RULES = {
        1: "0.0 - 0.4",
        2: "0.4 - 0.5",
        3: "0.5 - 0.6",
        4: "0.6 - 0.7",
        5: "0.7 - 0.8",
        6: "0.8 - 1.0"
    }

# Potenciális napsugárzás értékek újraosztályozása
POTENTIAL_SOLAR_RADIATION_RECLASSIFICATION_RULES = {
        1: "0.0 - 3.0",
        2: "3.0 - 3.4",
        3: "3.4 - 3.8",
        4: "3.8 - 4.2",
        5: "4.2 - 4.6",
        6: "4.6 - 5.0",
        7: "5.0 - 5.4",
        8: "5.4 - 5.8",
        9: "5.8 - 6.2",
        10: "6.2 - 10.0"
    }

# Érdesség értékek újraosztályozása
ROUGHNESS_RECLASSIFICATION_RULES = {
        1: "0.0 - 2.0", # Korlátozott (fagyveszélyes síkság)
        2: "2.0 - 9.0", # Optimális
        3: "9.0 - 18.0", # Feltételesen alkalmas (erózió)
        4: "18.0 - 25.0", # Alkalmatlan
    }



# ===============================================
# EREDMÉNY MEZŐK NEVÉNEK KEZELÉSE
# ===============================================

# Kulcs: Régi (vagy eredeti) név
# Érték: Az új név (üres str, ha jó a régi név)
# Fontos a mezők sorrendjének szempontjából is
FIELD_NAMES = {
        "id": "",
        "name": "",
        "settlement": "",
        "wine_district": "",
        "wine_region": "",
        "number_of_vineyards": "",
        "area_m2": "",
        "area_ha": "",

        "soil_bedrock_1": "soil_bedrock_limestone_area_rate",
        "soil_bedrock_2": "soil_bedrock_sandstone_area_rate",

        "soil_type_1": "soil_type_cambisols_soils_area_rate",
        "soil_type_2": "soil_type_luvisol_soils_area_rate",
        "soil_type_3": "soil_type_pseudogley_brown_forest_soils_area_rate",


        "elevation_minimum": "",
        "elevation_maximum": "",
        "elevation_mean": "",
        "elevation_median": "",
        "elevation_standard_deviation": "",

        "slope_minimum": "",
        "slope_maximum": "",
        "slope_mean": "",
        "slope_median": "",
        "slope_standard_deviation": "",

        "flow_accumulation_minimum": "",
        "flow_accumulation_maximum": "",
        "flow_accumulation_mean": "",
        "flow_accumulation_median": "",
        "flow_accumulation_standard_deviation": "",

        "topographic_wetness_index_minimum": "",
        "topographic_wetness_index_maximum": "",
        "topographic_wetness_index_mean": "",
        "topographic_wetness_index_median": "",
        "topographic_wetness_index_standard_deviation": "",

        "sediment_transport_index_minimum": "",
        "sediment_transport_index_maximum": "",
        "sediment_transport_index_mean": "",
        "sediment_transport_index_median": "",
        "sediment_transport_index_standard_deviation": "",

        "profile_curvature_minimum": "",
        "profile_curvature_maximum": "",
        "profile_curvature_mean": "",
        "profile_curvature_median": "",
        "profile_curvature_standard_deviation": "",

        "plan_curvature_minimum": "",
        "plan_curvature_maximum": "",
        "plan_curvature_mean": "",
        "plan_curvature_median": "",
        "plan_curvature_standard_deviation": "",

        "time_in_daylight_minimum": "",
        "time_in_daylight_maximum": "",
        "time_in_daylight_mean": "",
        "time_in_daylight_median": "",
        "time_in_daylight_standard_deviation": "",

        "potential_solar_radiation_minimum": "",
        "potential_solar_radiation_maximum": "",
        "potential_solar_radiation_mean": "",
        "potential_solar_radiation_median": "",
        "potential_solar_radiation_standard_deviation": "",

        "topographic_position_index_minimum": "",
        "topographic_position_index_maximum": "",
        "topographic_position_index_mean": "",
        "topographic_position_index_median": "",
        "topographic_position_index_standard_deviation": "",

        "roughness_minimum": "",
        "roughness_maximum": "",
        "roughness_mean": "",
        "roughness_median": "",
        "roughness_standard_deviation": "",

        "elevation_reclassified_1": "elevation_less_than_100_area_rate",
        "elevation_reclassified_2": "elevation_between_100_and_125_area_rate",
        "elevation_reclassified_3": "elevation_between_125_and_150_area_rate",
        "elevation_reclassified_4": "elevation_between_150_and_175_area_rate",
        "elevation_reclassified_5": "elevation_between_175_and_200_area_rate",
        "elevation_reclassified_6": "elevation_between_200_and_225_area_rate",
        "elevation_reclassified_7": "elevation_between_225_and_250_area_rate",
        "elevation_reclassified_8": "elevation_between_250_and_275_area_rate",
        "elevation_reclassified_9": "elevation_between_275_and_300_area_rate",
        "elevation_reclassified_10": "elevation_between_300_and_325_area_rate",
        "elevation_reclassified_11": "elevation_between_325_and_350_area_rate",
        "elevation_reclassified_12": "elevation_between_350_and_375_area_rate",
        "elevation_reclassified_13": "elevation_between_375_and_400_area_rate",
        "elevation_reclassified_14": "elevation_between_400_and_425_area_rate",
        "elevation_reclassified_15": "elevation_between_425_and_450_area_rate",
        "elevation_reclassified_16": "elevation_between_450_and_475_area_rate",
        "elevation_reclassified_17": "elevation_between_475_and_500_area_rate",
        "elevation_reclassified_18": "elevation_between_500_and_525_area_rate",
        "elevation_reclassified_19": "elevation_between_525_and_550_area_rate",
        "elevation_reclassified_20": "elevation_more_than_550_area_rate",

        "slope_reclassified_1": "slope_less_than_2_area_rate",
        "slope_reclassified_2": "slope_between_2_and_5_area_rate",
        "slope_reclassified_3": "slope_between_5_and_12_area_rate",
        "slope_reclassified_4": "slope_between_12_and_25_area_rate",
        "slope_reclassified_5": "slope_more_than_25_area_rate",

        "aspect_reclassified_0": "aspect_no_aspect_area_rate",
        "aspect_reclassified_1": "aspect_north_area_rate",
        "aspect_reclassified_2": "aspect_northeast_area_rate",
        "aspect_reclassified_3": "aspect_east_area_rate",
        "aspect_reclassified_4": "aspect_southeast_area_rate",
        "aspect_reclassified_5": "aspect_south_area_rate",
        "aspect_reclassified_6": "aspect_southwest_area_rate",
        "aspect_reclassified_7": "aspect_west_area_rate",
        "aspect_reclassified_8": "aspect_northwest_area_rate",

        "flow_direction_reclassified_0":
            "flow_direction_no_direction_area_rate",
        "flow_direction_reclassified_1": "flow_direction_north_area_rate",
        "flow_direction_reclassified_2": "flow_direction_northeast_area_rate",
        "flow_direction_reclassified_3": "flow_direction_east_area_rate",
        "flow_direction_reclassified_4": "flow_direction_southeast_area_rate",
        "flow_direction_reclassified_5": "flow_direction_south_area_rate",
        "flow_direction_reclassified_6": "flow_direction_southwest_area_rate",
        "flow_direction_reclassified_7": "flow_direction_west_area_rate",
        "flow_direction_reclassified_8": "flow_direction_northwest_area_rate",

        "flow_accumulation_reclassified_1":
            "flow_accumulation_less_than_10_area_rate",
        "flow_accumulation_reclassified_2":
            "flow_accumulation_between_10_and_100_area_rate",
        "flow_accumulation_reclassified_3":
            "flow_accumulation_between_100_and_1000_area_rate",
        "flow_accumulation_reclassified_4":
            "flow_accumulation_between_1000_and_10000_area_rate",
        "flow_accumulation_reclassified_5":
            "flow_accumulation_more_than_10000_area_rate",

        "topographic_wetness_index_reclassified_1":
            "topographic_wetness_index_less_than_6_area_rate",
        "topographic_wetness_index_reclassified_2":
            "topographic_wetness_index_between_6_and_9_area_rate",
        "topographic_wetness_index_reclassified_3":
            "topographic_wetness_index_between_9_and_12_area_rate",
        "topographic_wetness_index_reclassified_4":
            "topographic_wetness_index_between_12_and_15_area_rate",
        "topographic_wetness_index_reclassified_5":
            "topographic_wetness_index_more_than_15_area_rate",

        "sediment_transport_index_reclassified_1":
            "sediment_transport_index_less_than_5_area_rate",
        "sediment_transport_index_reclassified_2":
            "sediment_transport_index_between_5_and_15_area_rate",
        "sediment_transport_index_reclassified_3":
            "sediment_transport_index_more_than_15_area_rate",

        "profile_curvature_reclassified_1":
            "profile_curvature_convex_area_rate",
        "profile_curvature_reclassified_2":
            "profile_curvature_linear_area_rate",
        "profile_curvature_reclassified_3":
            "profile_curvature_concave_area_rate",

        "plan_curvature_reclassified_10": "plan_curvature_convex_area_rate",
        "plan_curvature_reclassified_20": "plan_curvature_linear_area_rate",
        "plan_curvature_reclassified_30": "plan_curvature_concave_area_rate",

        "landform_class_11": "landform_class_convex_and_convex_area_rate",
        "landform_class_12": "landform_class_convex_and_linear_area_rate",
        "landform_class_13": "landform_class_convex_and_concave_area_rate",
        "landform_class_21": "landform_class_linear_and_convex_area_rate",
        "landform_class_22": "landform_class_linear_and_linear_area_rate",
        "landform_class_23": "landform_class_linear_and_concave_area_rate",
        "landform_class_31": "landform_class_concave_and_convex_area_rate",
        "landform_class_32": "landform_class_concave_and_linear_area_rate",
        "landform_class_33": "landform_class_concave_and_concave_area_rate",

        "time_in_daylight_reclassified_1":
            "time_in_daylight_less_than_40_area_rate",
        "time_in_daylight_reclassified_2":
            "time_in_daylight_between_40_and_50_area_rate",
        "time_in_daylight_reclassified_3":
            "time_in_daylight_between_50_and_60_area_rate",
        "time_in_daylight_reclassified_4":
            "time_in_daylight_between_60_and_70_area_rate",
        "time_in_daylight_reclassified_5":
            "time_in_daylight_between_70_and_80_area_rate",
        "time_in_daylight_reclassified_6":
            "time_in_daylight_more_than_80_area_rate",

        "potential_solar_radiation_reclassified_1":
            "potential_solar_radiation_less_than_1800_area_rate",
        "potential_solar_radiation_reclassified_2":
            "potential_solar_radiation_between_1800_and_2300_area_rate",
        "potential_solar_radiation_reclassified_3":
            "potential_solar_radiation_between_2300_and_2800_area_rate",
        "potential_solar_radiation_reclassified_4":
            "potential_solar_radiation_between_2800_and_3300_area_rate",
        "potential_solar_radiation_reclassified_5":
            "potential_solar_radiation_between_3300_and_3700_area_rate",
        "potential_solar_radiation_reclassified_6":
            "potential_solar_radiation_between_3700_and_4100_area_rate",
        "potential_solar_radiation_reclassified_7":
            "potential_solar_radiation_between_4100_and_4500_area_rate",
        "potential_solar_radiation_reclassified_8":
            "potential_solar_radiation_more_than_4500_area_rate",

        "topographic_position_index_reclassified_1":
            "topographic_position_index_less_than__07_area_rate",
        "topographic_position_index_reclassified_2":
            "topographic_position_index_between__07_and__03_area_rate",
        "topographic_position_index_reclassified_3":
            "topographic_position_index_between__03_and_03_area_rate",
        "topographic_position_index_reclassified_4":
            "topographic_position_index_between_03_and_07_area_rate",
        "topographic_position_index_reclassified_5":
            "topographic_position_index_more_than_07_area_rate",

        "roughness_reclassified_1": "roughness_less_than_4_area_rate",
        "roughness_reclassified_2": "roughness_between_4_and_11_area_rate",
        "roughness_reclassified_3": "roughness_more_than_11_area_rate",

        "average_temperature_summer": "",

        "precipitation_year": "",

        "geometry": ""
    }