""" A rasteres adatok vektoros adatokhoz történő kapcsolásának
folyamatát valósítja meg. A folytonos DEM-alapú rasterek esetén zóna
statisztika. Az újraosztályozott DEM-alapú rasterek esetén kategóriák
területi aránya. A meteorológiai rasterek esetén pedig területtel
súlyozott átlag.
"""


import pathlib

import geopandas as gpd

from src import utils


def add_zonal_stats(
        gdfs: dict[str, gpd.GeoDataFrame],
        rasters: dict[str, dict[str, pathlib.Path]],
        dem_prefix: str,
        inner_function: bool = False,
        test_run: bool = False
) -> None:
    """ Hozzáadja a zóna statisztikákat a dűlőkhöz.

    Hozzáadja a különböző raszterek zóna statisztika értékeit az egyes
    dűlőkhöz a dűlőket tartalmazó GeoDataFrame-ben.

    Args:
        gdfs: A GeoDataFrame-eket tartalmazó dict.
        rasters: A raszterek elérési útját tartalmazó dict.
        dem_prefix: A DEM-alapú fájlok neveinek előtagja.
        inner_function: Belső függvényről van-e szó?
        test_run: Teszt futtatáshoz használt-e a függvény?
    """

    if not inner_function and not test_run:
        # A "stopper" indítása
        start = utils.run_time.start_time(
            "A join_rasters_on_polygons.calculate_zonal_statistics."
            "add_zonal_stats(gdfs, rasters, file_prefix) függvény futása "
            "elindult.",
            2
        )

    # Dűlőket tartalmazó GeoDataFrame
    vineyards = gdfs["vineyards"]

    # Raszterek elérési útjai
    raster_file_paths = [rasters['dem'][raster_name]
                         for raster_name in rasters['dem'].keys()
                         if "class" not in raster_name]

    # Raszterek nevei
    raster_names = [raster_name.replace(f"{dem_prefix}_", "")
                    for raster_name in rasters['dem'].keys()
                    if "class" not in raster_name]

    # A raszterek bejárása a zóna statisztikához
    for raster_file_path, raster_name in zip(raster_file_paths, raster_names):

        if raster_name in [
            "breach_depression",
            "aspect",
            "flow_direction"
        ]:
            continue

        # Zóna statisztika az adott raszter alapján
        vineyards = utils.raster.zonal_statistics(
            vineyards,
            raster_file_path,
            raster_name
        )

    # Dűlőket tartalmazó raszter visszaírása a dict-be
    gdfs["vineyards"] = vineyards

    if not inner_function and not test_run:
        # A "stopper" leállítása
        utils.run_time.end_time(
            "A join_rasters_on_polygons.calculate_zonal_statistics."
            "add_zonal_stats(gdfs, rasters, file_prefix) függvény futása "
            "befejeződött.",
            start,
            2
        )


def add_classes_area_rate(
        gdfs: dict[str, gpd.GeoDataFrame],
        rasters: dict[str, dict[str, pathlib.Path]],
        dem_prefix: str,
        inner_function: bool = False,
        test_run: bool = False
) -> None:
    """ Az újraosztályozott adatokat hozzákapcsolja a dűlőkhöz.

    Az egyes újraosztályozott raszteres adatok osztályainak területi
    arányát kapcsolja az egyes dűlőkhöz. Minden osztály külön mezőt
    kap.

    Args:
        gdfs: A GeoDataFrame-eket tartalmazó dict.
        rasters: A raszterek elérési útját tartalmazó dict.
        dem_prefix: A DEM-alapú fájlok neveinek előtagja.
        inner_function: Belső függvényről van-e szó?
        test_run: Teszt futtatáshoz használt-e a függvény?
    """

    if not inner_function and not test_run:
        # A "stopper" indítása
        start = utils.run_time.start_time(
            "A join_rasters_on_polygons.calculate_zonal_statistics."
            "add_classes_area_rate(gdfs, rasters, file_prefix) függvény futása "
            "elindult.",
            2
        )

    # Dűlőket tartalmazó GeoDataFrame
    vineyards = gdfs["vineyards"]

    # Raszterek elérési útjai
    raster_file_paths = [rasters['dem'][raster_name]
                         for raster_name in rasters['dem'].keys()
                         if "class" in raster_name]

    # Raszterek szűrése név alapján
    raster_names = [raster_name.replace(f"{dem_prefix}_", "")
                    for raster_name in rasters['dem'].keys()
                    if "class" in raster_name]

    # A raszterek bejárása a zóna statisztikához
    for raster_file_path, raster_name in zip(raster_file_paths, raster_names):

        # Osztály értékek kapcsolása a dűlőkhöz
        vineyards = utils.raster.join_reclassified_raster_on_polygons(
            vineyards,
            raster_file_path,
            raster_name
        )

    # Üres értékek feltöltése 0-val, illetve üres oszlopok törlése
    vineyards = vineyards.dropna(axis="columns", how="all")
    vineyards = vineyards.fillna(0)

    gdfs["vineyards"] = vineyards

    if not inner_function and not test_run:
        # A "stopper" leállítása
        utils.run_time.end_time(
            "A join_rasters_on_polygons.calculate_zonal_statistics."
            "add_classes_area_rate(gdfs, rasters, file_prefix) függvény futása "
            "befejeződött.",
            start,
            2
        )


