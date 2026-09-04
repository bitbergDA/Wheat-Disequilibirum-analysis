import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from sklearn.metrics import mean_squared_error
import xgboost as xgb
import matplotlib.pyplot as plt

data = pd.read_parquet(r'../../data/processed/wheat_spatial_model_residuals.parquet')
data['local_resid_lag1'] = data.groupby('country')['local_resid'].shift(1)
data['local_resid_log_lag1'] = (
    np.sign(data['local_resid_lag1'])
    * np.log1p(data['local_resid_lag1'].abs())
)


data['local_resid_lag2'] = (data.groupby('country')['local_resid'].shift(2))
data['local_resid_log_lag2'] = (
    np.sign(data['local_resid_lag2'])
    * np.log1p(data['local_resid_lag2'].abs())
)

data['local_resid_lag3'] = (data.groupby('country')['local_resid'].shift(3))
data['local_resid_log_lag3'] = (
    np.sign(data['local_resid_lag3'])
    * np.log1p(data['local_resid_lag3'].abs())
)

data['local_resid_lag4'] = (data.groupby('country')['local_resid'].shift(4))
data['local_resid_log_lag4'] = (
    np.sign(data['local_resid_lag4'])
    * np.log1p(data['local_resid_lag4'].abs())
)

data['resid_z_lag1'] = data.groupby('country')['resid_z'].shift(1)
data['common_resid_lag1'] = data.groupby('country')['common_resid'].shift(1)

data['Wy_lag2'] = data.groupby('country')['Wy'].shift(2)
data['Wy_lag3'] = data.groupby('country')['Wy'].shift(3)
data['naive_prediction'] = data.groupby('country')['y'].shift(1)
data['date'] = data['date'].dt.to_timestamp()

data = data.dropna()
TEST_START = '2024-01-01'
TEST_END = '2026-08-01'

train = data[data['date'] < TEST_START].copy()
test = data[
    (data['date'] >= TEST_START) &
    (data['date'] <= TEST_END)
].copy()
# Run model
model = smf.ols(
    'y ~  local_resid_lag1  +local_resid_lag2  + local_resid_lag3 + local_resid_lag4  +common_resid_lag1+ resid_z_lag1  +naive_prediction+C(country)+ C(month)',
    data=train
).fit(
    cov_type='cluster',
    cov_kwds={'groups': train['country']}
)

print(model.summary())
test['prediction'] = model.predict(test)


# Calc RMSE for model

rmse_model = np.sqrt(
    mean_squared_error(
        test['y'],
        test['prediction']
    )
)

rmse_naive = np.sqrt(
    mean_squared_error(
        test['y'],
        test['naive_prediction']
    )
)
# Print both

print("Naive RMSE:", rmse_naive)
print("Model RMSE:", rmse_model)
print("Model improvement:", (rmse_naive-rmse_model)/rmse_naive * 100,"%")



# Do tests
# 1. Naive / own history
m1 = smf.ols(
    'y ~ naive_prediction + C(country) + C(month)',
    data=train
).fit()

# 2. Add local residual
m2 = smf.ols(
    'y ~ naive_prediction + local_resid_lag1 + C(country) + C(month)',
    data=train
).fit()

# 3. Add standardized residual as well
m3 = smf.ols(
    'y ~ naive_prediction + local_resid_lag1 + resid_z_lag1 + C(country) + C(month)',
    data=train
).fit()

m4 = smf.ols(
    'y ~  local_resid_lag1+local_resid_lag2+local_resid_lag3+ local_resid_lag4+resid_z_lag1+naive_prediction+ C(country)+ C(month)',
    data=train
).fit()


# Predictions on TEST data
test['pred_m1'] = m1.predict(test)
test['pred_m2'] = m2.predict(test)
test['pred_m3'] = m3.predict(test)
test['pred_m4'] = m4.predict(test)


# RMSE function
def calc_rmse(actual, predicted):
    return np.sqrt(mean_squared_error(actual, predicted))


