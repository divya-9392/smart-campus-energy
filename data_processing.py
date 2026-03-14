import pandas as pd
import numpy as np

def load_data(file_path_or_buffer):
    """Loads energy data from an Excel file."""
    try:
        df = pd.read_excel(file_path_or_buffer)
        
        # Ensure 'Date' column is converted to datetime objects for accurate sorting/grouping
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'],errors='coerce')
            
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def get_total_campus_consumption(df):
    """Calculates total campus energy consumption."""
    if df is None or df.empty or 'Energy Consumption (kWh)' not in df.columns:
        return 0.0
    return round(df['Energy Consumption (kWh)'].sum(), 2)

def aggregate_by_building(df):
    """Aggregates energy usage by building."""
    if df is None or df.empty or 'Building Name' not in df.columns:
        return pd.DataFrame()
        
    building_agg = df.groupby('Building Name')['Energy Consumption (kWh)'].sum().reset_index()
    building_agg = building_agg.sort_values(by='Energy Consumption (kWh)', ascending=False)
    return building_agg

def aggregate_by_room(df):
    """Aggregates energy usage by room."""
    if df is None or df.empty or 'Room Number' not in df.columns:
        return pd.DataFrame()
        
    room_agg = df.groupby(['Building Name', 'Room Number'])['Energy Consumption (kWh)'].sum().reset_index()
    room_agg = room_agg.sort_values(by='Energy Consumption (kWh)', ascending=False)
    return room_agg

def get_daily_trend(df):
    """Calculates daily energy usage trend for the campus."""
    if df is None or df.empty or 'Date' not in df.columns:
        return pd.DataFrame()
        
    trend = df.groupby(df['Date'].dt.date)['Energy Consumption (kWh)'].sum().reset_index()
    trend.rename(columns={'Date': 'Date'}, inplace=True)
    return trend
def calculate_carbon_emissions(df):
    """Estimate CO2 emissions based on energy consumption."""
    
    if df is None or df.empty:
        return 0
        
    total_energy = df['Energy Consumption (kWh)'].sum()
    
    # Average grid emission factor
    emission_factor = 0.82   # kg CO2 per kWh
    
    carbon_emissions = total_energy * emission_factor
    
    return round(carbon_emissions, 2)


def calculate_efficiency_score(df, alerts_df):
    """Calculate smart campus energy efficiency score."""
    
    if df is None or df.empty:
        return 100
        
    total_usage = df['Energy Consumption (kWh)'].sum()
    
    if total_usage == 0:
        return 100
        
    if alerts_df is None or alerts_df.empty:
        return 100
        
    wasted_energy = alerts_df['Energy Consumption (kWh)'].sum()
    
    waste_percentage = (wasted_energy / total_usage) * 100
    
    efficiency_score = max(0, 100 - waste_percentage)
    
    return round(efficiency_score, 2)