def add_meteorological_data(
        gdfs: dict[str, gpd.GeoDataFrame],
        rasters: dict[str, dict[str, pathlib.Path]],
        inner_function: bool = False,
        test_run: bool = False
) -> None:
    """ A meteorológiai adatokat kapcsolja a dűlőkhöz.

    A meteorológiai adatokat hozzáadja az egyes dűlőkhöz. Az adatok
    terület átlaga kerül hozzáadásra a dűlők adataihoz.

    Args:
        gdfs: A GeoDataFrame-eket tartalmazó dict.
        rasters: A raszterek elérési útját tartalmazó dict.
        inner_function: Belső függvényről van-e szó?
        test_run: Teszt futtatáshoz használt-e a függvény?
    """

    if not inner_function and not test_run:
        # A "stopper" indítása
        start = utils.run_time.start_time(
            "A join_rasters_on_polygons.calculate_zonal_statistics."
            "add_meteorological_data(gdfs, rasters, file_prefix) függvény futása "
            "elindult.",
            2
        )

    # Dűlőket tartalmazó GeoDataFrame
    vineyards = gdfs["vineyards"]

    # Raszterek elérési útjai
    raster_file_paths = [rasters['meteorological'][raster_name]
                         for raster_name in rasters['meteorological'].keys()]

    # Raszterek nevei
    raster_names = [raster_name
                    for raster_name in rasters['meteorological'].keys()]

    # A raszterek bejárása a zóna statisztikához
    for raster_file_path, raster_name in zip(raster_file_paths, raster_names):

        vineyards = utils.raster.join_meteorological_data_on_polygons(
            vineyards,
            raster_file_path,
            raster_name
        )

    # Mezők (vagy oszlopok) sorrendjének rendezése
    columns = list(vineyards.columns)
    columns.remove("geometry")
    columns.append("geometry")
    vineyards = vineyards[columns]

    gdfs["vineyards"] = vineyards

    if not inner_function and not test_run:
        # A "stopper" indítása
        utils.run_time.end_time(
            "A join_rasters_on_polygons.calculate_zonal_statistics."
            "add_meteorological_data(gdfs, rasters, file_prefix) függvény futása "
            "befejeződött.",
            start,
            2
        )


# ===============================================
# A RASZTEREK DŰLŐK POLIGONJAIHOZ KAPCSOLÁSÁNAK FOLYAMATA
# ===============================================

def process(
        gdfs: dict[str, gpd.GeoDataFrame],
        rasters: dict[str, dict[str, pathlib.Path]],
        inner_function: bool = False,
        test_run: bool = False
) -> None:
    """ A raszterek dűlőkhöz kapcsolásának folyamatát hajtja végre.

    A rasztereket különböző módokon kapcsolja a dűlőkhöz. A folytonos
    értékeket tartalmazó domborzati rasztereket zóna statisztikával
    kapcsolja a dűlőkhöz. Az újraosztályozott értékeket domborzati
    rasztereket az egyes osztályok (kategóriák) területi arányával
    kapcsolja a dűlőkhöz. A meteorológiai adatokat pedig területi
    átlaggal kapcsolja a dűlőkhöz.

    Args:
        gdfs: A GeoDataFrame-eket tartalmazó dict.
        rasters: A raszterek elérési útját tartalmazó dict.
        inner_function: Belső függvényről van-e szó?
        test_run: Teszt futtatáshoz használt-e a függvény?
    """

    if not inner_function and not test_run:
        # A "stopper" indítása
        start = utils.run_time.start_time(
            "A join_rasters_on_polygons.calculate_zonal_statistics.process"
            "(gdfs, rasters) függvény futása elindult.",
            1
        )

    dem_prefix = list(rasters["dem"].keys())[0][:-10]

    # Zóna statisztikák hozzáadása a dűlőkhöz
    add_zonal_stats(
        gdfs,
        rasters,
        dem_prefix,
        inner_function=inner_function,
        test_run=test_run
    )

    # Az újraosztályozott értékek területi arányának hozzáadása a dűlőkhöz
    add_classes_area_rate(
        gdfs,
        rasters,
        dem_prefix,
        inner_function=inner_function,
        test_run=test_run
    )

    # Meteorológiai adatok hozzáadása a dűlőkhöz
    add_meteorological_data(
        gdfs,
        rasters,
        inner_function=inner_function,
        test_run=test_run
    )

    if not inner_function and not test_run:
        # A "stopper" leállítása
        utils.run_time.end_time(
            "A join_rasters_on_polygons.calculate_zonal_statistics.process"
            "(gdfs, rasters) függvény futása befejeződött.",
            start,
            1
        )