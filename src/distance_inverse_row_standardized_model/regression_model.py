import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

# Price data
df = pd.read_parquet(r'../../data/processed/wheat_prices.parquet')
df['Date'] = df['Date'].dt.to_timestamp()
df = df.set_index('Date')
# Spatial weights
W = pd.read_parquet(r'../../data/processed/W_distance.parquet')
countries = W.index.tolist()
prices = df[countries].copy()
prices_model = (
    prices.loc['2014':]
    .interpolate(method='time')
    .bfill()
    .ffill()
)
# get disel factor
diesel_factor = pd.read_parquet(r'../../data/processed/diesel_price.parquet')
print(diesel_factor)
y = prices_model

Wy = y @ W.T

y_lag = y.shift(1)
Wy_lag = Wy.shift(1)

data = pd.DataFrame({
    'y': y.stack(),
    'Wy': Wy.stack(),
    'y_lag': y_lag.stack(),
    'Wy_lag': Wy_lag.stack()
}).reset_index()

data.columns = ['date', 'country', 'y', 'Wy', 'y_lag', 'Wy_lag']
data["date"] = pd.to_datetime(data["date"]).dt.to_period("M")
data['month'] = data['date'].dt.month
data = data.merge(
    diesel_factor,
    on="date",
    how="left"
)
data['Wy_diesel'] = data['Wy'] * data['EU_price_with_tax_diesel']
data['Wy_diesel_lag'] = data['Wy_lag'] * data['EU_price_with_tax_diesel']
data = data.dropna()
print(data.shape)
print(data.head())
print(data.isna().sum())

# Now ready to make first model

model = smf.ols(
    'y ~ y_lag +Wy_diesel+ Wy_diesel_lag + C(country)+ C(month)', # You can shoose to use spatial weight matrix with diesel prices, or with just distance
    data=data
).fit(
    cov_type='cluster',
    cov_kwds={'groups': data['country']}
)

print(model.summary())

# Save residuals
data['residual'] = model.resid


#Inspect the residuals to identify events
data['resid_z'] = (
    data.groupby('country')['residual']
    .transform(lambda x: (x - x.mean()) / x.std())
).abs()


events = data[data['resid_z'].abs() > 2].copy()


# Define common event vs local event
data['common_resid'] = data.groupby('date')['residual'].transform('mean')

data['local_resid'] = (
    data['residual'] - data['common_resid']
)

# Check events
print("=== Local Residuals ===")
print(
    data.loc[
        data['local_resid'].abs().sort_values(ascending=False).index
    ].head(20)
)

print("=== Standradized residuals ===")
print(
    data.loc[
        data['resid_z'].abs().sort_values(ascending=False).index
    ].head(20)
)
print("=== Common Residuals ===")
print(
    data.loc[
        data['common_resid'].abs().sort_values(ascending=False).index
    ].head(30)
)
# Save data
data.to_parquet(
    r'../../data/processed/wheat_spatial_model_residuals.parquet'
)


# Plot the local residuals for top 6 countries
data = data.sort_values(["country", "date"])
top6_countries = (data.assign(abs_local_resid=data["local_resid"].abs()) .groupby("country")["abs_local_resid"].mean().sort_values(ascending=False).head(3).index)


print(top6_countries.tolist()) # Keep only the top 6 countries

df_top6 = data[data["country"].isin(top6_countries)].copy()
# Sort for plotting
df_top6 = df_top6.sort_values(["country", "date"])
# Common y-axis limits based on the entire dataset
ymin = data["local_resid"].min()
ymax = data["local_resid"].max()

# Add a little padding
padding = 0.05 * (ymax - ymin)
ymin -= padding
ymax += padding
# Create 2x3 grid
fig, axes = plt.subplots(
    1, 3,
    figsize=(15, 4),
    sharex=True,
    sharey=True
)

axes = axes.flatten()

for ax, country in zip(axes, top6_countries):
    country_data = data[data["country"] == country].sort_values("date")

    ax.plot(
        country_data["date"].dt.to_timestamp(),
        country_data["local_resid"],
        linewidth=1.5
    )

    ax.axhline(
        0,
        color="black",
        linewidth=0.8,
        linestyle="--"
    )

    ax.set_title(country, fontweight="bold")
    ax.grid(alpha=0.2)
    ax.set_ylim(ymin, ymax)


fig.suptitle(
    "Local residuals for countries with highest average absolute local residual",
    fontsize=16,
    fontweight="bold"
)

fig.supxlabel("Date")
fig.supylabel("Local residual")


plt.tight_layout()
plt.show()

# Plot lowest absolute average value
bottom6_countries = (
    data.assign(abs_local_resid=data["local_resid"].abs())
      .groupby("country")["abs_local_resid"]
      .mean()
      .sort_values(ascending=True)
      .head(3)
      .index
)

print(bottom6_countries.tolist())
fig, axes = plt.subplots( 1, 3, figsize=(15, 4), sharex=True, sharey=True )
axes = axes.flatten()

for ax, country in zip(axes, bottom6_countries):
    country_data = data[data["country"] == country].sort_values("date")

    ax.plot(
        country_data["date"].dt.to_timestamp(),
        country_data["local_resid"],
        linewidth=1.5
    )

    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_title(country, fontweight="bold")
    ax.grid(alpha=0.2)
    ax.set_ylim(ymin, ymax)


fig.suptitle( "Countries with lowest average absolute local residual", fontsize=16, fontweight="bold" )
fig.supxlabel("Date")
fig.supylabel("Local residual")
plt.tight_layout()
plt.show()