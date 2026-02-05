import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt

# =============================
# LOAD DATA
# =============================
df = pd.read_excel("claims_data.xlsx")

df['Departure_Month'] = pd.to_datetime(df['Departure_Month'])

# =============================
# AGGREGATE FINAL TOTALS
# =============================
total_df = (
    df.groupby(['Country','Departure_Month'])['Claim_Amount']
    .sum()
    .reset_index()
)

# =============================
# FORECAST PER COUNTRY
# =============================
results = []

for country in total_df['Country'].unique():
    
    country_df = total_df[total_df['Country'] == country]
    country_df = country_df.sort_values('Departure_Month')
    
    ts = country_df.set_index('Departure_Month')['Claim_Amount']
    
    # Need minimum history
    if len(ts) < 12:
        continue
    
    # =============================
    # FIT ARIMA MODEL
    # =============================
    model = ARIMA(ts, order=(1,1,1))   # baseline order
    model_fit = model.fit()
    
    # =============================
    # FORECAST NEXT MONTH
    # =============================
    forecast = model_fit.forecast(steps=1)
    
    results.append([
        country,
        forecast.index[0],
        forecast.iloc[0]
    ])

# =============================
# OUTPUT
# =============================
forecast_df = pd.DataFrame(
    results,
    columns=[
        "Country",
        "Forecast_Departure_Month",
        "Forecast_Total_Claims"
    ]
)

print(forecast_df)
    
