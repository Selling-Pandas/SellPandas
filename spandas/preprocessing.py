import pandas as pd
import matplotlib.pyplot as plt
from art import tprint

# write your code here
# it is preferable to use Classes in this module
# also use type annotations to make code more clear and efficient to write


class Loggs:
    test: bool = False


def get_dict_of_cols(
    df: pd.DataFrame, n=2, exclude=["id"], method: int = 1, ignore_strings: bool = False
):
    """
    Returns a dict like:
    {column: [str_value, str_value]}
    where the str_value is one of the few string values in the column

    if method == 2:
        return[column] == []

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
    ignore_strings : bool, default False
        Flag for ignoring columns with strings in them
    """
    if method not in (1, 2):
        raise ValueError("Method must be 1 or 2")

    result = {"method": method}
    if method == 1:
        columns_in_df = df.columns
        for column in columns_in_df:
            if column in exclude:
                continue
            str_count, strs, digit_count = 0, [], 0
            values = df[column].value_counts().keys()
            for val in values:
                if str(val).isdigit():
                    digit_count += 1
                else:
                    str_count += 1
                    strs.append(val)
                    if not ignore_strings:
                        continue
                if str_count > n:
                    continue
            if digit_count == 0:
                continue
            result[column] = strs
        return result
    elif method == 2:
        for col in df.columns:
            if (ignore_strings or df[col].dtype in ["float64", "int64"]) and df.shape[
                0
            ] / 100 < len(df[col].unique()) <= df.shape[0]:
                result[col] = []
        return result


def mark_outliers(series: pd.Series):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower_fence = q1 - 1.5 * iqr
    upper_fence = q3 + 1.5 * iqr
    # print(~series.apply(lambda x: lower_fence <= x <= upper_fence))
    return ~series.apply(lambda x: lower_fence <= x <= upper_fence)


def remove_outliers_from_series(series: pd.Series, method: int = 1):
    return series[~mark_outliers(series).astype(bool)]


def remove_outliers2(df: pd.DataFrame, columns: list[str] = None):
    pass
    return df[~sum(mark_outliers(df[col]) for col in columns).astype(bool)]


def print_distr(
    df: pd.DataFrame, cols: dict, figsize: tuple[int, int] = (30, 30), bins: int = 100
) -> tuple[bool, str]:
    try:
        _, axes = plt.subplots(
            (len(cols.keys()) // 2) + (1 if len(cols.keys()) % 2 > 0 else 0),
            2,
            figsize=figsize,
        )  # не читайте, не надо, это просто работает, ок?
        i, j, max_i = (
            0,
            0,
            (len(cols.keys()) // 2) + (1 if len(cols.keys()) % 2 > 0 else 0),
        )
        for col in cols.keys():
            exceptions = cols[col]
            col_of_nums = df[col].apply(
                lambda x: (-1000 if (x in exceptions or x != x) else float(x))
            )  # x != x only when x is NaN
            axes[i, j].hist(col_of_nums, bins=bins)
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


def is_el_ok(
    elem: str,
    exceps: list[str],
    Q3: int,
    Q1: int,
    value_for_exceptions=True,
    value_for_nan=True,
):
    if elem in exceps:
        return value_for_exceptions
    elem = float(elem)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    if lower_bound <= elem <= upper_bound:
        return True
    if elem != elem:
        return value_for_nan
    return False


def remove_outliers(
    df: pd.DataFrame,
    n: int = 2,
    logging: Loggs = Loggs(),
    select_method: int = 1,
    delete_method: int = 1,
    ignore_strings: bool = True,
    exclude: list[str] = ["id"],
):
    df = test_df(df, logging=logging.test)

    cols = get_dict_of_cols(
        df=df, n=n, exclude=exclude, method=select_method, ignore_strings=ignore_strings
    )

    tprint("Cols:")
    print()
    print(*cols, sep=" | ")
    tprint("============================")

    clear_df = df.copy(deep=True)
    deleted = {}
    """
    deleted = {
        method: "iqr" or smthg else
        column: {
            count: (count of deleted elements)
            deleted: []
        },
        ...
    }
    """
    for col in cols.keys():
        exceptions = cols[col]
        Q3 = (
            clear_df[clear_df[col].apply(lambda x: x not in exceptions)][col]
            .astype(float)
            .quantile(0.75)
        )
        Q1 = (
            clear_df[clear_df[col].apply(lambda x: x not in exceptions)][col]
            .astype(float)
            .quantile(0.25)
        )
        values = clear_df[col].apply(
            lambda x: is_el_ok(elem=str(x), exceps=exceptions, Q3=Q3, Q1=Q1)
        )
        if logging:
            deleted[col] = {}
            deleted[col]["count"] = (
                values.value_counts().values[1] if len(values.value_counts()) > 1 else 0
            )
            deleted[col]["deleted"] = list(clear_df[~values][col].values)
            print(
                f"column: {col} => deleted: {values.value_counts().values[1] if len(values.value_counts().values) > 1 else 0}"
            )
        clear_df = clear_df[values]
    tprint("WAS:")
    print_distr(df, cols, (10, 13))
    tprint("============================")
    tprint("BECAME:")
    print_distr(clear_df, cols, (10, 13))
    if logging:
        return clear_df, deleted
    return clear_df, {}


def test_df(df: pd.DataFrame, autofix=1, logging=False):
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
