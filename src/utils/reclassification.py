""" A DEM-alapú rasterek újraosztályozásához nyújt segédfüggvényeket. """


import pathlib
import time

import whitebox

import config


def _reclassify(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        dem_prefix: str,
        raster_name: str,
        primary_reclassification: dict[int, str],
        secondary_reclassification: dict[int, int] | None = None
) -> None:
    """ A raszterek újraosztályozását valósítja meg.

    Újraosztályozza a rasztereket a megadott feltételes intervallumok
    mentén. Az elsődleges újraosztályozásnál az eredeti raszter értékei
    vannak figyelembe véve, míg a másodlagos osztályozásnál már az
    elsődleges újraosztályozás értékei. Emellett az eredmény raszter
    elérési útját el is tárolja a raszterek elérési útját tartalmazó
    dict-ben.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        dem_prefix: Az eredmény fájl prefix-je.
        raster_name: A raszter neve prefix nélkül.
        primary_reclassification: Az elsődleges újraosztályozás
            szabályrendszere.
        secondary_reclassification: A másodlagos újraosztályozás
            szabályrendszere.
    """

    # A forrás és eredmény fájl neve és elérési útja
    src_file_name = f"{dem_prefix}{raster_name}.tif"
    result_file_name = f"{dem_prefix}{raster_name}_reclassified.tif"
    result_file_path = pathlib.Path(wbt.get_working_dir()).joinpath(result_file_name)

    # Raszter tárolása a dict-ben
    rasters['dem'][result_file_name.split(".")[0]] = result_file_path

    if result_file_path.exists():
        return

    # Elsődleges újraosztályozás
    reclass_vals = []
    for new_value, interval in primary_reclassification.items():

        # Minimum és maximum értékek kinyerése
        if isinstance(interval, str):
            min_value, max_value = tuple(interval.split(" - "))
        else:
            # Tuple esetében
            min_value, max_value = interval[0], interval[1]

        # Újraosztályozás értékek megadása
        reclass_vals.append(str(new_value))
        reclass_vals.append(min_value)
        reclass_vals.append(max_value)

    # Megfelelő formátum kialakítása az újraosztályozás értékeinél
    reclass_vals = ";".join(reclass_vals)

    # Újraosztályozás
    wbt.reclass(
        src_file_name,
        result_file_name if not secondary_reclassification else "temp.tif",
        reclass_vals
    )

    # Ha kell másodlagos újraosztályozás
    if secondary_reclassification:

        reclass_vals = []

        for new_value, old_value in secondary_reclassification.items():
            reclass_vals.append(str(new_value))
            reclass_vals.append(str(old_value))

        reclass_vals = ";".join(reclass_vals)

        # Másodlagos újraosztályozás
        wbt.reclass(
            "temp.tif",
            result_file_name,
            reclass_vals,
            assign_mode=True
        )

        # "temp.tif" ideiglenes fájl törlése
        time.sleep(0.5)
        pathlib.Path(wbt.get_working_dir()).joinpath("temp.tif").unlink(
            missing_ok=True
        )



def reclassify_elevation(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        file_prefix: str,
) -> None:
    """ Újraosztályozza a magasság értékeket tartalmazó rasztert.

    Újraosztályozza a magasság értékeket tartalmazó rasztert 19
    különböző osztályba. Emellett az eredmény raszter elérési útját is
    eltárolja a raszterek elérési útját tároló dict-ben.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        file_prefix: Az eredmény fájl prefix-je.
    """

    # Magasság értékek újraosztályozása
    _reclassify(
        wbt,
        rasters,
        file_prefix,
        "_elevation",
        config.ELEVATION_RECLASSIFICATION_RULES
    )


def reclassify_slope(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        file_prefix: str,
) -> None:
    """ Újraosztályozza a lejtőszög értékeket tartalmazó rasztert.

    Újraosztályozza a lejtőszög értékeket tartalmazó rasztert 5
    különböző osztályba. Emellett az eredmény raszter elérési útját is
    eltárolja a raszterek elérési útját tároló dict-ben.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        file_prefix: Az eredmény fájl prefix-je.
    """

    # Lejtőszög értékek újraosztályozása
    _reclassify(
        wbt,
        rasters,
        file_prefix,
        "_slope",
        config.SLOPE_RECLASSIFICATION_RULES
    )


