""" Az adatok betöltésének folyamatát valósítja meg. Betölti a vektoros
adatokat egy-egy GeoDataFrame-be, amelyeket egy dict-ben tárol.
A rasteres adatok esetében pedig egy másik dict-ben külön belső
dict-ekben tárolja el a DEM-alapú és a meteorológiai rasterek elérési
útjait.
"""


import pathlib
import typing

import geopandas as gpd

from src import utils
import config


def load_vector_files(test_run: bool) -> dict[str, gpd.GeoDataFrame]:
    """ Vektor fájlok betöltése.

    Vektor fájlokat betölti egy-egy GeoDataFrame-be EPSG:23700-as
    CRS-sel, majd a GeoDataFrame-eket egy Python dict-be tárolja.

    Args:
        test_run: Teszt futtatáshoz használt-e a függvény?

    Returns:
        A dict, amely a GeoDataFrame-eket tárolja.
    """

    import pyogrio.errors

    # A "stopper" indítása
    if not test_run:
        start = utils.run_time.start_time(
            "A load_data.load_vector_files() függvény futása elindult.",
            2
        )

    gdfs = {}

    # Dűlők betöltése
    try:
        vineyards = gpd.read_file(
            config.VINEYARDS_FILE_PATH,
            layer=(
                config.VINEYARDS_LAYER_NAME
                if config.VINEYARDS_FILE_PATH.lower().endswith(".gpkg")
                else None
            )
        ).to_crs(23700)[[config.VINEYARDS_NAME_FIELD, "geometry"]] \
            .rename(columns={config.VINEYARDS_NAME_FIELD: "name"})

        gdfs["vineyards"] = vineyards

    except pyogrio.errors.DataSourceError:
        raise ValueError(f"'{config.VINEYARDS_FILE_PATH}' nem található.")

    except pyogrio.errors.DataLayerError:
        raise ValueError(
            f"'{config.VINEYARDS_FILE_PATH}' fájlon belül nem található "
            f"'{config.VINEYARDS_LAYER_NAME}' nevű réteg."
        )

    except KeyError:
        raise ValueError(
            f"'{config.VINEYARDS_FILE_PATH}' fájlon belüli "
            f"'{config.VINEYARDS_LAYER_NAME}' nevű rétegnek nincs "
            f"'{config.VINEYARDS_NAME_FIELD}' nevő mezője."
        )

    # Települések betöltése (ha kell)
    try:
        if config.SETTLEMENTS_FILE_PATH:
            settlements = gpd.read_file(
                config.SETTLEMENTS_FILE_PATH,
                layer=(
                    config.SETTLEMENTS_LAYER_NAME
                    if config.SETTLEMENTS_FILE_PATH.lower().endswith(".gpkg")
                    else None
                )
            ).to_crs(23700)[[config.SETTLEMENTS_NAME_FIELD, "geometry"]] \
                .rename(columns={config.SETTLEMENTS_NAME_FIELD: "settlement"})
            gdfs["settlements"] = settlements

    except pyogrio.errors.DataSourceError:
        raise ValueError(f"'{config.SETTLEMENTS_FILE_PATH}' nem található.")

    except pyogrio.errors.DataLayerError:
        raise ValueError(
            f"'{config.SETTLEMENTS_FILE_PATH}' fájlon belül nem található "
            f"'{config.SETTLEMENTS_LAYER_NAME}' nevű réteg."
        )

    except KeyError:
        raise ValueError(
            f"'{config.SETTLEMENTS_FILE_PATH}' fájlon belüli "
            f"'{config.SETTLEMENTS_LAYER_NAME}' nevű rétegnek nincs "
            f"'{config.SETTLEMENTS_NAME_FIELD}' nevő mezője."
        )

    # Borvidékek betöltése (ha kell)
    try:
        if config.WINE_DISTRICTS_FILE_PATH:
            wine_ditricts = gpd.read_file(
                config.WINE_DISTRICTS_FILE_PATH,
                layer=(
                    config.WINE_DISTRICTS_LAYER_NAME
                    if config.WINE_DISTRICTS_FILE_PATH.lower().endswith(".gpkg")
                    else None
                )
            ).to_crs(23700)[[config.WINE_DISTRICTS_NAME_FIELD, "geometry"]] \
                .rename(
                    columns={config.WINE_DISTRICTS_NAME_FIELD: "wine_district"}
                )
            gdfs["wine_districts"] = wine_ditricts

    except pyogrio.errors.DataSourceError:
        raise ValueError(f"'{config.WINE_DISTRICTS_FILE_PATH}' nem található.")

    except pyogrio.errors.DataLayerError:
        raise ValueError(
            f"'{config.WINE_DISTRICTS_FILE_PATH}' fájlon belül nem található "
            f"'{config.WINE_DISTRICTS_LAYER_NAME}' nevű réteg."
        )

    except KeyError:
        raise ValueError(
            f"'{config.WINE_DISTRICTS_FILE_PATH}' fájlon belüli "
            f"'{config.WINE_DISTRICTS_LAYER_NAME}' nevű rétegnek nincs "
            f"'{config.WINE_DISTRICTS_NAME_FIELD}' nevő mezője."
        )

    # Borrégiók betöltése (ha kell)
    try:
        if config.WINE_REGIONS_FILE_PATH:
            wine_regions = gpd.read_file(
                config.WINE_REGIONS_FILE_PATH,
                layer=(
                    config.WINE_REGIONS_LAYER_NAME
                    if config.WINE_REGIONS_FILE_PATH.lower().endswith(".gpkg")
                    else None
                )
            ).to_crs(23700)[[config.WINE_REGIONS_NAME_FIELD, "geometry"]] \
                .rename(
                    columns={config.WINE_REGIONS_NAME_FIELD: "wine_region"}
                )
            gdfs["wine_regions"] = wine_regions

    except pyogrio.errors.DataSourceError:
        raise ValueError(f"'{config.WINE_REGIONS_FILE_PATH}' nem található.")

    except pyogrio.errors.DataLayerError:
        raise ValueError(
            f"'{config.WINE_REGIONS_FILE_PATH}' fájlon belül nem található "
            f"'{config.WINE_REGIONS_LAYER_NAME}' nevű réteg."
        )

    except KeyError:
        raise ValueError(
            f"'{config.WINE_REGIONS_FILE_PATH}' fájlon belüli "
            f"'{config.WINE_REGIONS_LAYER_NAME}' nevű rétegnek nincs "
            f"'{config.WINE_REGIONS_NAME_FIELD}' nevő mezője."
        )

    # Talajok betöltése
    try:
        soil_property_fields = config.SOILS_PROPERTY_FIELDS.copy()
        soil_property_fields.append("geometry")
        soils = gpd.read_file(
            config.SOILS_FILE_PATH,
            layer=(
                config.SOILS_LAYER_NAME
                if config.SOILS_FILE_PATH.lower().endswith(".gpkg")
                else None
            )
        ).to_crs(23700)[soil_property_fields]
        gdfs["soils"] = soils

    except pyogrio.errors.DataSourceError:
        raise ValueError(f"'{config.SOILS_FILE_PATH}' nem található.")

    except pyogrio.errors.DataLayerError:
        raise ValueError(
            f"'{config.SOILS_FILE_PATH}' fájlon belül nem található "
            f"'{config.SOILS_LAYER_NAME}' nevű réteg."
        )

    except KeyError:
        raise ValueError(
            f"'{config.SOILS_FILE_PATH}' fájlon belüli "
            f"'{config.SOILS_LAYER_NAME}' nevű rétegben nem található legalább "
            f"egy mező a következők közül: {config.VINEYARDS_NAME_FIELD}."
        )

    # A "stopper" leállítása
    if not test_run:
        utils.run_time.end_time(
            "A load_data.load_vector_files() függvény futása "
            "befejeződött.",
            start,
            2
        )

    return gdfs


