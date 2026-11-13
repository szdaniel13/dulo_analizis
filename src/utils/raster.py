""" A rasteres adatok kezeléséhez nyújt segédfüggvényeket. """


import pathlib
import typing

import rasterio
import pyproj
import pandas as pd
import geopandas as gpd
import rasterstats
import numpy as np

import config
from src import utils


def raster_to_eov(
        raster_path: pathlib.Path,
        data_type: typing.Literal["dem", "meteorological"]
) -> pathlib.Path:
    """ A raszter vetületét átváltja EOV-ba.

    A raszter vetületét átváltja EOV-ba és elmenti azt egy új fájlban.

    Args:
        raster_path: A raszter elérési útja.
        data_type: Az adattípusa (DEM vagy meteorológiai

    Returns:
        Az új raszter elérési útja.
    """

    from rasterio.warp import (
        calculate_default_transform,
        reproject,
        Resampling
    )


    # Az eredmény fájl elérés
    if data_type == "dem":
        dst_path = (
            pathlib.Path(config.RESULT_DEM_FILES_DIRECTORY_PATH)
            .joinpath(raster_path.name).absolute()
        )
    else:
        dst_path = (
            pathlib.Path(config.RESULT_METEOROLOGICAL_FILES_DIRECTORY_PATH)
            .joinpath(raster_path.name).absolute()
        )

    # Ha már korábbi futtatás által létre lett hozva
    if dst_path.exists():
        return dst_path

    # Ha még nem léteznek a mappák hozza létre
    utils.file_handling.create_folders(dst_path)

    # Forrás raszter
    with rasterio.open(raster_path) as src:

        # Az eredeti raszter "geometriai" tulajdonságai a későbbi számításokhoz
        transform, width, height = calculate_default_transform(
            src.crs,
            pyproj.CRS(23700),
            src.width,
            src.height,
            *src.bounds
        )

        # Pixelek mérete a számításokhoz
        x_pixel_size = transform.a
        y_pixel_size = -transform.e

        # Hasonló legyen a két pixel oldal hossza
        new_pixel_size = min(x_pixel_size, y_pixel_size)

        # A raszter geometriai tulajdonságainak újra számítása
        transform, width, height = calculate_default_transform(
            src.crs,
            pyproj.CRS(23700),
            src.width,
            src.height,
            *src.bounds,
            resolution=new_pixel_size
        )

        # Metaadatok frissítése az új raszterhálóhoz
        metadata = src.meta.copy()
        metadata.update({
            "crs": "EPSG:23700",
            "transform": transform,
            "width": width,
            "height": height
        })

        # Eredmény raszter
        with rasterio.open(dst_path, "w", **metadata) as dst:

            # Az egyes sávok vetületváltása
            for band_num in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, band_num),
                    destination=rasterio.band(dst, band_num),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=pyproj.CRS(23700),
                    resampling=Resampling.bilinear
                )

    return dst_path


def get_raster_resolution(raster_path: pathlib.Path) -> float:
    """ Megadja a raszter felbontását méterben.

    Meghatározza a megadott elérési úton található raszter térbeli
    felbontását méterben.

    Args:
        raster_path: A raszter elérési útja.

    Returns:
        A raszter felbontása méterben.
    """

    with rasterio.open(str(raster_path)) as src:
        return src.transform.a


def get_raster_center_in_wgs84(raster_path: pathlib.Path) \
    -> tuple[float, float]:
    """ Kiszámítja a raszter középponjtának koordinátáit WGS84-ben.

    A megadott elérési úton található raszter középpontjának
    koordinátáit adja meg fokban (WGS84).

    Args:
        raster_path: A raszter elérési útja.

    Returns:
        1. A középpont földrajzi szélességének koordinátája.
        2. A középpont földrajzi hosszúságának koordinátája.
    """

    from rasterio.warp import transform


    with rasterio.open(raster_path) as src:

        # A raszter határai --> középpont koordinátái
        bounds = src.bounds
        center_x = (bounds.left + bounds.right) / 2
        center_y = (bounds.bottom + bounds.top) / 2

        # Középpont koordinátái WGS84-ben
        lon_list, lat_list = transform(
            src.crs,
            pyproj.CRS("EPSG:4326"),
            [center_x],
            [center_y]
        )

        return lat_list[0], lon_list[0]


