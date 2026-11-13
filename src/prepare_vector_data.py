""" A vektoros adatok előkészítésének folyamatát valósítja meg.
Kiegészíti a dűlők adatait, valamint a nevük alapján ábécé sorrendbe
rendezi őket. Térbeli összekapcsolással a települések, borvidékek és
borrégiók neveit a dűlőkhöz kapcsolja. Végül a kategorikus talaj adatok
területi arányait hozzákapcsolja a dűlőkhöz.
"""


import geopandas as gpd
import pandas as pd

from src import utils


def supplement_vineyard_data(
        vineyards: gpd.GeoDataFrame,
        test_run: bool
) -> gpd.GeoDataFrame:
    """ Kiegészíti a dűlők alapadatait.

    Kiegészíti a dűlők alapadatait az azonosítóval ('id'), a
    területükkel m2-ben ('area_m2') és a területükkel hektárban
    ('area_ha').

    Args:
        vineyards: A dűlőket tartalmazó GeoDataFrame.
        test_run: Teszt futtatáshoz használt-e a függvény?

    Returns:
        A dűlőket tartalmazó GeoDataFrame a kiegészítés után.
    """

    if not test_run:
        # A "stopper" indítása
        start = utils.run_time.start_time(
            f"A prepare_vector_data.supplement_vineyard_data(vineyards) "
            f"függvény futása elindult.",
            2
        )

    # Sorbarendezés indexei
    vineyards_sort_index = (
        vineyards["name"]
        .str.normalize("NFD")
        .sort_values()
        .reset_index()
    )

    # Dűlők indexeinek kinyerése
    vineyards["index"] = vineyards.index
    vineyards = vineyards.drop(columns=["name"])

    # Indexek összekapcsolása a GeoDataFrame-mel
    vineyards = gpd.GeoDataFrame(
        pd.merge(vineyards_sort_index, vineyards, how="inner", on="index"),
        crs=vineyards.crs
    )
    vineyards = vineyards.drop(columns=["index"])

    # Az "id", az "area_m2" és az "area_ha" mezők létrehozása
    vineyards["id"] = vineyards.index
    vineyards["area_m2"] = vineyards.area
    vineyards["area_ha"] = vineyards.area / 10_000

    if not test_run:
        # A "stopper" leállítása
        utils.run_time.end_time(
            f"A prepare_vector_data.supplement_vineyard_data(vineyards) "
            f"függvény futása bejeződött.",
            start,
            2
        )

    return vineyards


def spatial_join(
        vineyards: gpd.GeoDataFrame,
        other_gdf: gpd.GeoDataFrame,
        other_gdf_name_col: str,
        test_run: bool
) -> gpd.GeoDataFrame:
    """ Térbeli összekapcsolás a dűlők és a hozzákapcsolandó
    GeoDataFrame között.

    Összekapcsolja a dűlőket tartalmazó GeoDataFrame-et a megadott
    GeoDataFrame-mel, majd kezeli azt az esetet is, ha több név lenne
    egy dűlőhöz kapcsolva a mások GeoDataFrame-ből.

    Args:
        vineyards: A dúlőket tartalmazó GeoDataFrame.
        other_gdf: A dűlőkkel összekapcsolandó GeoDataFrame.
        other_gdf_name_col: Az összekapcsolandó GeoDataFrame-ben a
            neveket tartalmazó oszlop neve.
        test_run: Teszt futtatáshoz használt-e a függvény?

    Returns:
        A dűlőket tartalmazó GeoDataFrame az összekapcsolás után.
    """

    if not test_run:
        # A "stopper" indítása
        start = utils.run_time.start_time(
            f"A prepare_vector_data.spatial_join(vineyards, other_gdf, "
            f"{other_gdf_name_col}) függvény futása elindult.",
            2
        )

    # Az másik GeoDataFrame név és geometry oszlopa legyen csak figyelembe véve
    other_gdf = other_gdf[[other_gdf_name_col, "geometry"]]

    # Később a geometriák visszaalakításához kell
    original_geoms = vineyards.geometry

    # Centroid geometria alkalmazása
    vineyards = vineyards.set_geometry(vineyards.geometry.centroid)

    # GeoDataFrame-ek térbeli összekapcsolása
    vineyards = gpd.sjoin(
        vineyards,
        other_gdf,
        how="left"
    )

    # Indexek kezelése a későbbi problémmák megelőzőse érdekében
    vineyards = vineyards.reset_index(drop=True)
    vineyards = vineyards.drop(columns=["index_right"])

    # Ha több név lett hozzá kapcsolva egy-egy dűlőhöz
    if len(vineyards) > len(original_geoms):

        # A nevek összevonva legyenek 1 sorban az adott dűlőhöz
        grouped_names = (
            vineyards.groupby("id")[other_gdf_name_col]
            .transform(
                lambda x: ", ".join(x.dropna().unique())
                if x.dropna().nunique() > 1
                else x
            )
        )

        # A nevek átadása és a duplikátumok törlése
        vineyards[other_gdf_name_col] = grouped_names
        vineyards = vineyards.drop_duplicates(ignore_index=True)

    vineyards[other_gdf_name_col] = (
        vineyards[other_gdf_name_col].fillna("Nem ismert")
    )

    # Eredeti geometriák visszaállítása
    vineyards = vineyards.set_geometry(original_geoms)

    if not test_run:
        # A "stopper" leállítása
        utils.run_time.end_time(
            f"A prepare_vector_data.spatial_join(vineyards, other_gdf, "
            f"{other_gdf_name_col}) függvény futása befejeződött.",
            start,
            2
        )

    return vineyards


