""" A rasteres adatok kiszámításának folyamatát tartalmazza.
DEM-alapján domborzati paraméterek számítása. DEM-alapú rasterek
újraosztályozása.
"""


import os
import pathlib
import sys

import whitebox

import config
from src import utils


def calculate_terrain_parameters(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        file_prefix: str,
        test_run: bool
) -> None:
    """ Kiszámítja a domborzati paramétereket, majd fájlba is menti
    őket.

    A domborzatmodell alapján kiszámítja a különböző domborzati
    paramétereket (pl. lejtőszög, kitettség, folyásirány,
    rofilgörbület stb.). A számítás után egyből fájlba is menti a
    létre jövő rasztereket.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszterek elérési útját tároló dict.
        file_prefix: A raszterek neveinek előtagja.
        test_run: Teszt futtatáshoz használt-e a függvény?
    """

    if not test_run:
        # A "stopper" indítása
        start = utils.run_time.start_time(
            "A calculate_raster_data.calculate_terrain_parameters(wbt, "
            "rasters, file_prefix) függvény futása elindult.",
            2
        )

    # Kitöltött DEM fájl későbbi számításokhoz (Breach Depression)
    utils.dem.calculate_breach_depression(
        wbt,
        rasters,
        file_prefix
    )

    # A lejtőszög fokban mérve a DEM alapján
    utils.dem.calculate_slope(
        wbt,
        rasters,
        file_prefix
    )

    # Kitettség (fokban) a DEM alapján
    utils.dem.calculate_aspect(
        wbt,
        rasters,
        file_prefix
    )

    # Dinf Flow Direction (folyási irány) a Breach Depression alapján
    utils.dem.calculate_flow_direction(
        wbt,
        rasters,
        file_prefix
    )

    # Flow Accumulation a Dinf Flow Direction alapján
    utils.dem.calculate_flow_accumulation(
        wbt,
        rasters,
        file_prefix
    )

    # Topográfiai Nedvesség Index (TWI - Topographic Wetness Index)
    utils.dem.calculate_topographic_wetness_index(
        wbt,
        rasters,
        file_prefix
    )

    # Sediment Transport Index (STI)
    utils.dem.calculate_sediment_transport_index(
        wbt,
        rasters,
        file_prefix
    )

    # Profilgörbület számítása a Breach Depression alapján
    utils.dem.calculate_profile_curvature(
        wbt,
        rasters,
        file_prefix
    )

    # Plan-görbület (másnéven tangenciális-görbület)
    utils.dem.calculate_plan_curvature(
        wbt,
        rasters,
        file_prefix
    )

    # Napsütéses idő hossza
    utils.dem.calculate_time_in_daylight(
        wbt,
        rasters,
        file_prefix
    )

    # Potenciális napsütéses értékek (kWh/m2/nap)
    utils.dem.calculate_potential_solar_radiation(
        wbt,
        rasters,
        file_prefix
    )

    # Topográfiai Helyzeti Index (TPI - Topographic Position Index)
    utils.dem.calculate_topographic_position_index(
        wbt,
        rasters,
        file_prefix
    )

    # Érdesség számítása
    utils.dem.calculate_roughness(
        wbt,
        rasters,
        file_prefix
    )

    if not test_run:
        # A "stopper" leállítása
        utils.run_time.end_time(
            "A calculate_raster_data.calculate_terrain_parameters(wbt, "
            "rasters, file_prefix) függvény futása befejeződött.",
            start,
            2
        )


