import pytest

import sys
import pathlib

import geopandas as gpd
import rasterio
import pyproj

import config
import config_test

from src import load_data
from src import prepare_vector_data
from src import calculate_raster_data
from src import join_rasters_to_polygons
from src import make_result_data


@pytest.fixture(autouse=True)
def fix_sys_argv(monkeypatch) -> None:
    """ Parancssor szimulálása, mintha onnan indították volna a
    tesztet. """

    test_dir = pathlib.Path(__file__).resolve().parent

    monkeypatch.chdir(test_dir)

    monkeypatch.setattr(sys, "argv", [str(test_dir)])


@pytest.fixture(autouse=True)
def config_setting_for_test(monkeypatch) -> None:
    """ A konfiguráció beállításait elvégzi a teszthez."""

    for key in dir(config_test):

        if not key.isupper():
            continue

        monkeypatch.setattr(f"config.{key}", getattr(config_test, key))


def test_load_data():
    """ Teszteli az adatbetöltés folyamatát.

    A teszt 3 részre van bontva:
        1. Betöltött vektoros adatok tesztje.
        2. Betöltött DEM adatok tesztje.
        3. Betöltött meteorológiai adatok tesztje.

    Returns:
        1. GeoDataFrame-ek dict-je.
        2. Raszterek elérési útjának dict-je.
    """

    gdfs, rasters = load_data.process(test_run=True)

    # =================================
    # BETÖLTÖTT VEKTOROS ADATOK TESZTJE
    # =================================

    test_gdfs_result = 0
    for layer in gdfs.keys():

        # A CRS EOV-e
        if gdfs[layer].crs == "EPSG:23700":
            test_gdfs_result += 1

        # Dűlők mezőnevei megfelelnek-e
        if layer == "vineyards":
            columns = gdfs[layer].columns.to_list()
            if columns == ["name", "geometry"]:
                test_gdfs_result += 1

        # Települések mezőnevei megfelelnek-e
        elif layer == "settlements":
            columns = gdfs[layer].columns.to_list()
            if columns == ["settlement", "geometry"]:
                test_gdfs_result += 1

        # Borvidékek mezőnevei megfelelnek-e
        elif layer == "wine_districts":
            columns = gdfs[layer].columns.to_list()
            if columns == ["wine_district", "geometry"]:
                test_gdfs_result += 1

        # Borrégiók mezőnevei megfelelnek-e
        elif layer == "wine_regions":
            columns = gdfs[layer].columns.to_list()
            if columns == ["wine_region", "geometry"]:
                test_gdfs_result += 1

        # Talajok mezőnevei megfelelnek-e
        elif layer == "soils":
            columns = gdfs[layer].columns.to_list()
            soil_fields = config.SOILS_PROPERTY_FIELDS.copy()
            soil_fields.append("geometry")
            if columns == soil_fields:
                test_gdfs_result += 1

    assert test_gdfs_result == 10



    # =================================
    # BETÖLTÖTT DEM ADATOK TESZTJE
    # =================================

    test_dem_result = 0

    for raster_name in rasters['dem'].keys():

        # DEM raster EOV-ban van-e
        with rasterio.open(rasters['dem'][raster_name]) as src:
            if src.crs == pyproj.CRS("EPSG:23700"):
                test_dem_result += 1

    assert test_dem_result == 1



    # =================================
    # BETÖLTÖTT METEOROLÓGIAI ADATOK TESZTJE
    # =================================

    test_meteo_result = 0

    for raster_name in rasters['meteorological'].keys():

        # Meteorológiai adatok EOV-ban vannak-e
        with rasterio.open(rasters['meteorological'][raster_name]) as src:
            if src.crs == pyproj.CRS("EPSG:23700"):
                test_meteo_result += 1

    assert test_meteo_result == len(rasters['meteorological'].keys())


def test_prepare_vector_data() -> dict[str, gpd.GeoDataFrame]:
    """ Teszteli a vektoros adatok előkészítésének folyamatát.

    Returns:
        A GeoDataFrame-eket tartalmazó dict az adatokelőkészítése után.
    """

    gdfs = load_data.process(test_run=True)[0]

    prepare_vector_data.process(
        gdfs,
        test_run=True
    )

    test_result = 0
    vineyards = gdfs["vineyards"]

    # Megvannak-e a szükséges mezőnevek
    for field_name in ["settlement", "wine_district", "wine_region"]:
        if field_name in vineyards.columns:
            test_result += 1

    # Talaj tulajdonságok vizsgálata
    for soil_property in config.SOILS_PROPERTY_FIELDS:

        soil_property_cols = [
            col
            for col in vineyards.columns
            if col.startswith(soil_property)
        ]

        # Talaj adat mezőit tartalmazó DataFrame
        soil_values = vineyards[soil_property_cols]

        # Soronként megfelelnek-e az eredmények
        inner_result = 0
        for _, row in soil_values.iterrows():
            if 0.995 <= row.sum() <= 1.005:
                inner_result += 1

        if inner_result == len(vineyards):
            test_result += 1

    assert test_result == 3 + len(config.SOILS_PROPERTY_FIELDS)