def join_soils_preperties_to_vineyards(
        vineyards: gpd.GeoDataFrame,
        soils: gpd.GeoDataFrame,
        inner_function: bool = False,
        test_run: bool = False
) -> gpd.GeoDataFrame:
    """ A talajtulajdonságok összekapcsolása a dűlőkkel.

    A dűlőkhöz csatolja annak talajainak tulajdonságait. Ezt teszi úgy,
    hogy az egyes tulajdonságokkal rendelkező talajrészek területi
    arányát kiszámolja a dűlők területéhez mérten.
    Pl. 1.00 a teljes dűlő --> 'A' típusú talaj területi aránya 0.37

    Args:
        vineyards: A dűlőket tartalmazó GeoDataFrame.
        soils: A talajokat (AGROTOPO) tartalmazó GeoDataFrame.
        inner_function: Belső függvényként van-e alkalmazva?
        test_run: Teszt futtatáshoz használt-e a függvény?

    Returns:
        A dűlőket tartalmazó GeoDataFrame a talajadatokkal együtt.
    """

    if not inner_function and not test_run:
        # A "stopper" indítása
        start = utils.run_time.start_time(
            f"prepare_vector_data.join_soils_to_vineyards(vineyards, soils) "
            f"függvény futása elindult.",
            2
        )

    # Talajok metszése a dűlők területével + attribútumok összekapcsolásával
    soils_clipped = gpd.overlay(
        soils,
        vineyards,
    )

    # Metszet talajrészek területe a későbbi számításokhoz
    soils_clipped["clipped_area"] = soils_clipped.geometry.area

    # Szükséges talajtulajdonságok
    soil_properties = soils.drop(columns=["geometry"]).columns

    # Rész eredmény Pivot-táblák list-je
    pivot_tables = []

    for soil_property in soil_properties:

        # Talaj részek csoportosítása tulajdonság alapján
        # + csoport terület számítás
        grouped = soils_clipped.groupby(
            ["id", "area_m2", soil_property],
            as_index=False
        )["clipped_area"].sum()

        # Terület arány számítás (csoport terület / dűlő terület)
        grouped["area_ratio"] = (
                grouped["clipped_area"] / grouped["area_m2"]
        ).round(3)

        # Pivot-tábla létrehozása az egyes csoportok alapján
        pivot = grouped.pivot(
            index="id",
            columns=soil_property,
            values="area_ratio"
        )

        # Oszlopnevek módosítása a tulajdonság alapján + Pivot-tábla mentése
        pivot.columns = [f"{soil_property}_{col}" for col in pivot.columns]
        pivot_tables.append(pivot)

    # Pivot-táblák összekapcsolása + hiányzó értékek helyett 0
    all_ratios = pd.concat(
        pivot_tables,
        axis=1
    ).fillna(0)

    # Csoportok területarányának hozzákapcsolása a dűlőkhöz id alapján
    # + hiányzó értékek helyett 0
    vineyards = vineyards.merge(
        all_ratios,
        on="id",
        how="left"
    ).fillna(0)

    if not inner_function and not test_run:
        # A "stopper" leállítása
        utils.run_time.end_time(
            f"prepare_vector_data.join_soils_to_vineyards(vineyards, soils) "
            f"függvény futása befejeződött.",
            start,
            2
        )

    return vineyards


# ===============================================
# A VEKTOROS ADATOK ELŐKÉSZÍTÉSÉNEK FOLYAMATA
# ===============================================

def process(
        gdfs: dict[str, gpd.GeoDataFrame],
        test_run: bool = False
) -> None:
    """ Végrehajtja a vektoros adatok előkészítésének folyamatát.

    A dűlőket térben összekapcsolja a településekkel, a borvidékekkel,
    a borrégiókkal és a talajokkal. Majd kezeli a térbeli
    összekapcsolások eredményét a dűlőket tartalmazó GeoDataFrame-ben.

    Args:
        gdfs: A GeoDataFrame-eket tartalmazó dict.
        test_run: Teszt futtatáshoz használt-e a függvény?
    """

    if not test_run:
        # A "stopper" indítása
        start = utils.run_time.start_time(
            "A prepare_vector_data.process(gdfs) függvény futása "
            "elindult.",
            1
        )

    vineyards = gdfs["vineyards"]

    # Dűlők adatainak kiegészítése (id, area_m2, area_ha)
    vineyards = supplement_vineyard_data(
        vineyards,
        test_run=test_run
    )

    for layer in gdfs.keys():

        if layer in ["vineyards", "soils"]:
            continue

        vineyards = spatial_join(
            vineyards,
            gdfs[layer],
            layer[:-1],
            test_run=test_run
        )

    soils = gdfs["soils"]
    vineyards = join_soils_preperties_to_vineyards(
        vineyards,
        soils,
        test_run=test_run
    )

    gdfs["vineyards"] = vineyards

    if not test_run:
        # A "stopper" leállítása
        utils.run_time.end_time(
            "A prepare_vector_data.process(gdfs) függvény futása "
            "befejeződött.",
            start,
            1
        )