def reclassify_rasters(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        file_prefix: str,
        test_run: bool
) -> None:
    """ Újraosztályozza a domborzati rasztereket.

    Újraosztáyozza a domborzati rasztereket különböző szabályok
    szerint. Példák a szabályokra: kitettség esetében égtájanként
    (észak, északkelet, kelet ... északnyugat), lejtőszögek esetében
    a meredekség szintek alapján (0 - 2, 2 - 5, 5 - 12, 12 - 25, 25 <).
    Természetesen fájlba is menti a létrejövő rasztereket.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszterek elérési útját tároló dict.
        file_prefix: A domborzatmodell nevének előtagja.
        test_run: Teszt futtatáshoz használt-e a függvény?
    """

    if not test_run:
        # A "stopper" indítása
        start = utils.run_time.start_time(
            "A calculate_raster_data.reclassify_rasters(wbt, rasters, "
            "file_prefix) függvény futása elindult.",
            2
        )

    # Magasság értékeket tartalmazó raszter újraosztályozása
    utils.reclassification.reclassify_elevation(
        wbt,
        rasters,
        file_prefix
    )

    # Lejtőszög értékeket tartalmazó raszter újraosztályozása
    utils.reclassification.reclassify_slope(
        wbt,
        rasters,
        file_prefix
    )

    # Kitettség értékeket tartalmazó raszter újraosztályozása
    utils.reclassification.reclassify_aspect(
        wbt,
        rasters,
        file_prefix
    )

    # Folyásirány értékeket tartalmazó raszter újraosztályozása
    utils.reclassification.reclassify_flow_direction(
        wbt,
        rasters,
        file_prefix
    )

    # Flow Accumulation értékeket tartalmazó raszter újraosztályozása
    utils.reclassification.reclassify_flow_accumulation(
        wbt,
        rasters,
        file_prefix
    )

    # Topográfiai Nedvesség Index értékeket tartalmazó raszter újraosztályozása
    utils.reclassification.reclassify_topographic_wetness_index(
        wbt,
        rasters,
        file_prefix
    )

    # Sediment Transport Index értékeket tartalmazó raszter újraosztályozása
    utils.reclassification.reclassify_sediment_transport_index(
        wbt,
        rasters,
        file_prefix
    )

    # Profile Curvature értékeket tartalmazó raszter újraosztályozása
    utils.reclassification.reclassify_profile_curvature(
        wbt,
        rasters,
        file_prefix
    )

    # Plan Curvature értékeket tartalmazó raszter újraosztályozása
    utils.reclassification.reclassify_plan_curvature(
        wbt,
        rasters,
        file_prefix
    )

    # Felszínforma értékek (Plan Cuevature RC + Profile Curvature RC)
    utils.reclassification.calculate_landform_class(
        wbt,
        rasters,
        file_prefix
    )

    # Napsütéses idő hosszát tartalmazó raszter újraosztályozása
    utils.reclassification.reclassify_time_in_daylight(
        wbt,
        rasters,
        file_prefix
    )

    # Potenciális napsugrázás értékeket tartalmazó raszter újraosztályozása
    utils.reclassification.reclassify_potential_solar_radiation(
        wbt,
        rasters,
        file_prefix
    )

    # Topográfiai Helyzeti Index értékeket tartalmazó raszter újraosztályozása
    utils.reclassification.reclassify_topographic_position_index(
        wbt,
        rasters,
        file_prefix
    )

    # Érdesség értékeket tartalmazó raszter újraosztályozása
    utils.reclassification.reclassify_roughness(
        wbt,
        rasters,
        file_prefix
    )

    if not test_run:
        # A "stopper" leállítása
        utils.run_time.end_time(
            "A calculate_raster_data.reclassify_rasters(wbt, rasters, "
            "file_prefix) függvény futása befejeződött.",
            start,
            2
        )


# ===============================================
# RASZTER ADATOKKAL TÖRTÉNŐ SZÁMÍTÁSOK FOLYAMATA
# ===============================================

def process(
        rasters: dict[str, dict[str, pathlib.Path]],
        test_run: bool = False
) -> None:
    """ A raszter adatokkal történő számítások folyamatát hajtja végre.

    A raszter adatokkal történő számítások folyamatát hajtja végre.
    Olyan számításokat végez, mint a domborzati paraméterek
    kiszámítása, illetve ezen raszterek értékeinek újraosztályozása.

    Args:
        rasters: A raszterek elérési útjait tartalmazó dict.
        test_run: Teszt futtatáshoz használt-e a függvény?
    """

    if not test_run:
        # A "stopper" indítása
        start = utils.run_time.start_time(
            "A calculate_raster_data.process(rasters) függvény futása "
            "elindult.",
            1
        )

    # A DEM fájlok előtagja
    dem_prefix = list(rasters["dem"].keys())[0][:-10]

    # A munka mappa abszolút elérési útja
    working_dir = pathlib.Path(config.RESULT_DEM_FILES_DIRECTORY_PATH).absolute()

    # WhiteBoxTools a domborzati paraméterek számításához
    wbt = whitebox.WhiteboxTools()
    whitebox.download_wbt(verbose=False)
    wbt.set_verbose_mode(False)  # Ne szemetelje tele a konzolt
    wbt.set_max_procs(-1)  # Az összees processzor mag használata
    wbt.set_compress_rasters(True)
    wbt.set_working_dir(working_dir)

    # Domborzati paraméterek számítása
    calculate_terrain_parameters(
        wbt,
        rasters,
        dem_prefix,
        test_run=test_run
    )

    # Raszterek újraosztályozása
    reclassify_rasters(
        wbt,
        rasters,
        dem_prefix,
        test_run=test_run
    )

    if not test_run:
        # A "stopper" leállítása
        utils.run_time.end_time(
            "A calculate_raster_data.process(rasters) függvény futása "
            "befejeződött.",
            start,
            1
        )