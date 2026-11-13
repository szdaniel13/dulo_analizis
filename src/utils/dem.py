""" Lehetővé teszi a DEM-alapú domborzati paraméterek kiszámítását. """


import pathlib

import numpy as np
import whitebox
import richdem as rd

from src import utils


def handle_dem_file(
        rasters: dict[str, dict[str, pathlib.Path]],
        dem_prefix: str,
        raster_name: str,
        wbt: whitebox.WhiteboxTools
) -> tuple[str, pathlib.Path]:
    """ Kezeli a DEM-alapú fájlokat.

    A DEM-alapú fájlhoz fájlnevet és eléréi utat hoz létre. Ezen
    fájl eléréi útját el is tárolja a raszterek elérési útját tároló
    dict-be.

    Args:
        rasters: A raszterek elérési útját tároló dict.
        dem_prefix: A DEM-alapú fájlok prefix-sze.
        raster_name: A DEM-alapú raszter neve.
        wbt: A WhiteboxTools objektum.

    Returns:
        1. A DEM-alapú fájl neve.
        2. A DEM-alapú fájl elérési útja.
    """

    # Az eredmény fájl neve
    result_file_name = f"{dem_prefix}{raster_name}.tif"

    # Az eredmény fájl elérési útja
    result_file_path = (
        pathlib.Path(wbt.get_working_dir())
        .joinpath(result_file_name).absolute()
    )

    # Raszter tárolása a dict-ben
    rasters['dem'][result_file_name.split(".")[0]] = result_file_path

    return result_file_name, result_file_path


def calculate_breach_depression(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        dem_prefix: str
) -> None:
    """ Kitölti a DEM-et, ha lenne üres érték.

    Kitölti a DEM-et a Breach Depression módszerrel. Emellett a
    létrejövő fájl elérését el is tárolja a raszterek dict-jében.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        dem_prefix: Az eredmény fájl prefix-je.
    """

    # Az eredményfájl neve és elérési útja
    result_file_name, result_file_path = handle_dem_file(
        rasters,
        dem_prefix,
        "_breach_depression",
        wbt
    )

    # Ha már létezik a fájl ne számítson újra
    if not result_file_path.exists():

        # Raszter felbontása
        resolution = utils.raster.get_raster_resolution(
            rasters['dem'][f"{dem_prefix}_elevation"]
        )

        # Távolság a számításhoz
        if resolution <= 5:
            dist = 50
        elif resolution <= 20:
            dist = 60
        else:
            dist = 100

        # Fill Depression számítás
        wbt.breach_depressions_least_cost(
            f"{dem_prefix}_elevation.tif",
            result_file_name,
            dist=dist,
            fill=True
        )

def calculate_slope(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        dem_prefix: str
) -> None:
    """ Kiszámítja a DEM alapján a lejtőszöget fokban.

    Kiszámítja a DEM alapján a lejtőszöget fokban mérve és emellett
    el is tárolja azt a raszterek dict-jében.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        dem_prefix: Az eredmény fájl prefix-je.
    """

    # Az eredményfájl neve és elérési útja
    result_file_name, result_file_path = handle_dem_file(
        rasters,
        dem_prefix,
        "_slope",
        wbt
    )

    # Ha már létezik a fájl ne számítson újra
    if not result_file_path.exists():

        # Lejtőszög számítás fokban
        wbt.slope(
            f"{dem_prefix}_elevation.tif",
            result_file_name,
            units="degrees"
        )


def calculate_aspect(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        dem_prefix: str
) -> None:
    """ Kiszámítja a kitettséget a DEM alapján.

    Kiszámítja a DEM alapján a kitettség értékeket. Majd az eredmény
    raszter elérési útját eltárolja a raszter eléréseket tartalmazó
    dict-ben.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        dem_prefix: Az eredmény fájl prefix-je.
    """

    # Az eredményfájl neve és elérési útja
    result_file_name, result_file_path = handle_dem_file(
        rasters,
        dem_prefix,
        "_aspect",
        wbt
    )

    # Ha már létezik a fájl ne számítson újra
    if not result_file_path.exists():

        # Kitettség számítás
        wbt.aspect(
            f"{dem_prefix}_elevation.tif",
            result_file_name
        )