def test_calculate_raster_data() -> dict[str, dict[str, pathlib.Path]]:
    """ Teszteli a rasteres adatok kiszámításának folyamatát.

    A teszt 2 részre van bontva:
        1. A kiszámított domborzati paraméterek létezésének vizsgálata.
        2. Az újraosztályozott DEM-alapú rasterek létezésének
            vizsgálata, valamint azon rasterek értékeinek vizsgálata.

    Returns:
        A raster elérési útját tartalmazó dict a kiszámított rasterek
            után.
    """

    rasters = load_data.process(test_run=True)[1]

    calculate_raster_data.process(
        rasters,
        test_run=True
    )

    dem_prefix = list(rasters["dem"].keys())[0][:-10]


    # =================================
    # KISZÁMÍTOTT DOMBORZATI PARAMÉTEREK TESZTJE
    # =================================

    test_calculated_result = 0
    calculated_raster_names = [
        name
        for name in rasters['dem'].keys()
        if "class" not in name
    ]

    searched_raster_names = [
        f"{dem_prefix}_breach_depression",
        f"{dem_prefix}_slope",
        f"{dem_prefix}_aspect",
        f"{dem_prefix}_flow_direction",
        f"{dem_prefix}_flow_accumulation",
        f"{dem_prefix}_topographic_wetness_index",
        f"{dem_prefix}_sediment_transport_index",
        f"{dem_prefix}_profile_curvature",
        f"{dem_prefix}_plan_curvature",
        f"{dem_prefix}_time_in_daylight",
        f"{dem_prefix}_potential_solar_radiation",
        f"{dem_prefix}_topographic_position_index",
        f"{dem_prefix}_roughness",
    ]

    for searched_name in searched_raster_names:
        if searched_name in calculated_raster_names:
            test_calculated_result += 1

    assert test_calculated_result == len(searched_raster_names)



    # =================================
    # ÚJRAOSZTÁLYOZOTT RASZTEREK TESZTJE
    # =================================

    test_reclassified_result = 0

    searched_raster_names = [
        f"{dem_prefix}_elevation_reclassified",
        f"{dem_prefix}_slope_reclassified",
        f"{dem_prefix}_aspect_reclassified",
        f"{dem_prefix}_flow_direction_reclassified",
        f"{dem_prefix}_flow_accumulation_reclassified",
        f"{dem_prefix}_topographic_wetness_index_reclassified",
        f"{dem_prefix}_sediment_transport_index_reclassified",
        f"{dem_prefix}_profile_curvature_reclassified",
        f"{dem_prefix}_plan_curvature_reclassified",
        f"{dem_prefix}_landform_class",
        f"{dem_prefix}_time_in_daylight_reclassified",
        f"{dem_prefix}_potential_solar_radiation_reclassified",
        f"{dem_prefix}_topographic_position_index_reclassified",
        f"{dem_prefix}_roughness_reclassified",
    ]

    for searched_name in searched_raster_names:
        with rasterio.open(rasters['dem'][searched_name]) as src:
            sum_values = src.read(1).sum()

            if sum_values % 1 == 0:
                test_reclassified_result += 1


    assert test_reclassified_result == len(searched_raster_names)