def reclassify_aspect(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        file_prefix: str,
) -> None:
    """ Újraosztályozza a kitettség értékeket tartalmazó rasztert.

    Újraosztályozza a kitettség értékeket tartalmazó rasztert 8
    különböző osztályba. Emellett az eredmény raszter elérési útját is
    eltárolja a raszterek elérési útját tároló dict-ben.

    -----

    Az új értékek:
        - [-10, 0) --> 0 (nincs kitettség)
        - [0, 22.5) --> 1 (észak)
        - [22.5, 67.5) --> 2 (északkelet)
        - [67.5, 112.5) --> 3 (kelet)
        - [112.5, 157.5) --> 4 (délkelet)
        - [157.5, 202.5) --> 5 (dél)
        - [202.5, 247.5) --> 6 (délnyugat)
        - [247.5, 292.5) --> 7 (nyugat)
        - [292.5, 337.5) --> 8 (északnyugat)
        - [337.5, 360.1) --> 1 (észak)

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        file_prefix: Az eredmény fájl prefix-je.
    """

    # Elsődleges újraosztályozás feltételei
    primary_reclassification = {
        0: "-10 - 0", # Nincs kitettség
        1: "0 - 22.5", # Észak
        2: "22.5 - 67.5", # Északkelet
        3: "67.5 - 112.5", # Kelet
        4: "112.5 - 157.5", # Délkelet
        5: "157.5 - 202.5", # Dél
        6: "202.5 - 247.5", # Délnyugat
        7: "247.5 - 292.5", # Nyugat
        8: "292.5 - 337.5", # Északnyugat
        9: "337.5 - 360.1" # Észak (szintén)
    }

    # Másodlagos újraosztályozás feltételei
    secondary_reclassification = {1: 9}

    # Kitettség értékek újraosztályozása
    _reclassify(
        wbt,
        rasters,
        file_prefix,
        "_aspect",
        primary_reclassification,
        secondary_reclassification
    )


def reclassify_flow_direction(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        file_prefix: str,
) -> None:
    """ Újraosztályozza a folyási irány értékeket tartalmazó rasztert.

    Újraosztályozza a folyási irány értékeket tartalmazó rasztert 8
    különböző osztályba. Emellett az eredmény raszter elérési útját is
    eltárolja a raszterek elérési útját tároló dict-ben.

    -----

    Az új értékek:
        - [-10, 0) --> 0 (nincs folyásirány)
        - [0, 22.5) --> 1 (észak)
        - [22.5, 67.5) --> 2 (északkelet)
        - [67.5, 112.5) --> 3 (kelet)
        - [112.5, 157.5) --> 4 (délkelet)
        - [157.5, 202.5) --> 5 (dél)
        - [202.5, 247.5) --> 6 (délnyugat)
        - [247.5, 292.5) --> 7 (nyugat)
        - [292.5, 337.5) --> 8 (északnyugat)
        - [337.5, 360.1) --> 1 (észak)

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        file_prefix: Az eredmény fájl prefix-je.
    """

    # Elsődleges újraosztályozás feltételei
    primary_reclassification = {
        0: "-10 - 0", # Nincs folyásirány
        1: "0 - 22.5",  # Észak
        2: "22.5 - 67.5",  # Északkelet
        3: "67.5 - 112.5",  # Kelet
        4: "112.5 - 157.5",  # Délkelet
        5: "157.5 - 202.5",  # Dél
        6: "202.5 - 247.5",  # Délnyugat
        7: "247.5 - 292.5",  # Nyugat
        8: "292.5 - 337.5",  # Északnyugat
        9: "337.5 - 360.1"  # Észak (szintén)
    }

    # Másodlagos újraosztályozás feltételei
    secondary_reclassification = {1: 9}

    # Kitettség értékek újraosztályozása
    _reclassify(
        wbt,
        rasters,
        file_prefix,
        "_flow_direction",
        primary_reclassification,
        secondary_reclassification
    )


def reclassify_flow_accumulation(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        file_prefix: str,
) -> None:
    """ Újraosztályozza a Flow Accumulation értékeket tartalmazó
    rasztert.

    Újraosztályozza a Flow Accumulation értékeket tartalmazó rasztert 8
    különböző osztályba. Emellett az eredmény raszter elérési útját is
    eltárolja a raszterek elérési útját tároló dict-ben.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        file_prefix: Az eredmény fájl prefix-je.
    """

    # Flow Accumulation értékek újraosztályozása
    _reclassify(
        wbt,
        rasters,
        file_prefix,
        "_flow_accumulation",
        config.FLOW_ACCUMULATION_RECLASSIFICATION_RULES
    )


