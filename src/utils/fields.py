""" Függvényeket tartalmaz a vektoros adatok mezők alapján történő
kezeléséhez.
"""


import typing

import geopandas as gpd
import pandas as pd

import config


def get_name_field_for_level(
        level: typing.Literal["vineyard", "settlement", "wine_district",
                              "wine_region"],
        avaible_layers: list[str]
) -> str:
    """ Meghatározza az elemek nevét tarttalmazó mező nevét az adott
    összevonási szintnek megfelelően.

    Meghatározza annak a mezőnek a nevét, amely az adott szintű
    összevonás esetén az elemek nevét (települések neve, borvidékek
    neve, borrégiók neve) tartalmazza.

    Args:
        level: Az összevonás szintje.
        avaible_layers: Az elérhető rétegek nevei.

    Returns:
        Annak a mezőnekv a neve, amely a szintnek megfelelő elemek
            nevét tartalmazza.
    """

    if level == "vineyard":
        return (
            config.FIELD_NAMES["name"]
            if config.FIELD_NAMES["name"]
            else "name"
        )

    elif level == "settlement":
        if "settlements" in avaible_layers:
            return (
                config.FIELD_NAMES["settlement"]
                if config.FIELD_NAMES["settlement"]
                else "settlement"
            )

    elif level == "wine_district":
        if "wine_districts" in avaible_layers:
            return (
                config.FIELD_NAMES["wine_district"]
                if config.FIELD_NAMES["wine_district"]
                else "wine_district"
            )

    elif level == "wine_region":
        if "wine_regions" in avaible_layers:
            return (
                config.FIELD_NAMES["wine_region"]
                if config.FIELD_NAMES["wine_region"]
                else "wine_region"
            )


def filter_fields_for_dissolve(
        vineyards: gpd.GeoDataFrame,
        settlements_name_field: str | None,
        wine_districts_name_field: str | None,
        wine_regions_name_field: str | None
) -> gpd.GeoDataFrame:
    """ Csak a szükséges oszlopokat hagyja meg az összevonás utáni
    újraszámítások miatt.

    A szintnek megfelelően összevont dűlőben csak a szükséges alap
    adatokat hagyja meg mezőként és a többi mezőt, amely az
    újraszámítások során létrejön kitörli.

    Args:
        vineyards: A dűlőket az összevonás után tartalmazó
            GeoDataFrame.
        settlements_name_field: A települések neveit tartalmazó mező
            neve.
        wine_districts_name_field: A borvidékek neveit tartalmazó mező
            neve.
        wine_regions_name_field: A borrégiók neveit tartalmaazó mező
            neve.

    Returns:
        Az öszevont dűlőket tartalmazó GeoDataFrame a felesleges mezők
            törlése után.
    """

    fields_to_keep = ["id", "name", "area_m2", "area_ha",
                      "number_of_vineyards", "geometry"]

    if settlements_name_field:
        fields_to_keep.append(settlements_name_field)
    if wine_districts_name_field:
        fields_to_keep.append(wine_districts_name_field)
    if wine_regions_name_field:
        fields_to_keep.append(wine_regions_name_field)

    vineyards = vineyards[fields_to_keep]

    return vineyards


def sort_level_data_by_name(
        vineyards: gpd.GeoDataFrame,
        name_field:  str
) -> gpd.GeoDataFrame:
    """ Sorba rendezi az adott szint alapján összevont dűlőket név
    alapján.

    Sorba rendezi a megadott szint alapján összevont dűlőket település,
    borvidék vagy borrégió neve alapján.

    Args:
        vineyards: A dűlőket tartalmazó GeoDataFrame.
        name_field: A dűlők összevonási szintjének megfelelő mezőnév

    Returns:
        A GeoDataFrame a sorbarendezés után.
    """

    # Sorbarendezés indexei
    vineyards_sort_index = (
        vineyards[name_field]
        .str.normalize("NFD")
        .sort_values()
        .reset_index()
    )

    # Indexek kinyerése
    vineyards["index"] = vineyards.index
    vineyards = vineyards.drop(columns=[name_field])

    # Indexek és a sorba rendezett GeoDataFrame összevonása
    vineyards = gpd.GeoDataFrame(
        pd.merge(vineyards_sort_index, vineyards, how="inner", on="index"),
        crs=vineyards.crs
    )
    vineyards = vineyards.drop(columns=["index"])

    return vineyards


def drop_fields_for_level_data(
        vineyards: gpd.GeoDataFrame,
        level: str,
        avaible_layers: list[str]
) -> gpd.GeoDataFrame:

    # Név mezők kinyerése szintnek megfelelően
    vineyards_name_field = get_name_field_for_level(
        "vineyard",
        avaible_layers
    )
    settlements_name_field = get_name_field_for_level(
        "settlement",
        avaible_layers
    )
    wine_districts_name_field = get_name_field_for_level(
        "wine_district",
        avaible_layers
    )
    wine_regions_name_field = get_name_field_for_level(
        "wine_region",
        avaible_layers
    )

    # Eldobandó mező nevek kigyűjtése
    fields_to_drop = [vineyards_name_field]

    if (level in ["wine_district", "wine_region", "all"] and
            settlements_name_field):
        fields_to_drop.append(settlements_name_field)

    if level in ["wine_region", "all"] and wine_districts_name_field:
        fields_to_drop.append(wine_districts_name_field)

    if level == "all" and wine_regions_name_field:
        fields_to_drop.append(wine_regions_name_field)

    if level == "settlement":
        vineyards = vineyards.drop(
            columns=fields_to_drop
        )

    elif level == "wine_district":
        vineyards = vineyards.drop(
            columns=fields_to_drop
        )

    elif level == "wine_region":
        vineyards = vineyards.drop(
            columns=fields_to_drop
        )

    else:
        vineyards = vineyards.drop(
            columns=fields_to_drop
        )

    return vineyards


def handle_field_names_in_level_data(
        vineyards: gpd.GeoDataFrame,
        level: str,
        avaible_layers: list[str]
) -> gpd.GeoDataFrame:
    """ Kezeli a mező neveket a megadott szint alapján összevont
    GeoDataFrame-ben.

    Szűri, majd átnevezi a mezőket az adott szintnek megfelelően a
    dűlőket tároló GeoDataFrame-ben.

    Args:
        vineyards: A dűlőket tartalmazó GeoDataFrame.
        level: A dűlők összevonási szintje.
        avaible_layers: Az elérhető rétegek nevei.
    """

    vineyards_name_field = get_name_field_for_level(
        "vineyard",
        avaible_layers
    )
    settlements_name_field = get_name_field_for_level(
        "settlement",
        avaible_layers
    )
    wine_districts_name_field = get_name_field_for_level(
        "wine_district",
        avaible_layers
    )
    wine_regions_name_field = get_name_field_for_level(
        "wine_region",
        avaible_layers
    )

    # Felesleges mezők törlése
    vineyards = drop_fields_for_level_data(
        vineyards,
        level,
        avaible_layers
    )

    field_names = config.FIELD_NAMES.copy()
    filterd_field_names = {}
    for old, new in field_names.items():
        if new not in ["", vineyards_name_field, settlements_name_field,
                       wine_districts_name_field, wine_regions_name_field]:
            filterd_field_names[old] = new

    vineyards = vineyards.rename(columns=filterd_field_names)

    return vineyards