def zonal_statistics(
        vineyards: gpd.GeoDataFrame,
        raster_file_path: pathlib.Path,
        field_name_prefix: str
) -> gpd.GeoDataFrame:
    """ Zóna statisztikát készít az egyes dűlőkhöz a megadott raszter
    alapján.

    Zóna statisztikát készít a megadott raszterből az egyes dűlőkhöz.
    A következő statisztikákat számolja ki: minimum, maximum, átlag,
    medián, szórás.

    Args:
        vineyards: A dűlőket tartalmazó GeoDataFrame.
        raster_file_path: A raszter elérési útja.
        field_name_prefix: A létrehozandó mezők nevének előtagja.

    Returns:
        A dűlőket tartalmazó GeoDataFrame a statsztikákat tartalmazó
            mezőkkel kiegészítve.
    """

    # Zóna statisztikák kiszámítása
    stats_values = rasterstats.zonal_stats(
        vineyards,
        raster_file_path,
        stats=["min", "max", "mean", "median", "std"]
    )

    try:
        # Zóna statisztikák eltárolása
        vineyards[f"{field_name_prefix}_minimum"] = \
            [round(s["min"], 3) for s in stats_values]
        vineyards[f"{field_name_prefix}_maximum"] = \
            [round(s["max"], 3) for s in stats_values]
        vineyards[f"{field_name_prefix}_mean"] = \
            [round(s["mean"], 3) for s in stats_values]
        vineyards[f"{field_name_prefix}_median"] = \
            [round(s["median"], 3) for s in stats_values]
        vineyards[f"{field_name_prefix}_standard_deviation"] = \
            [round(s["std"], 3) for s in stats_values]

    except TypeError:
        raise ValueError(
            "Van olyan dűlő, amely nem metszi a domborzatmodellt."
        )

    return vineyards


def join_reclassified_raster_on_polygons(
        vineyards: gpd.GeoDataFrame,
        raster_file_path: pathlib.Path,
        field_name_prefix: str
) -> gpd.GeoDataFrame:
    """ Az újraosztályozott rasztereket kapcsolja az egyes dűlőkhöz.

    Az újraosztályozott rasztereket kapcsolja az egyes dűlőkhöz úgy,
    hogy az egyes kategóriákhoz tartozó területi arányokat kapcsolja
    a dűlőkhöz.

    Args:
        vineyards: A dűlőket tartalmazó GeoDataFrame.
        raster_file_path: A raszter elérési útja.
        field_name_prefix: Az létrehozandó mezők nevének előtagja.

    Returns:
        A dűlőket tartalmazó GeoDataFrame az értékek összekapcsolása
            után.
    """

    # Zóna statisztika kategóriánként
    stats_values = rasterstats.zonal_stats(
        vineyards,
        raster_file_path,
        categorical=True
    )

    # Statisztikákat tartalmazó DataFrame
    stats_values = pd.DataFrame(stats_values)

    # Az összes pixel száma dűlőnként
    total_pixels = stats_values.sum(axis=1)

    for column in stats_values.columns:

        # Kategóriához tartozó pixel aránya az összes pixelhez
        stats_values[column] = (stats_values[column] / total_pixels).round(3)

        # Mezők (vagy oszlopok) átnevezése
        stats_values = stats_values.rename(
            columns={column: f"{field_name_prefix}_{int(column)}"}
        )

    # Statisztika vissza csatolása a geometriákhoz
    vineyards = vineyards.join(stats_values)

    return vineyards


