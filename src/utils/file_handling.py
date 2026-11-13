""" Fájlok kezeléséhez nyújt függvényt. """


import pathlib


def create_folders(file_path: pathlib.Path) -> None:
    """ Létrehozza a mappákat a megadott fájl elérés alapján.

    Kinyeri a fájl elérési útjából a mappákat és, ha azok közül
    valamelyik is nem létezne létre hozza.

    Args:
        file_path: A fájl elérési útja.
    """

    file_path.parent.mkdir(parents=True, exist_ok=True)