import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager

from typing import Tuple


class Subplots:
    def __init__(self, nplots: int, figsize: Tuple[int, int] | None = None) -> None:
        font_dirs = ['fonts']
        font_files = font_manager.findSystemFonts(fontpaths=font_dirs)

        for font_file in font_files:
            font_manager.fontManager.addfont(font_file)

        plt.rcParams["font.family"] = "HSE Sans"
        plt.rcParams["font.size"] = 32
        #  сменить цвет графика на голубой
        plt.rcParams["axes.prop_cycle"] = plt.cycler(color=["#0072B2"])
        n = (nplots // 2) + nplots % 1
        if not figsize:
            figsize = (20, 10 * n)
        self.fig, self.axes = plt.subplots(
            nrows=n,
            ncols=2,
            figsize=figsize
        )


def subplots(nplots: int, figsize: Tuple[int, int] | None = None):
    return Subplots(nplots=nplots, figsize=figsize)
