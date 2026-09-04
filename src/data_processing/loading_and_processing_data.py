import pandas as pd
import numpy as np
import openpyxl

df = pd.read_excel(r"../../data/raw/Filename_Tue_Aug_25_2026 (2).xlsx")

df = df.drop(columns=["iso3_country_code"])

df.columns = [df.columns[0]] + [col.split(',')[0].strip() for col in df.columns[1:]]

df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y').dt.to_period('M')
df = df.drop(columns=['Sweden'])
df.info()
df.to_parquet(r'../../data/processed/wheat_prices.parquet')