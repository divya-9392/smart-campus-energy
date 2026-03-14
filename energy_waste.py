import pandas as pd
import numpy as np


def detect_unoccupied_waste(df, threshold=2.0):
    """
    Detect rooms consuming energy while unoccupied.
    Threshold avoids small phantom loads.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    if 'Occupancy Status' not in df.columns or 'Energy Consumption (kWh)' not in df.columns:
        return pd.DataFrame()

    waste_df = df[
        (df['Occupancy Status'] == 0) &
        (df['Energy Consumption (kWh)'] > threshold)
    ].copy()

    if not waste_df.empty:
        waste_df['Alert Type'] = 'Unoccupied Energy Waste'
        waste_df['Description'] = (
            'Room is unoccupied but consuming significant energy '
            f'(> {threshold} kWh).'
        )

    return waste_df


def detect_abnormal_usage(df, z_threshold=3.0):
    """
    Detect abnormal energy usage using Z-score per building.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    if 'Building Name' not in df.columns or 'Energy Consumption (kWh)' not in df.columns:
        return pd.DataFrame()

    abnormal_records = []

    for building, group in df.groupby('Building Name'):

        mean_energy = group['Energy Consumption (kWh)'].mean()
        std_energy = group['Energy Consumption (kWh)'].std()

        if std_energy > 0:
            group = group.copy()

            group['Z-Score'] = (
                (group['Energy Consumption (kWh)'] - mean_energy)
                / std_energy
            )

            anomalies = group[group['Z-Score'] > z_threshold].copy()

            if not anomalies.empty:
                anomalies['Alert Type'] = 'Abnormal Excessive Usage'
                anomalies['Description'] = (
                    f'Energy usage exceeds {z_threshold} standard deviations '
                    'above building average.'
                )

                abnormal_records.append(anomalies)

    if abnormal_records:
        return pd.concat(abnormal_records, ignore_index=True)

    return pd.DataFrame()


def classify_severity(row):
    """
    Classify alert severity based on energy consumption.
    """
    energy = row['Energy Consumption (kWh)']

    if energy > 20:
        return "CRITICAL"
    elif energy > 10:
        return "HIGH"
    elif energy > 5:
        return "MEDIUM"
    else:
        return "LOW"


def generate_waste_alerts(df):
    """
    Combine all waste detection methods into a unified alert system.
    """

    unoccupied_waste = detect_unoccupied_waste(df)
    abnormal_waste = detect_abnormal_usage(df)

    alerts = []

    if not unoccupied_waste.empty:
        alerts.append(unoccupied_waste)

    if not abnormal_waste.empty:
        alerts.append(abnormal_waste)

    if alerts:

        combined_alerts = pd.concat(alerts, ignore_index=True)

        # Add severity classification
        combined_alerts['Severity'] = combined_alerts.apply(
            classify_severity, axis=1
        )

        columns_to_show = [
            'Date',
            'Building Name',
            'Room Number',
            'Energy Consumption (kWh)',
            'Alert Type',
            'Severity',
            'Description'
        ]

        existing_cols = [
            col for col in columns_to_show if col in combined_alerts.columns
        ]

        return combined_alerts[existing_cols]

    return pd.DataFrame()