def reclassify_topographic_wetness_index(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        file_prefix: str,
) -> None:
    """ Újraosztályozza a Topográfiai Nedvesség Index értékeket
    tartalmazó rasztert.

    Újraosztályozza a Topográfiai Nedvesség Index értékeket tartalmazó
    rasztert 8 különböző osztályba. Emellett az eredmény raszter
    elérési útját is eltárolja a raszterek elérési útját tároló
    dict-ben.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        file_prefix: Az eredmény fájl prefix-je.
    """

    # Topográfiai Nedevesség Index értékek újraosztályozása
    _reclassify(
        wbt,
        rasters,
        file_prefix,
        "_topographic_wetness_index",
        config.TOPOGRAPHIC_WETNESS_INDEX_RECLASSIFICATION_RULES
    )


def reclassify_sediment_transport_index(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        file_prefix: str,
) -> None:
    """ Újraosztályozza a Sediment Transport Index értékeket
    tartalmazó rasztert.

    Újraosztályozza a Sediment Transport Index értékeket tartalmazó
    rasztert 8 különböző osztályba. Emellett az eredmény raszter
    elérési útját is eltárolja a raszterek elérési útját tároló
    dict-ben.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        file_prefix: Az eredmény fájl prefix-je.
    """

    # Sediment Transport Index értékek újraosztályozása
    _reclassify(
        wbt,
        rasters,
        file_prefix,
        "_sediment_transport_index",
        config.SEDIMENT_TRANSPORT_INDEX_RECLASSIFICATION_RULES
    )


def reclassify_profile_curvature(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        file_prefix: str,
) -> None:
    """ Újraosztályozza a Profile Curvature értékeket tartalmazó
    rasztert.

    Újraosztályozza a Profile Curvature értékeket tartalmazó rasztert
    8 különböző osztályba. Emellett az eredmény raszter elérési útját
    is eltárolja a raszterek elérési útját tároló dict-ben.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        file_prefix: Az eredmény fájl prefix-je.
    """

    # Profile Curvature értékek újraosztályozása
    _reclassify(
        wbt,
        rasters,
        file_prefix,
        "_profile_curvature",
        config.PROFIL_CURVATURE_RECLASSIFICATION_RULES
    )


def reclassify_plan_curvature(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        file_prefix: str,
) -> None:
    """ Újraosztályozza a Plan Curvature értékeket tartalmazó rasztert.

    Újraosztályozza a Plan Curvature értékeket tartalmazó rasztert
    8 különböző osztályba. Emellett az eredmény raszter elérési útját
    is eltárolja a raszterek elérési útját tároló dict-ben.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        file_prefix: Az eredmény fájl prefix-je.
    """

    # Plan Curvature értékek újraosztályozása
    _reclassify(
        wbt,
        rasters,
        file_prefix,
        "_plan_curvature",
        config.PLAN_CURVATURE_RECLASSIFICATION_RULES
    )


def calculate_landform_class(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        file_prefix: str,
) -> None:
    """ Újraosztályozott görbületet tartalmazó raszter létrehozása

    Ez a függvény igazából nem végez újraosztályozást, hanem a két
    újraosztályozott görbületi raszter pixelértékeit adja össze.
    A Plan Curvature Reclassified értékei: 10, 20, 30.
    A Profile Curvature Reclassified értékei: 1, 2, 3.

    -----

    Egyenlet: Plan Curvature Reclassified + Profile Curvature
    Reclassified

    -----

    Az új értékek:
        - 11 (konvex - konvex) --> Csúcs / gerincváll
        - 12 (konvex - lineáris) --> Divergens egyenes lejtő
        - 13 (konvex - konkáv) --> Gerinctalp
        - 21 (lineáris - konvex) --> Egyenes lejtőváll
        - 22 (lineáris - lineáris) --> Tökéletesen egyenes lejtő
        - 23 (lineáris - konkáv) --> Egyenes lejtőalj
        - 31 (konkáv - konvex) --> Völgyváll
        - 32 (konkáv - lineáris) --> Völgyoldal
        - 33 (konkáv - konkáv) --> Völgytalp / meder

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        file_prefix: Az eredmény fájl prefix-je.
    """

    result_file_name = f"{file_prefix}_landform_class.tif"
    result_file_path = pathlib.Path(wbt.get_working_dir()).joinpath(result_file_name)

    # Raszter tárolása a dict-ben
    rasters['dem'][result_file_name.split(".")[0]] = result_file_path

    # Csak akkor végezzen számítást, ha még nem létezik a fájl
    if not result_file_path.exists():

        # Újraosztályozott raszter létrehozása raszterkalkulátorral
        wbt.raster_calculator(
            result_file_name,
            f'"{file_prefix}_plan_curvature_reclassified.tif" + '
            f'"{file_prefix}_profile_curvature_reclassified.tif"'
        )


