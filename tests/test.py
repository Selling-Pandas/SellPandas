import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from SellPandas.preprocessing import *

# url = "ecology.xlsx"
# url = 'База данных Оригинал.xlsx'
url = 'C:\\Users\\Vex1cK\\Vex\\Proga\\Selling Pandas\\spandas\\База данных Оригинал.xlsx'
# url = "Copy of Как быть успешным в учебе.xls"
df = pd.read_excel(url)
exc = ['user_id']
df=df.groupby('user_id')
clear_df, deleted = data_preprocessing(df.sum(), select_method=2, exclude=exc, logging=Loggs(was_became=False))