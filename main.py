from src import load_data
from src import prepare_vector_data
from src import calculate_raster_data
from src import join_rasters_to_polygons
from src import make_result_data
from src import utils


def main():

    # A "stopper" indítása
    start = utils.run_time.start_time(
        "A program (main.main() függvény futása) elindult.",
        0
    )

    # Adatok betöltése
    gdfs, rasters = load_data.process()

    # Tisztán vektoros adatok előkészítése
    prepare_vector_data.process(gdfs)

    # Raszterek létrehozása számításokkal
    calculate_raster_data.process(rasters)

    # Zóna statisztikák számítása
    join_rasters_to_polygons.process(gdfs, rasters)

    # Eredmény adat előállítása és mentése GPKG fájlba
    make_result_data.process(gdfs, rasters)

    # A "stopper" leállítása
    utils.run_time.end_time(
        "A program (main.main() függvény futása) befejeződött.",
        start,
        0
    )


if __name__ == "__main__":
    main()