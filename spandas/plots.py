import matplotlib.pyplot as plt
from matplotlib import font_manager
from pandas import DataFrame
from SPandas.utils import is_float

from typing import Tuple


def subplots(nplots: int, figsize: Tuple[int, int] = ()):
    font_dirs = ['fonts']
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)

    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)

    plt.rcParams["font.family"] = "HSE Sans"
    plt.rcParams["font.size"] = 32
    #  сменить цвет графика на тёмнно-синий
    plt.rcParams["axes.prop_cycle"] = plt.cycler(color=["#01287a"])
    n = (nplots // 2) + nplots % 2
    if not figsize:
        figsize = (20, 10 * n)
    fig, axes = plt.subplots(
        nrows=n,
        ncols=2,
        figsize=figsize
    )
    return fig, axes


def print_distributions(
    df: DataFrame, cols: dict, figsize: tuple[int, int] = (), bins: int = 100
) -> tuple[bool, str]:
    try:
        _, axes = subplots(
            len(cols),
            figsize=figsize,
        )
        i, j, max_i = (
            0,
            0,
            (len(cols) // 2) + (1 if len(cols) % 2 > 0 else 0),
        )
        for col in cols:
            col_of_nums = df[col].apply(
                lambda x: (-1000 if (not is_float(str(x)) or x != x) else float(x))
            )  # x != x only when x is NaN
            axes[i, j].hist(col_of_nums)
            axes[i, j].set_xlabel(f"Значение переменной {col}")
            axes[i, j].set_ylabel("Частота")
            axes[i, j].set_title(f"График распределения переменной {col}")
            # axes[i, j].set_xticks(range())
            # axes[i, j].set_xlim(min(-1000, col_of_nums.min()), col_of_nums.max())
            # axes[i, j].set_ylim(0, 1500)
            i += 1
            if i == max_i:
                j += 1
                i = 0
        plt.tight_layout()
        plt.show()
    except Exception as ex:
        return False, str(ex)
    return True, ""
