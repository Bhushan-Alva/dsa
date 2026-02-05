import pandas as pd
import numpy as np
from scipy.stats.mstats import winsorize

# =========================================
# LOAD DATA
# =========================================
df = pd.read_excel("claims_data.xlsx")

# Convert to datetime
df['Departure_Month'] = pd.to_datetime(df['Departure_Month'])
df['Claim_Month'] = pd.to_datetime(df['Claim_Month'])

# Convert to monthly period (clean lag math)
df['Departure_Month'] = df['Departure_Month'].dt.to_period('M')
df['Claim_Month'] = df['Claim_Month'].dt.to_period('M')

# =========================================
# CREATE LAG COLUMN
# =========================================
df['Lag'] = (df['Claim_Month'] - df['Departure_Month']).apply(lambda x: x.n)

# Keep valid lag window
df = df[df['Lag'].isin([0,1,2])]

# =========================================
# BUILD DEVELOPMENT TRIANGLE
# =========================================
triangle = (
    df.groupby(['Country','Departure_Month','Lag'])['Claim_Amount']
    .sum()
    .unstack(fill_value=0)
)

# Ensure lag columns exist
for lag in [0,1,2]:
    if lag not in triangle.columns:
        triangle[lag] = 0

triangle = triangle[[0,1,2]]

# =========================================
# CALCULATE TOTAL & RATIOS
# =========================================
triangle['Total'] = triangle.sum(axis=1)

triangle = triangle[triangle['Total'] > 0]

ratio_triangle = triangle[[0,1,2]].div(triangle['Total'], axis=0)

# =========================================
# WINSORIZED MEAN FUNCTION
# =========================================
def winsorized_mean(series, lower=0.05, upper=0.05):
    w = winsorize(series, limits=[lower, upper])
    return np.mean(w)

# =========================================
# FORECAST PER COUNTRY
# =========================================
results = []

countries = ratio_triangle.index.get_level_values(0).unique()

for country in countries:
    
    country_ratio = ratio_triangle.loc[country].sort_index()
    country_triangle = triangle.loc[country].sort_index()
    
    latest_month = country_ratio.index.max()
    
    # Remove current incomplete month
    history_ratio = country_ratio.loc[country_ratio.index < latest_month]
    
    # Use last 12 months
    history_ratio = history_ratio.tail(12)
    
    if len(history_ratio) < 4:
        continue
    
    # =========================================
    # APPLY WINSORIZED MEAN
    # =========================================
    lag0_ratio = winsorized_mean(history_ratio[0])
    lag1_ratio = winsorized_mean(history_ratio[1])
    lag2_ratio = winsorized_mean(history_ratio[2])
    
    # Normalize ratios (important)
    total_ratio = lag0_ratio + lag1_ratio + lag2_ratio
    
    lag0_ratio /= total_ratio
    lag1_ratio /= total_ratio
    lag2_ratio /= total_ratio
    
    # =========================================
    # FORECAST CURRENT MONTH
    # =========================================
    current_data = country_triangle.loc[latest_month]
    
    lag0_actual = current_data[0]
    
    if lag0_ratio > 0:
        estimated_total = lag0_actual / lag0_ratio
    else:
        estimated_total = lag0_actual
    
    forecast_lag1 = estimated_total * lag1_ratio
    forecast_lag2 = estimated_total * lag2_ratio
    
    results.append([
        country,
        latest_month,
        lag0_actual,
        estimated_total,
        forecast_lag1,
        forecast_lag2,
        lag0_ratio,
        lag1_ratio,
        lag2_ratio
    ])

# =========================================
# OUTPUT RESULT
# =========================================
forecast_df = pd.DataFrame(
    results,
    columns=[
        "Country",
        "Departure_Month",
        "Current_Lag0_Actual",
        "Estimated_Final_Total",
        "Forecast_Lag1_NextMonth",
        "Forecast_Lag2_MonthPlus2",
        "Lag0_Ratio_Used",
        "Lag1_Ratio_Used",
        "Lag2_Ratio_Used"
    ]
)

print(forecast_df)

# Optional export
forecast_df.to_excel("claims_forecast_output.xlsx", index=False)
    
