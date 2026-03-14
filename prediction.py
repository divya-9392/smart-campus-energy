import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from datetime import timedelta
import numpy as np


def train_and_predict(df, days_to_predict=7):
    """
    Train Random Forest model on historical daily energy usage
    and predict future campus-wide consumption.
    """

    if df is None or df.empty or 'Date' not in df.columns:
        return None, "Insufficient data for prediction"

    # Aggregate energy by date
    daily_df = df.groupby('Date')['Energy Consumption (kWh)'].sum().reset_index()
    daily_df = daily_df.sort_values('Date')

    if len(daily_df) < 14:
        return None, "Need at least 14 days of historical data."

    # ---------------------------
    # Feature Engineering
    # ---------------------------

    daily_df['DayOfWeek'] = daily_df['Date'].dt.dayofweek
    daily_df['DayOfMonth'] = daily_df['Date'].dt.day
    daily_df['Month'] = daily_df['Date'].dt.month
    daily_df['IsWeekend'] = daily_df['DayOfWeek'].apply(lambda x: 1 if x >= 5 else 0)

    # Lag Feature
    daily_df['Prev_Day_Energy'] = daily_df['Energy Consumption (kWh)'].shift(1)

    model_df = daily_df.dropna()

    X = model_df[
        [
            'DayOfWeek',
            'DayOfMonth',
            'Month',
            'IsWeekend',
            'Prev_Day_Energy'
        ]
    ]

    y = model_df['Energy Consumption (kWh)']

    # ---------------------------
    # Train Model
    # ---------------------------

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42
    )

    model.fit(X, y)

    # ---------------------------
    # Predict Future Dates
    # ---------------------------

    last_date = daily_df['Date'].max()
    last_known_energy = daily_df.iloc[-1]['Energy Consumption (kWh)']

    future_dates = [
        last_date + timedelta(days=i)
        for i in range(1, days_to_predict + 1)
    ]

    predictions = []
    current_lag = last_known_energy

    for date in future_dates:

        day_of_week = date.dayofweek
        day_of_month = date.day
        month = date.month
        is_weekend = 1 if day_of_week >= 5 else 0

        features = pd.DataFrame(
            [{
                'DayOfWeek': day_of_week,
                'DayOfMonth': day_of_month,
                'Month': month,
                'IsWeekend': is_weekend,
                'Prev_Day_Energy': current_lag
            }]
        )

        pred_energy = model.predict(features)[0]

        # Prevent negative prediction
        pred_energy = max(0, pred_energy)

        predictions.append({
            'Date': date,
            'Predicted Energy (kWh)': round(pred_energy, 2)
        })

        current_lag = pred_energy

    return pd.DataFrame(predictions), "Success"