def reclassify_time_in_daylight(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        file_prefix: str,
) -> None:
    """ Napsütéses idő hosszát tartalmazó raszter újraosztályozása.

    Újraosztályozza a napsütéses idő hosszát tartalmazó rasztert.
    Emellett az eredmény raszter elérési útját el is tárolja a
    raszterek elérési útját tároló dict-ben.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        file_prefix: Az eredmény fájl prefix-je.
    """

    # Napsütéses idő hosszát tartalmazó raszter újraosztályozása
    _reclassify(
        wbt,
        rasters,
        file_prefix,
        "_time_in_daylight",
        config.TIME_IN_DAYLIGHT_RECLASSIFICATION_RULES
    )


def reclassify_potential_solar_radiation(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        file_prefix: str,
) -> None:
    """ Potenciális napsugrázás értékeket tartalmazó raszter
    újraosztályozása.

    Újraosztályozza a potenciális napsugárzás értékeket tartalmazó
    rasztert. Emellett az eredmény raszter elérési útját el is tárolja
    a raszterek elérési útját tároló dict-ben.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        file_prefix: Az eredmény fájl prefix-je.
    """

    # Potenciális napsugárzást tartalmazó raszter újraosztályozása
    _reclassify(
        wbt,
        rasters,
        file_prefix,
        "_potential_solar_radiation",
        config.POTENTIAL_SOLAR_RADIATION_RECLASSIFICATION_RULES
    )


def reclassify_topographic_position_index(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        file_prefix: str,
) -> None:
    """ Topográfiai Helyzeti Index értékeket tartalmazó raszter
    újraosztályozása.

    Újraosztályozza a Topográfiai Helyzeti Index értékeket tartalmazó
    rasztert. Emellett az eredmény raszter elérési útját el is tárolja
    a raszterek elérési útját tároló dict-ben.

    -----

    Új értékek:
        - [-1.0, -0.7) --> 1 (mély völgyek, kanyonok)
        - [-0.7, -0.3) --> 2 (hegyi völgyek / lejtő közepém húzódó
            völgyek)
        - [-0.3, 0.3) --> 3 (síkság / konstans lejtőszög)
        - [0.3, 0.7) --> 4 (emelkedő lejtőszög / hegyváll)
        - [0.7, 1.0) --> 5 (hegygerinc / hegycsúcs)

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        file_prefix: Az eredmény fájl prefix-je.
    """

    # Elsődleges újraosztályozás feltételei
    primary_reclassification = {
        1: "-1.0 - -0.7", # Mély völgyek, kanyonok
        2: "-0.7 - -0.3", # Hegyi völgyek vagy lejtő közepén húzódó völgyek
        3: "-0.3 - 0.3", # Síkság vagy konstans lejtőszög
        4: "0.3 - 0.7", # Emelkedő lejtőszög vagy hegyváll
        5: "0.7 - 1.1" # Hegygerinc vagy hegycsúcs
    }

    # Potenciális napsugárzást tartalmazó raszter újraosztályozása
    _reclassify(
        wbt,
        rasters,
        file_prefix,
        "_topographic_position_index",
        primary_reclassification
    )


def reclassify_roughness(
        wbt: whitebox.WhiteboxTools,
        rasters: dict[str, dict[str, pathlib.Path]],
        file_prefix: str,
) -> None:
    """ Érdesség értékeket tartalmazó raszter újraosztályozása.

    Újraosztályozza az érdesség értékeket tartalmazó rasztert.
    Emellett az eredmény raszter elérési útját el is tárolja a
    raszterek elérési útját tároló dict-ben.

    Args:
        wbt: A WhiteboxTools objektum.
        rasters: A raszter eléréseket tárológ dict.
        file_prefix: Az eredmény fájl prefix-je.
    """

    # Potenciális napsugárzást tartalmazó raszter újraosztályozása
    _reclassify(
        wbt,
        rasters,
        file_prefix,
        "_roughness",
        config.ROUGHNESS_RECLASSIFICATION_RULES
    )