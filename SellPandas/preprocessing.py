
from dataclasses import dataclass

# third party
from art import tprint
from SellPandas.plots import print_distributions
from SellPandas.utils import is_float

import pandas as pd


# write your code here
# it is preferable to use Classes in this module
# also use type annotations to make code more clear and efficient to write


@dataclass
class Loggs:
    """
    Класс отвечает за вывод логов
    Каждое поле включает или вылючает логи а конкретном этапе

    test:
    логи на этапе тестирования датасета на "приколы" (описано в object_to_float_check)
    cols_selection:
        Вывод выбранных колонок для очистки от выбросов
    was_became:
        Отвечает за вывод логов типа "было-стало" (графики и т.д.)
    """

    test: bool = False
    cols_selection: bool = True
    was_became: bool = True


def get_list_of_cols(
    df: pd.DataFrame, n=2, exclude=["id"], method: int = 1, ignore_strings: bool = True
):
    """
    Returns a list like:
    [column, column, column ...]
    where the column is name of selected column

    Parameters
    ----------
    df : pd.DataFrame
        Your main pandas dataframe
    n : int
        The maximum allowed number of string values per column
        len(return[column]) <= n
    exclude : list[str], default ["id"]
        The columns you want to exclude from the result
    method : int in (1, 2), default 1
        The method of selecting the columns
    ignore_strings : bool, default True
        Flag for ignoring strings in columns
    """
    if method not in (1, 2):
        raise ValueError("Method must be 1 or 2")

    result = []
    if method == 1:
        for col in df.columns:
            if col in exclude:
                continue
            if df[col].dtype not in ["float64", "int64"] and not ignore_strings:
                continue
            if df[col].dtype in ["float64", "int64"]:
                result.append(col)
                continue
            str_count = sum(list(map(lambda x: not is_float(str(x)), df[col].unique())))
            if str_count <= n:
                result.append(col)
        return result
    elif method == 2:
        for col in df.columns:
            if (ignore_strings or df[col].dtype in ["float64", "int64"]) and df.shape[
                0
            ] / 100 < len(df[col].unique()) <= df.shape[0]:
                result.append(col)
        return result


def mark_outliers(series: pd.Series, method: int = 1):
    """
    returns a Series of bool values. True if element is outlier

    Parameters
    ----------
    series : pd.Series
        Column from the pd.Dataframe or any other series with dtype in
        ("int64", "float64")
    method : int in (1, ) default 1
        method of marking the outliers
    ----------
    Здесь не используется ignore_string т.к. если он True, то строки и так сохраняются
    А если он False, то столбцы со строками вообще не должны выбираться, поэтому сюда
    строковые значения не попадут
    """
    series_without_strings = series.copy(deep=True)
    if series.dtype not in ['float64', 'int64']:
        series_without_strings = series[series.apply(lambda x: is_float(str(x)))] \
            .astype("float64")
    if method == 1:
        q1 = series_without_strings.quantile(0.25)
        q3 = series_without_strings.quantile(0.75)
        iqr = q3 - q1
        lower_fence = q1 - 1.5 * iqr
        upper_fence = q3 + 1.5 * iqr
        return ~series.apply(lambda x: (lower_fence <= float(x) <= upper_fence
                                        if is_float(str(x)) else True))
    if method == 2:
        q05 = series_without_strings.quantile(0.05)
        q95 = series_without_strings.quantile(0.95)
        return ~series.apply(lambda x: (q05 <= float(x) <= q95
                                        if is_float(str(x)) else True))


def remove_outliers_from_series(series: pd.Series, method: int = 1):
    """
    returns series without outliers

    Parameters
    ----------
    series : pd.Series
        Column from the pd.Dataframe or any other series with dtype in
        ("int64", "float64")
    method : int in (1, ) default 1
        method of marking the outliers
    """
    return series[~mark_outliers(series, method=method)]


def remove_outliers(df: pd.DataFrame, columns: list[str] = [], method: int = 1):
    """
    returns your df without outliers

    Parameters
    ----------
    df : pd.DataFrame
        Your main pandas dataframe
    method : int in (1, ) default 1
        method of marking the outliers
    columns: list[str] default []
        List of columns you want to clear of outliers
    """
    return df[~sum(mark_outliers(df[co], method=method) for co in columns).astype(bool)]


def data_preprocessing(
    df: pd.DataFrame,
    n: int = 2,
    logging: Loggs = Loggs(),
    select_method: int = 1,
    delete_method: int = 1,
    save_deleted: bool = True,
    ignore_strings: bool = True,
    exclude: list[str] = ["id"],
):
    """
    Returns two values: clear dataframe and dict of deleted values

    clear_df = pd.Dataframe without outliers

    deleted = {  # not empty only if save_deleted is True
        method: "iqr" or smthg else
        column: {
            count: (count of deleted elements)
            deleted: {
                id: value,
                id: value,
                ...
            }
        },
        ...
    }


    Parameters
    ----------
    df : pd.DataFrame
        Your main pandas dataframe
    n : int
        The maximum allowed number of string values per column (for selection columns)
    exclude : list[str], default ["id"]
        The columns you want to exclude
    select_method : int in (1, 2), default 1
        The method of selecting the columns
    delete_method : int in (1, ), default 1
        The method of deleting the outliers
    ignore_strings : bool, default True
        Flag for ignoring strings in columns
    save_deleted : bool, default True
        Flag for saving and returns deleted values
    logging : Loggs
        object of class Loggs (it consists of flags for logging, look class Loggs)
    """
    df = object_to_float_check(df, logging=logging.test)

    cols = get_list_of_cols(
        df=df, n=n, exclude=exclude, method=select_method, ignore_strings=ignore_strings
    )

    if logging.cols_selection:
        tprint("Selected cols:")
        print()
        print(*cols, sep=" | ")
        tprint("__________")

    clear_df = df.copy(deep=True)
    deleted = {}
    for col in cols:
        marks = mark_outliers(clear_df[col], method=delete_method)
        if save_deleted:
            deleted[col] = {}
            deleted[col]["count"] = sum(marks)
            deleted[col]["deleted"] = dict(
                zip(
                    list(clear_df[marks][col].keys()), list(clear_df[marks][col].values)
                )
            )
            print(f"column: {col} => deleted: {deleted[col]['count']}")
        clear_df = clear_df[~marks]
    if logging.was_became:
        tprint("WAS:")
        print_distributions(df, cols)
        tprint("__________")
        tprint("BECAME:")
        print_distributions(clear_df, cols)
    return clear_df, deleted


def object_to_float_check(df: pd.DataFrame, autofix: bool = True, logging=False):
    """
    Герман попросил
    Идея в чём, в датасете могут быть столбцы типа object но при этом в них только числа
    Эта фанка это находит и меняет тип столбца
    Всегда вызывается автоматически из data_preprocessing

    Parameters
    ----------
    df : pd.DataFrame
        Your main pandas dataframe
    autofix : bool default True
        Flag for autofixing the problem
    logging : bool default False
        Flag for logging the process
    """
    testing = df.select_dtypes(include="object")
    bad_columns = []
    for col in testing.columns:
        if sum(testing[col].apply(lambda x: not str(x).isdigit())) == 0:
            bad_columns.append(col)
    if bad_columns and logging:
        print(f'Найдены "плохие столбцы" вот их список: {" | ".join(bad_columns)}')
    if autofix:
        for col in bad_columns:
            df[col] = df[col].astype(float)

    return df