def test_join_rasters_to_polygons() -> dict[str, gpd.GeoDataFrame]:
    """ Teszteli a rasteres adatok vektoros adatokhoz történő
        kapcsolásának folyamatát.

    A teszt 3 részből áll:
        1. A zóna statisztikával történő összekapcsolás eredmény
            mezőinek vizsgálata.
        2. Az újraosztályozott rasterek területi arányát tartalmazó
            mezőinek vizsgálata.
        3. A meteorológiai adatokkal történő összekapcsolás során
            létrejött mezők vizsgálata.

    Returns:
         GeoDataFrame-eket tartalmazó dict az összekapcsolások után.
    """

    gdfs, rasters = load_data.process(test_run=True)

    prepare_vector_data.process(
        gdfs,
        test_run=True
    )

    calculate_raster_data.process(
        rasters,
        test_run=True
    )

    join_rasters_to_polygons.process(
        gdfs,
        rasters,
        test_run=True
    )

    vineyards = gdfs["vineyards"]



    # =================================
    # ZÓNA STATISZTIKA TESZTJE
    # =================================

    test_zonal_stats_result = 0

    searched_raster_names = [
        "elevation",
        "slope",
        "flow_accumulation",
        "topographic_wetness_index",
        "sediment_transport_index",
        "profile_curvature",
        "plan_curvature",
        "time_in_daylight",
        "potential_solar_radiation",
        "topographic_position_index",
        "roughness"
    ]

    stats = ["minimum", "maximum", "mean", "median", "standard_deviation"]

    for searched_name in searched_raster_names:
        for stat in stats:
            if f"{searched_name}_{stat}" in vineyards.columns:
                test_zonal_stats_result += 1

    assert test_zonal_stats_result == len(searched_raster_names) * len(stats)



    # =================================
    # ÚJRAOSZTÁLYOZOTT TERÜLETI ARÁNYOK TESZTJE
    # =================================

    test_class_area_rate_result = 0

    searched_raster_names = [
        "elevation",
        "slope",
        "aspect",
        "flow_direction",
        "flow_accumulation",
        "topographic_wetness_index",
        "sediment_transport_index",
        "profile_curvature",
        "plan_curvature",
        "landform_class",
        "time_in_daylight",
        "potential_solar_radiation",
        "topographic_position_index",
        "roughness"
    ]

    for searched_name in searched_raster_names:

        area_rate_cols = [
            col
            for col in vineyards.columns
            if col.startswith(searched_name) and col[-1].isdigit()
        ]

        area_rate_values = vineyards[area_rate_cols]

        # Soronként megfelelnek-e az eredmények
        inner_result = 0
        for _, row in area_rate_values.iterrows():
            if 0.995 <= row.sum() <= 1.005:
                inner_result += 1

        if inner_result == len(vineyards):
            test_class_area_rate_result += 1

    assert test_class_area_rate_result == len(searched_raster_names)



    # =================================
    # METEOROLÓGIAI ADATOK KAPCSOLÁSÁNAK TESZTJE
    # =================================

    test_meteo_join_result = 0
    searched_raster_names = list(rasters['meteorological'].keys())

    for searched_name in searched_raster_names:
        if searched_name in vineyards.columns:
            test_meteo_join_result += 1

    assert test_meteo_join_result == len(searched_raster_names)




def test_make_result_data():
    """ Teszteli az eredmény adatok készítésének folyamata.

    A teszt 2 részből áll:
        1. A szükséges eredmény rétegek létezésének vizsgálata.
        2. A GeoDataFrame-ek mezők nevének megfelelelő átnevezésének
            tesztje.
    """

    import pyogrio.errors


    gdfs, rasters = load_data.process(test_run=True)

    prepare_vector_data.process(
        gdfs,
        test_run=True
    )

    calculate_raster_data.process(
        rasters,
        test_run=True
    )

    join_rasters_to_polygons.process(
        gdfs,
        rasters,
        test_run=True
    )

    make_result_data.process(
        gdfs,
        rasters,
        test_run=True
    )



    # =================================
    # EREDMÉNY RÉTEGEK SZÁMÁNAK TESZTJE
    # =================================

    test_number_of_layers_result = 0

    result_gdfs = {}

    searched_layers = [
        "vineyards",
        "settlements",
        "wine_districts",
        "wine_regions",
        "all"
    ]

    # Rétegek létezésének vizsgálata
    for searched_layer in searched_layers:
        try:
            result_gdfs[searched_layer] = gpd.read_file(
                pathlib.Path(config.RESULT_VECTOR_FILES_DIRECTORY_PATH) \
                    .joinpath("vineyards_analytics.gpkg"),
                layer=searched_layer
            )
            test_number_of_layers_result += 1
        except pyogrio.errors.DataLayerError:
            raise ValueError(
                f"A(z) '{searched_layer}' nevű réteg nem található."
            )

    assert test_number_of_layers_result == len(searched_layers)



    # =================================
    # EREDMÉNY RÉTEGEK MEZŐINEK TESZTJE
    # =================================

    test_fields_result = 0

    field_names = config.FIELD_NAMES

    # Keresendő mezők neveinek kigyűjtése
    searched_fields = []
    for old, new in field_names.items():
        if new == "":
            searched_fields.append(old)
        else:
            searched_fields.append(new)

    # Keresett rétegek bejárása
    for searched_layer in searched_layers:

        gdf = result_gdfs[searched_layer]

        # A mezők megfelelő névvel szerepelnek-e a GeoDataFrame-ekben
        for col in gdf.columns:
            if col not in searched_fields:
                break
        else:
            test_fields_result += 1


    assert test_fields_result == len(searched_layers)