def calculate_flow_direction(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        dem_prefix: str
) -> None:
    """ Kiszámítja a Fill Depression alapján a lefolyásirányt.

    Kiszámítja a Fill Depression alapján a lefolyás irányát a Dinf
    módszerrel. Emellett az eredmény fájl elérési útját el is tárolja
    a raszterek elérési útját tároló dict-ben.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        dem_prefix: Az eredmény fájl prefix-je.
    """

    # Az eredményfájl neve és elérési útja
    result_file_name, result_file_path = handle_dem_file(
        rasters,
        dem_prefix,
        "_flow_direction",
        wbt
    )

    # Ha már létezik a fájl ne számítson újra
    if not result_file_path.exists():

        # Dinf Flow Direction
        wbt.d_inf_pointer(
            f"{dem_prefix}_breach_depression.tif",
            result_file_name
        )


def calculate_flow_accumulation(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        dem_prefix: str
) -> None:
    """ Kiszámítja a Flow Accumulation-t a Fill Depression alapján.

    Kiszámítja a Flow Accumulation-t a Fill Depression alapján. A
    számítás során a Dinf Flow Direction-t alkalmazza. Emellett az
    eredmény raszter elérési útját el is tárolja a raszterek elérési
    útját tartalmazó dict-ben.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        dem_prefix: Az eredmény fájl prefix-je.
    """

    # Az eredményfájl neve és elérési útja
    result_file_name, result_file_path = handle_dem_file(
        rasters,
        dem_prefix,
        "_flow_accumulation",
        wbt
    )

    # Ha már létezik a fájl ne számítson újra
    if not result_file_path.exists():

        # Flow Accumulation számítása Dinf módszer alapján
        wbt.d_inf_flow_accumulation(
            f"{dem_prefix}_breach_depression.tif",
            result_file_name
        )


def calculate_topographic_wetness_index(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        dem_prefix: str
) -> None:
    """ Kiszámítja a Topográfiai Nedvesség Indexet.

    Kiszámítja a Topográfiai Nedvesség Indexet (TWI - Topographic
    Wetness Index) a Flow Accumulation és a Slope (fokban) alapján.
    Emellett az eredmény raszter elérési útját el is tárolja a
    raszterek elérési útját tartalmazó dict-be.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        dem_prefix: Az eredmény fájl prefix-je.
    """

    # Az eredményfájl neve és elérési útja
    result_file_name, result_file_path = handle_dem_file(
        rasters,
        dem_prefix,
        "_topographic_wetness_index",
        wbt
    )

    # Ha már létezik a fájl ne számítson újra
    if not result_file_path.exists():

        # Topográfiai Nedvesség Index számítása
        wbt.wetness_index(
            f"{dem_prefix}_flow_accumulation.tif",
            f"{dem_prefix}_slope.tif",
            result_file_name
        )


def calculate_sediment_transport_index(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        dem_prefix: str
) -> None:
    """ Kiszámítja az LS-faktort.

    Kiszámítja az LS-faktort (STI - Sediment Transport Index) a Flow
    Accumulation és a Slope (fokban) alapján. Emellett az eredmény
    raszter elérési útját el is tárolja a raszterek eléréi útját tároló
    dict-ben.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        dem_prefix: Az eredmény fájl prefix-je.
    """

    # Az eredményfájl neve és elérési útja
    result_file_name, result_file_path = handle_dem_file(
        rasters,
        dem_prefix,
        "_sediment_transport_index",
        wbt
    )

    # Ha már létezik a fájl ne számítson újra
    if not result_file_path.exists():

        # LS-faktor (STI - Sediment Transport Index)
        wbt.sediment_transport_index(
            f"{dem_prefix}_flow_accumulation.tif",
            f"{dem_prefix}_slope.tif",
            result_file_name
        )


def calculate_profile_curvature(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        dem_prefix: str
) -> None:
    """ Kiszámítja a profilgörbületet a Breach Depression alapján.

    Kiszámítja a profilgörbületet a Breach Depression-nel korrigált
    DEM alapján, amely jobb hidrológiai pontosságot ad. Emellett az
    eredmény raszter elérési útját el is tárolja a raszterek elérési
    útját tároló dict-ben.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        dem_prefix: Az eredmény fájl prefix-je.
    """

    # Az eredményfájl neve és elérési útja
    result_file_name, result_file_path = handle_dem_file(
        rasters,
        dem_prefix,
        "_profile_curvature",
        wbt
    )

    # Ha már létezik a fájl ne számítson újra
    if not result_file_path.exists():

        # Profilgörbület számítás
        wbt.profile_curvature(
            f"{dem_prefix}_breach_depression.tif",
            result_file_name
        )