# Calculate RMSE
rmse_m1 = calc_rmse(test['y'], test['pred_m1'])
rmse_m2 = calc_rmse(test['y'], test['pred_m2'])
rmse_m3 = calc_rmse(test['y'], test['pred_m3'])
rmse_m4 = calc_rmse(test['y'], test['pred_m4'])

# Naive RMSE
rmse_naive = calc_rmse(
    test['y'],
    test['naive_prediction']
)


print("=" * 45)
print("OUT-OF-SAMPLE RMSE")
print("=" * 45)

print(f"Naive:             {rmse_naive:.5f}")
print(f"Model 1:           {rmse_m1:.5f}")
print(f"Model 2:           {rmse_m2:.5f}")
print(f"Model 3:           {rmse_m3:.5f}")
print(f"Model 4:           {rmse_m4:.5f}")

# TESTING ROBUSTNESS
results = []

for year, subset in test.groupby(test['date'].dt.year):

    rmse_model = np.sqrt(
        mean_squared_error(
            subset['y'],
            subset['prediction']
        )
    )

    rmse_naive = np.sqrt(
        mean_squared_error(
            subset['y'],
            subset['naive_prediction']
        )
    )

    improvement = (
        (rmse_naive - rmse_model)
        / rmse_naive * 100
    )

    results.append({
        'year': year,
        'n': len(subset),
        'rmse_model': rmse_model,
        'rmse_naive': rmse_naive,
        'improvement_pct': improvement
    })

results = pd.DataFrame(results)

print(results)

# plot
test['actual_change'] = test['y'] - test['naive_prediction']
test['model_change'] = test['prediction'] - test['naive_prediction']

countries = test['country'].unique()

fig, axes = plt.subplots(
    len(countries),
    1,
    figsize=(14, 8 * len(countries)),
    sharex=True
)

for ax, country in zip(axes, countries):

    subset = (
        test[test['country'] == country]
        .sort_values('date')
    )

    ax.plot(
        subset['date'],
        subset['actual_change'],
        color='steelblue',
        label='Actual',
        linewidth=2
    )

    ax.plot(
        subset['date'],
        subset['model_change'],
        color='crimson',
        label='Predicted',
        linewidth=2,
        linestyle='--'
    )

    ax.axhline(0, color='black', linewidth=0.8)
    ax.set_title(country)
    ax.grid(alpha=0.2)

axes[0].legend()
plt.tight_layout()
plt.show()
#### TEST A XGBOOST MODEL HERE ####
"""
features = [
    'naive_prediction',
    'local_resid_lag1',
    'local_resid_lag2',
    'local_resid_lag3',
    'local_resid_lag4',
    'resid_z_lag1'
]
X = pd.get_dummies(
    data[['country', 'month'] + features],
    columns=['country'],
    drop_first=True
)

y = data['y']

train_mask = data['date'] < '2024-01-01'

X_train = X.loc[train_mask]
X_test = X.loc[~train_mask]

y_train = y.loc[train_mask]
y_test = y.loc[~train_mask]



param_grid = [
    {'max_depth': 2, 'learning_rate': 0.05, 'n_estimators': 300},
    {'max_depth': 2, 'learning_rate': 0.05, 'n_estimators': 500},
    {'max_depth': 2, 'learning_rate': 0.05, 'n_estimators': 1000},
]

results = []

for params in param_grid:

    model = xgb.XGBRegressor(
        n_estimators=params['n_estimators'],
        max_depth=params['max_depth'],
        learning_rate=params['learning_rate'],
        subsample=0.8,
        colsample_bytree=0.8,
        objective='reg:squarederror',
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    prediction = model.predict(X_test)

    rmse = np.sqrt(
        mean_squared_error(y_test, prediction)
    )

    results.append({
        **params,
        'RMSE': rmse
    })

results = pd.DataFrame(results).sort_values('RMSE')

print(results)

"""