def _raster_grid_to_gdf(
        raster_file_path: pathlib.Path,
        field_name: str
) -> gpd.GeoDataFrame:
    """ GeoDataFrame-et készít a raszterhálóból.

    A raszterhálóból GeoDataFrame-et készít, tehát az egyes pixelek
    négyszög alakú poligonként fognak megjelenni a GeoDataFrame
    geometriái között. Természetesen a létrejövő GeoDataFrame-ben
    lesz egy meező is, amely a pixelértékeket tárolja.

    Args:
        raster_file_path: A raszter fájl elérési útja.
        field_name: A mező neve, ameéyhez majd a pixelértékek fognak
            tartozni.

    Returns:
        A raszterhálót tartalmazó GeoDataFrame.
    """

    from shapely.geometry import box

    with rasterio.open(raster_file_path) as src_raster:

        # A raszter geometriai információi
        transform = src_raster.transform
        height, width = src_raster.height, src_raster.width
        crs = src_raster.crs

        # Sorok és oszlopok indexei
        rows, cols = np.meshgrid(
            np.arange(height),
            np.arange(width),
            indexing="ij"
        )

        # Cellák középpontjai
        xs, ys = rasterio.transform.xy(
            transform,
            rows,
            cols
        )

        # Raszterhálóból poligonok készítése
        xs, ys = np.array(xs).flatten(), np.array(ys).flatten()
        xres, yres = transform.a, abs(transform.e)
        polygons = [
            box(x - xres / 2, y - yres / 2, x + xres / 2, y + yres / 2)
            for x, y in zip(xs, ys)
        ]
        geometry = gpd.GeoSeries(polygons, crs=crs)

        # Pixel értékek
        values = src_raster.read(1).flatten()

        # GeoDataFrame létrehozása a rácshálóból
        raster_grid = gpd.GeoDataFrame(
            {field_name: values},
            geometry=geometry,
            crs=crs
        )

    return raster_grid


def join_meteorological_data_on_polygons(
        vineyards: gpd.GeoDataFrame,
        raster_file_path: pathlib.Path,
        field_name: str
) -> gpd.GeoDataFrame:
    """ A megadott meteorológiai adatokat tartalmazó rasztert kapcsolja
    a dűlőkhöz.

    A megadott meteorológiai adatokat tartalmazó rasztert kapcsolja
    a dűlőkhöz. A kapcsolás eredményeként a dűlőkhöz a pixelértékek
    területi átlaga lesz átadva.

    Args:
        vineyards: A dűlőket tartalmazó GeoDataFrame.
        raster_file_path: A raszter fájl elérési útja.
        field_name: A mező neve, amely a kapcsolt értékeket fogja
            tárolni.

    Returns:
        A dűlőket tartalmazó GeoDataFrame az adatok kiegészítése után.
    """

    # Raszterháló GeoDataFrame-ben
    raster_grid = _raster_grid_to_gdf(
        raster_file_path,
        field_name
    )

    # Raszterháló metszése a dűlőkket + attribútumok összekapcsolása
    grid_clipped = gpd.overlay(
        raster_grid,
        vineyards,
    )

    # Vágott négyzetek területei
    grid_clipped["clipped_area"] = grid_clipped.geometry.area

    # Területtel súlyozott értékek
    grid_clipped["weighted_value"] = (
            grid_clipped[field_name] * grid_clipped["clipped_area"]
    )

    # Raszterháló csoportosítása
    grouped = grid_clipped.groupby("id").agg(
        total_clipped_area=("clipped_area", "sum"),
        total_weighted_value=("weighted_value", "sum")
    ).reset_index()

    # Terület átlag számítás
    grouped[field_name] = (
            grouped["total_weighted_value"] / grouped["total_clipped_area"]
    ).round(2)

    # Az eredmények visszakapcsolása a dűlőkhöz
    vineyards = vineyards.merge(
        grouped[["id", field_name]],
        on="id",
        how="left"
    )

    # A hiányzó értékek pótlása 0-val
    vineyards[field_name] = vineyards[field_name].fillna(0)

    return vineyards