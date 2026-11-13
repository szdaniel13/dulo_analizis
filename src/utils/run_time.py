""" A futási idő méréséhez nyújt segédfüggvényeket. """


import timeit


def start_time(
        text: str,
        level: int
) -> float:
    """ Az "stopper" elindítása a függvényhez.

    Args:
        text: A kiírandó szöveg.
        level: A szöveg szintje.

    Returns:
        A kezdő időpont másodpercben.
    """

    start = timeit.default_timer()

    tabs = "\t" * level
    empty_row = "\n" * (2 - level)

    print(tabs + text + empty_row)

    return start


def end_time(
        text: str,
        start: float,
        level: int
):
    """ A "stopper" leállítása a függvényhez.

    Args:
        text: A kiírandó szöveg.
        start: A kezdőidőpont másodpercben.
        level: A szöveg szintje.
    """

    stop = timeit.default_timer()

    run_time = stop - start
    hours, mod = divmod(run_time, 3600)
    minutes, mod = divmod(mod, 60)
    seconds = mod

    tabs = "\t" * level
    empty_row = "\n" * (3 - level)

    run_time_str = (f"A futási idő {f'{hours:.0f} óra ' if hours > 0 else ''}"
                    f"{f'{minutes:.0f} perc ' if minutes > 0 else ''}"
                    f"{f'{seconds:.3f} sec' if seconds > 0 else ''}.")

    print(f"{tabs}{text} {run_time_str} {empty_row}")