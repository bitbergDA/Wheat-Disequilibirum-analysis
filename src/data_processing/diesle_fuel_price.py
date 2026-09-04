import pandas as pd

df = pd.read_excel(r'../../data/raw/Weekly_Oil_Bulletin_Prices_History_maticni_4web.xlsx')
print(df)
df = df[df["CTR"] == "EU_"]
df["Consumer prices of petroleum products inclusive of duties and taxes"] = pd.to_datetime(df["Consumer prices of petroleum products inclusive of duties and taxes"])

monthly = (
    df.groupby(df["Consumer prices of petroleum products inclusive of duties and taxes"].dt.to_period("M"))["EU_price_with_tax_diesel"]
      .mean()
      .reset_index()
)

df_small = monthly[["EU_price_with_tax_diesel", "Consumer prices of petroleum products inclusive of duties and taxes"]].copy()
df_small = df_small.rename(columns={"Consumer prices of petroleum products inclusive of duties and taxes": "date"})
df_small["date"] = df_small["date"] + 1
print(df_small)
df_small = df_small[df_small["date"] >= "2014-01"]
df_small.to_parquet(r'../../data/processed/diesel_price.parquet')