def load_raster_files(
        rasters: dict[str, dict],
        data_type: typing.Literal["dem", "meteorological"],
        test_run: bool
) -> None:
    """ Betölti a raszter fájlokat.

    A raszter fájlokat betölti és a CRS-t mindegyik esetében
    EPSG:23700-ra állítja (transzformálja). A transzformálás során
    létrejövő új raszterek elérési útját pedig eltárolja egy dict-ben.
    A dict kulcsai a fájl nevek alapján vannak elnevezve.

    Args:
        rasters: A rasztereket tároló dict.
        data_type: Az adattípusa (DEM vagy meteorológiai adat)
        test_run: Teszt futtatáshoz használt-e a függvény?
    """

    # A "stopper" indítása
    if not test_run:
        start = utils.run_time.start_time(
            f"A load_data.load_raster_files(rasters, {data_type}) "
            f"függvény futása elindult.",
            2
        )

    # Abszolút elérési utak kinyerése
    if data_type == "dem":
        directory_path = pathlib.Path(
            config.DEM_FILE_DIRECTORY_PATH
        )
    else:
        directory_path = pathlib.Path(
            config.METEOROLOGICAL_RASTER_DATA_DIRECTORY_PATH
        )

    # A megadott mappa bejárása
    try:
        for item in directory_path.iterdir():

            # Ha .tif fájl, akkor mentse le
            if item.is_file() and str(item).lower().endswith(".tif"):
                rasters[data_type][str(item.name)[:-4]] = (
                    directory_path.joinpath(item.name).absolute()
                )

                rasters[data_type][str(item.name)[:-4]] = (
                    utils.raster.raster_to_eov(
                        rasters[data_type][str(item.name)[:-4]],
                        data_type
                    )
                )

            # Ha mappa, akkor azt is járja be
            elif not item.is_file():
                item_absolute_path = directory_path.joinpath(item.name).absolute()

                # A belső elem kezelése
                for inner_item in item_absolute_path.iterdir():
                    if inner_item.is_file and str(inner_item).lower() \
                            .endswith(".tif"):
                        rasters[data_type][str(inner_item.name)[:-4]] = (
                            item_absolute_path.joinpath(inner_item.name)
                        )

                        rasters[data_type][str(inner_item.name)[:-4]] = (
                            utils.raster.raster_to_eov(
                                rasters[data_type][str(inner_item.name)[:-4]],
                                data_type
                            )
                        )

            # Csak 1 DEM legyen
            if data_type == 'dem' and len(rasters['dem'].keys()) == 1:
                break

    except FileNotFoundError:
        raise ValueError(f"'{directory_path}' mappa nem található.")

    if len(rasters[data_type].keys()) == 0:
        raise ValueError(f"'{directory_path}' mappán belül nem található "
                         f"megfelelő '.tif' fájl '{data_type.upper()}' "
                         f"számára.")

    # A "stopper" indítása
    if not test_run:
        utils.run_time.end_time(
            f"A load_data.load_raster_files(rasters, {data_type}) "
            f"függvény futása elindult.",
            start,
            2
        )