def calculate_plan_curvature(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        dem_prefix: str
) -> None:
    """ Kiszámítja a Plan-görbületet a Breach Depression alapján.

    Kiszámítja a Plan-görbületet (másnéven tangenciális-görbületet) a
    Breach Depression-nel korrigált DEM alapján, amely jobb hidrológiai
    pontosságot ad. Emellett az eredmény raszter elérési útját el is
    tárolja a raszterek elérési útját tároló dict-ben.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        dem_prefix: Az eredmény fájl prefix-je.
    """

    # Az eredményfájl neve és elérési útja
    result_file_name, result_file_path = handle_dem_file(
        rasters,
        dem_prefix,
        "_plan_curvature",
        wbt
    )

    # Ha már létezik a fájl ne számítson újra
    if not result_file_path.exists():

        # A raszter felbontása méterben
        resolution = utils.raster.get_raster_resolution(
            rasters['dem'][f"{dem_prefix}_breach_depression"]
        )

        # Szűréshez használt pixel szám a felbontás alapján
        if resolution <= 10:
            filter_size = 11
        elif 10 < resolution <= 20:
            filter_size = 7
        else:
            filter_size = 5

        # Pixelzaj szűrése
        wbt.feature_preserving_smoothing(
            f"{dem_prefix}_breach_depression.tif",
            "temp.tif",
            filter=filter_size
        )

        # Plan-görbület (vagy Tangenciális-görbület) számítása
        wbt.plan_curvature(
            "temp.tif",
            result_file_name
        )

        # Ideiglenes fájl törlése
        pathlib.Path(wbt.get_working_dir()).joinpath("temp.tif").unlink()


def calculate_time_in_daylight(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        dem_prefix: str
) -> None:
    """ Napsütéses idő hosszának számítása a DEM alapján.

    A DEM alapján kiszámítja a napsütéses idő hosszát. A számítást
    április 1. (az év 91. napja) és október 31. (az év 304. napja)
    között végzi el. Minden napot 06:00 és 18:00 között számol.
    A számítást az eredmény raszter elérési útja elmentésre kerül
    a raszterek elérési útját tároló dict-ben.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        dem_prefix: Az eredmény fájl prefix-je.
    """

    # Az eredményfájl neve és elérési útja
    result_file_name, result_file_path = handle_dem_file(
        rasters,
        dem_prefix,
        "_time_in_daylight",
        wbt
    )

    # Ha már létezik a fájl ne számítson újra
    if not result_file_path.exists():

        # Raszter középpontjának koordinátái
        lat, long = utils.raster.get_raster_center_in_wgs84(
            rasters['dem'][f"{dem_prefix}_elevation"]
        )

        # Felbontás alapján számított maximális árnyék távolság
        resolution = utils.raster.get_raster_resolution(
            rasters['dem'][f"{dem_prefix}_elevation"]
        )
        if resolution <= 5:
            max_dist = 2000
        elif 5 < resolution <= 20:
            max_dist = 3500
        else:
            max_dist = 5000


        # Napsütéses idő hossz
        wbt.time_in_daylight(
            f"{dem_prefix}_elevation.tif",
            result_file_name,
            lat=lat,
            long=long,
            utc_offset="+02:00",
            max_dist=max_dist,
            start_day=91, # Április 1.
            end_day=304, # Október 31.
            start_time="06:00:00",
            end_time="18:00:00"
        )


