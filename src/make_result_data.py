""" Az eredmény adat kialakításának folyamatát valósítja meg. Kezeli a
mezóneveket. Összevonja a dűlőket magasabb szinteken (pl. település,
borvidék). Vegül pedig egy GeoPackage-be elmenti a GeoDataFrame-ek
tartalmát.
"""


import typing
import pathlib

import geopandas as gpd

import config
from src import prepare_vector_data
from src import join_rasters_to_polygons
from src import utils


def handle_field_names(
        gdfs: dict[str, gpd.GeoDataFrame],
        test_run: bool
) -> None:
    """ Sorba rendezi a mező neveket, majd átnevezi őket.

    A dűlőket tartalmazó GeoDataFrame mezőit (oszlopait) sorba rendezi
    logika szerint, majd átnevezi őket egy meghatározott szabály
    szerint.

    Args:
        gdfs: A GeoDataFrame-ket tartalmazó dict.
        test_run: Teszt futtatáshoz használt-e a függvény?
    """

    if not test_run:
        # A "stopper" indítása
        start = utils.run_time.start_time(
            "A make_result_data.handle_field_names(gdfs) függvény futása "
            "elindult.",
            2
        )

    vineyards = gdfs["vineyards"]

    # Régi és új mező nevek egy dict-ben
    field_names = config.FIELD_NAMES.copy()

    # Mezők sorbarendezése még a régi nevek alapján
    columns = list(vineyards.columns)
    old_names_sorted = list(field_names.keys())
    names_not_found = []
    for name in old_names_sorted:
        if name not in columns:
            names_not_found.append(name)
    for name in names_not_found:
        old_names_sorted.remove(name)
    vineyards = vineyards[old_names_sorted]

    # A szabályban nem fontos mezők törlése
    for old_name in field_names.keys():
        if field_names[old_name] == "":
            names_not_found.append(old_name)
    for name in names_not_found:
        if name in field_names.keys():
            del field_names[name]

    # Mezők átnevezése a dict alapján
    vineyards = vineyards.rename(columns=field_names)

    # Dűlőket tartalmazó GeoDataFrame visszavezetése a dict-be
    gdfs["vineyards"] = vineyards

    if not test_run:
        # A "stopper" leállítása
        utils.run_time.end_time(
            "A make_result_data.handle_field_names(gdfs) függvény futása "
            "befejeződött.",
            start,
            2
        )


def dissolve_data(
        gdfs: dict[str, gpd.GeoDataFrame],
        rasters: dict[str, dict[str, pathlib.Path]],
        level: typing.Literal["settlement", "wine_district", "wine_region",
               "country"]| str,
        result_gdfs: dict[str, gpd.GeoDataFrame],
        test_run: bool
) -> None:
    """ Összevonja a dűlőket a megadott szintre.

    Összevonja a dűlőket a megadott szintre (település, borvidék,
    borrégió), majd a dűlők adatait is összegzi ehhez mérten.

    Args:
        gdfs: A GeoDataFrame-ket tároló dict.
        rasters: A raszterek elérési útját tároló dict.
        level: Az összevonás szintje.
        result_gdfs: Az összevonás eredményeként létre jövő
            GeoDataFrame-et tároló dict.
        test_run: Teszt futtatáshoz használt-e a függvény?
    """

    if not test_run:
        # A "stopper" indítása
        start = utils.run_time.start_time(
            f"A make_result_data.dissolve_data(gdfs, rasters, {level}) "
            "függvény futása elindult.",
            2
        )

    # Dűlőket tartalmazó GeoDataFrame
    vineyards = gdfs["vineyards"].copy()

    # Az összevonás szintjének megfelelő név mező
    name_field = utils.fields.get_name_field_for_level(
        level,
        list(gdfs.keys())
    )

    # Dűlők száma az adott összevonási szint elemei esetében
    if name_field:
        number_of_vineyards = vineyards.groupby(by=name_field).size()
    else:
        number_of_vineyards = len(vineyards)

    # Dűlők összevonása szintnek megfelelően
    if level != "all":
        vineyards = vineyards.dissolve(
            by=name_field,
            as_index=False
        )
        vineyards["number_of_vineyards"] = number_of_vineyards.values
        vineyards = utils.fields.sort_level_data_by_name(vineyards, name_field)
    else:
        vineyards = vineyards.dissolve()
        vineyards['number_of_vineyards'] = number_of_vineyards

    vineyards = vineyards.reset_index(drop=True)
    vineyards["id"] = vineyards.index

    # Dűlő területek újra számítása
    vineyards["area_m2"] = vineyards.area
    vineyards["area_ha"] = vineyards.area / 10_000

    settlements_name_field = utils.fields.get_name_field_for_level(
        "settlement",
        list(gdfs.keys())
    )
    wine_districts_name_field = utils.fields.get_name_field_for_level(
        "wine_district",
        list(gdfs.keys())
    )
    wine_regions_name_field = utils.fields.get_name_field_for_level(
        "wine_region",
        list(gdfs.keys())
    )

    # Oszlopok szűrése az újraszámítás előkészítéséhez
    vineyards = utils.fields.filter_fields_for_dissolve(
        vineyards,
        settlements_name_field,
        wine_districts_name_field,
        wine_regions_name_field
    )

    # Talaj adatok újra számítása a megfelelő szinthez
    vineyards = prepare_vector_data.join_soils_preperties_to_vineyards(
        vineyards,
        gdfs["soils"],
        inner_function=True
    )

    # Ideiglenes dict a GeoDataFrame-eknek
    temp_gdfs = {
        "vineyards": vineyards
    }

    # Raszterek összekapcsolása a poligonokkal
    join_rasters_to_polygons.process(
        temp_gdfs,
        rasters,
        inner_function=True
    )

    # Mező nevek kezelése (sorbarendezés, törlés)
    vineyards = temp_gdfs["vineyards"]
    vineyards = utils.fields.handle_field_names_in_level_data(
        vineyards,
        level,
        list(gdfs.keys())
    )

    # A szint GeoDataFrame-jének eltárolása a dict-ben
    level = level if level == "all" else f"{level}s"
    result_gdfs[level] = vineyards

    if not test_run:
        # A "stopper" leállítása
        utils.run_time.end_time(
            f"A make_result_data.dissolve_data(gdfs, rasters, {level}) "
            "függvény futása befejeződött.",
            start,
            2
        )