# ===============================================
# AZ ADATBETÖLTÉS FOLYAMATA
# ===============================================

def process(test_run: bool = False) \
        -> tuple[
            dict[str, gpd.GeoDataFrame],
            dict[str, dict[str, pathlib.Path]]
        ]:
    """ Végre hajtja az adatbetöltés folyamatát.

    Betölti a vektor fájlokat GeoDataFrame-be, a rasztereket pedig az
    elérési útjuk alapján tárolja. Mind a GeoDataFrame-ek, mind a
    raszterek egy-egy közös dict-be kerülnek.

    Args:
        test_run: Teszt futtatáshoz használt-e a függvény?

    Returns:
        1. GeoDataFrame-eket tartalmazó dict.
        2. A raszterek elérési útjait tartalmazó dict.
    """

    # A "stopper" indítása
    if not test_run:
        start = utils.run_time.start_time(
            "A load_data.process() függvény futása elindult.",
            1
        )

    gdfs = load_vector_files(test_run=test_run)

    rasters = {"dem": {}, "meteorological": {}}

    for data_type in ["dem", "meteorological"]:
        load_raster_files(
            rasters,
            data_type,
            test_run=test_run
        )

    if not test_run:
        # A "stopper" leállítása
        utils.run_time.end_time(
            "A load_data.process() függvény futása befejeződött.",
            start,
            1
        )

    return gdfs, rasters