def _solar_radiation(
        wbt: whitebox.WhiteboxTools,
        dem_prefix: str,
        result_file_path: pathlib.Path
) -> None:
    """ Belső megoldás a napsugárzás számításához.

    napsugrázás (kWh/m2/nap) = max_value * Time in Daylight *
    cos(radian(Slope))

    Args:
        wbt: A WhiteboxTools objektum.
        dem_prefix: Az eredmény fájl prefix-je.
        result_file_path: Az eredmény fájl elérési útja.
    """

    # Napsütéses idő hosszúsága
    time_in_daylight = rd.LoadGDAL(
        str(
            pathlib.Path(
                wbt.get_working_dir()
            ).joinpath(f"{dem_prefix}_time_in_daylight.tif")
        )
    )

    # Lejtőszög (fokban)
    slope = rd.LoadGDAL(
        str(
            pathlib.Path(
                wbt.get_working_dir()
            ).joinpath(f"{dem_prefix}_slope.tif")
        )
    )

    aspect = rd.LoadGDAL(
        str(
            pathlib.Path(
                wbt.get_working_dir()
            ).joinpath(f"{dem_prefix}_aspect.tif")
        )
    )

    # Raszter geometriai tulajdonságok
    geotransform = slope.geotransform
    projection = slope.projection

    # Hiányzó értékek kezelése
    time_in_daylight = np.where(
        time_in_daylight == time_in_daylight.no_data,
        np.nan,
        time_in_daylight
    )

    # Hiányzó értékek kezelése
    slope = np.where(
        slope == slope.no_data,
        np.nan,
        slope
    )

    # Potenciális napsugárzás számítása
    potential_solar_radiation = rd.rdarray(
        (5.05 * time_in_daylight * (
            (np.cos(np.deg2rad(slope)) * 0.82) +
            np.sin(np.deg2rad(slope)) *
            0.57 *
            np.cos(np.deg2rad(aspect - 180))
        )) + 2.60,
        no_data=np.nan
    )

    # Raszter geometriai tulajdonságok átadása
    potential_solar_radiation.geotransform = geotransform
    potential_solar_radiation.projection = projection

    # Új raszter fájlba mentése
    rd.SaveGDAL(
        result_file_path,
        potential_solar_radiation
    )


def calculate_potential_solar_radiation(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        dem_prefix: str
) -> None:
    """ Potenciális napsugrázás számítása a Time in Daylight alapján.

    Potenciális napsugárzás számítása a napsütéses idő hossza alapján
    egy napra (kWh/m2/nap).
    Az egyenlet: 6.0 * Time in daylight * cos(radián(Slope)).
    Az eredmény raszter elérési útját eltárolja a raszterek elérési
    útját tároló dict-ben.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        dem_prefix: Az eredmény fájl prefix-je.
    """

    # Az eredményfájl neve és elérési útja
    result_file_name, result_file_path = handle_dem_file(
        rasters,
        dem_prefix,
        "_potential_solar_radiation",
        wbt
    )

    # Ha már létezik a fájl ne számítson újra
    if not result_file_path.exists():

        # Potenciális napsugárzás kiszámítása
        _solar_radiation(
            wbt,
            dem_prefix,
            result_file_path
        )


def calculate_topographic_position_index(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        dem_prefix: str
) -> None:
    """ Kiszámítja a Topográfiai Helyzeti Indexet a DEM alapján.

    Kiszámítja a Topográfiai Helyzeti Indexet (TPI - Topographic
    Position Index) a DEM alapján. Emellett az eredmény raszter
    elérési útját el is tárolja a raszterek elérési útját tároló
    dict-ben.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        dem_prefix: Az eredmény fájl prefix-je.
    """

    # Az eredményfájl neve és elérési útja
    result_file_name, result_file_path = handle_dem_file(
        rasters,
        dem_prefix,
        "_topographic_position_index",
        wbt
    )

    # Ha már létezik a fájl ne számítson újra
    if not result_file_path.exists():

        # Topográfiai Helyzeti Index
        wbt.relative_topographic_position(
            f"{dem_prefix}_elevation.tif",
            result_file_name
        )


def calculate_roughness(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        dem_prefix: str
) -> None:
    """ Kiszámítja az érdességet a DEM alapján.

    Kiszámítja az érdességet (roughness a DEM alapján). Emellett az
    eredmény raszter fájl elérési útját el is tárolja a raszterek
    elérési útját tároló dict-ben.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        dem_prefix: Az eredmény fájl prefix-je.
    """

    # Az eredményfájl neve és elérési útja
    result_file_name, result_file_path = handle_dem_file(
        rasters,
        dem_prefix,
        "_roughness",
        wbt
    )

    # Ha már létezik a fájl ne számítson újra
    if not result_file_path.exists():

        # Érdesség kiszámítása
        wbt.multiscale_roughness(
            f"{dem_prefix}_elevation.tif",
            result_file_name,
            "temp.tif",
            max_scale=4
        )

        # Ideiglenes fájl törlése
        pathlib.Path(wbt.get_working_dir()).joinpath("temp.tif").unlink()