def save_gdfs(
        result_gdfs: dict[str, gpd.GeoDataFrame],
        test_run: bool
):
    """ Lementi egy GeoPackage-be a dict-ben tárolt GeoDataFrame-ket.

    Bejárja a dict-et, majd a benne található GeoDataFrame-ket lementi
    egy GeoPackage-be. A GeoPackage rétegeinek neve a dict kulcsai
    lesznek.

    Args:
        result_gdfs: Az eredményként mentendő GeoDataFrame-ke ttároló
            dict.
        test_run: Teszt futtatáshoz használt-e a függvény?
    """

    if not test_run:
        # A "stopper" indítása
        start = utils.run_time.start_time(
            f"A make_result_data.save_gdfs(result_gdfs) függvény futása "
            f"elindult.",
            2
        )

    # Az eredmény fájl elérési útja és a mappák létrehozása, ha még nem létezik
    result_file_path = pathlib.Path(
        f"{config.RESULT_VECTOR_FILES_DIRECTORY_PATH}"
    ).joinpath("vineyards_analytics.gpkg").absolute()

    utils.file_handling.create_folders(result_file_path)

    for layer in result_gdfs.keys():

        # GeoDataFrame beolvasása a dict-ből és fájlba mentése
        gdf = result_gdfs[layer]

        # Mezők sorba rendezése a config-ban megadottak szerint
        field_order = [
            new if new else old
            for old, new in config.FIELD_NAMES.items()
            if old in gdf.columns or new in gdf.columns]
        gdf = gdf[field_order]

        # Számértékek kerekítése
        numerical_fields = gdf.select_dtypes(include="number").columns
        gdf[numerical_fields] = gdf[numerical_fields].round(3)

        # GeoDataFrame fájlba mentése
        gdf.to_file(result_file_path, layer=layer)

        # Módosított GeoDataFrame visszatöltése
        result_gdfs[layer] = gdf

    if not test_run:
        # A "stopper" leállítása
        utils.run_time.end_time(
            f"A make_result_data.save_gdfs(gdfs) függvény futása befejezése.",
            start,
            2
        )


# ===============================================
# EREDMÉNY FÁJLOK ELKÉSZÍTÉSÉNEK FOLYAMATA
# ===============================================

def process(
        gdfs: dict[str, gpd.GeoDataFrame],
        rasters: dict[str, dict[str, pathlib.Path]],
        test_run: bool=False
) -> None:
    """ Az eredmény fájl készítésének, majd mentésének folyamatát
    hajtja végre.

    Kezeli a dűlőket tartalmazó GeoDataFrame (majd GeoDataFrame-ek)
    mezőit. Majd összevonja a dűlőket különböző szintek alapján. Az
    eredmény GeoDataFrame-ket el is menti egy GeoPackage-be. Majd az
    egyes űlőkhöz és szintnek megfelelő dűlőhalmazhoz külön CSV
    állományt hoz létre, amely a domborzati pixelek értékeit tárolja.

    Args:
        gdfs: A GeoDataFrame-ket tároló dict.
        rasters: A raszterek elérési útjait tároló dict.
        test_run: Teszt futtatáshoz használt-e a függvény?
    """

    if not test_run:
        # A "stopper" indítása
        start = utils.run_time.start_time(
            "A make_result_data.process(gdfs) függvény futása "
            "elindult.",
            1
        )

    # A dűlőket tartalmazó GeoDataFrame mezőneveinek kezelése
    handle_field_names(
        gdfs,
        test_run=test_run
    )

    result_gdfs = {"vineyards": gdfs["vineyards"]}

    # Dűlők összegzése a megefelelő szinthez
    for level in ["settlement", "wine_district", "wine_region", "all"]:

        # Ha nincs az eredmény adatok között csak ugorja át
        if level != "all" and f"{level}s" not in gdfs.keys():
            continue

        dissolve_data(
            gdfs,
            rasters,
            level,
            result_gdfs,
            test_run=test_run
        )

    # GeoDataFrame-ek tartalmának mentése fájlba
    save_gdfs(
        result_gdfs,
        test_run=test_run
    )

    if not test_run:
        # A "stopper" leállítása
        utils.run_time.end_time(
            "A make_result_data.process(gdfs) függvény futása "
            "befejeződött.",
            start,
            1
        )