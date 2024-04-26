import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass
from art import tprint
from spandas.plots import print_distr

# write your code here
# it is preferable to use Classes in this module
# also use type annotations to make code more clear and efficient to write


@dataclass
class Loggs:
    """
    Класс отвечает за вывод логов
    Объект класса буквально такой: тут логи пиши, а тут логи не пиши
    Такой объект передаётся в качестве параметра в основную функцию data_preprocessing
    """
    test: bool = False
    cols_selection: bool = True
    was_became: bool = True


def get_list_of_cols(
    df: pd.DataFrame,
    n=2,
    exclude=["id"],
    method: int = 1,
    ignore_strings: bool = True
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
            if df[col].dtype not in ['float64', 'int64'] and not ignore_strings:
                continue
            if df[col].dtype in ['float64', 'int64']:
                result.append(col)
                continue
            str_count = sum(list(map(lambda x: not str(x).isdigit(), df[col].unique())))
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
    Здесь не используется ignore_string т.к. если он True, то строки и так сохраняются
    А если он False, то столбцы со строками вообще не должны выбираться, поэтому сюда
    строковые значения не попадут
    """
    if series.dtype not in ['float64', 'int64']:
        series_without_strings = series[series.apply(lambda x: str(x).isdigit())] \
            .astype("float64")
    if method == 1:
        q1 = series_without_strings.quantile(0.25)
        q3 = series_without_strings.quantile(0.75)
        iqr = q3 - q1
        lower_fence = q1 - 1.5 * iqr
        upper_fence = q3 + 1.5 * iqr
        return ~series.apply(lambda x: (lower_fence <= float(x) <= upper_fence
                                        if str(x).isdigit() else True))
    if method == 2:
        #  here will be some method
        pass


def remove_outliers_from_series(series: pd.Series, method: int = 1):
    return series[~mark_outliers(series, method=method)]


def remove_outliers(df: pd.DataFrame, columns: list[str] = None, method: int = 1):
    return df[~sum(mark_outliers(df[co], method=method) for co in columns).astype(bool)]


def is_el_ok(
    elem: str,
    Q3: int,
    Q1: int,
    value_for_str=True,
    value_for_nan=True,
):
    if not elem.isdigit():
        return value_for_str
    elem = float(elem)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    if lower_bound <= elem <= upper_bound:
        return True
    if elem != elem:
        return value_for_nan
    return False


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
    df = test_df(df, logging=logging.test)

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
    """
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
    """
    for col in cols:
        marks = mark_outliers(clear_df[col], method=delete_method)
        if save_deleted:
            deleted[col] = {}
            deleted[col]["count"] = (sum(marks))
            deleted[col]["deleted"] = dict(zip(list(clear_df[marks][col].keys()),
                                               list(clear_df[marks][col].values)))
            print(f"column: {col} => deleted: {deleted[col]['count']}")
        clear_df = clear_df[~marks]
    if logging.was_became:
        tprint("WAS:")
        print_distr(df, cols, (10, 13))
        tprint("__________")
        tprint("BECAME:")
        print_distr(clear_df, cols, (10, 13))
    return clear_df, deleted


def test_df(df: pd.DataFrame, autofix=1, logging=False):
    """
    Герман попросил
    Идея в чём, в датасете могут быть столбцы типа object но при этом в них только числа
    Эта фанка это находит и меняет тип столбца
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
