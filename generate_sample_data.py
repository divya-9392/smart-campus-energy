import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_data(num_days=30, num_buildings=5, rooms_per_building=10):
    start_date = datetime.now() - timedelta(days=num_days)
    
    data = []
    buildings = [f"Building {chr(65+i)}" for i in range(num_buildings)] # Building A, B, etc.
    
    for day in range(num_days):
        current_date = start_date + timedelta(days=day)
        
        for building in buildings:
            for room_num in range(1, rooms_per_building + 1):
                room = f"{building[-1]}-{room_num:03d}"
                
                # Base energy is somewhat related to whether room is occupied
                occupancy = random.choices([0, 1], weights=[0.4, 0.6])[0]
                
                # Devices on correlates with occupancy but sometimes devices are left on
                if occupancy == 1:
                    devices_on = random.randint(1, 10)
                else:
                    devices_on = random.choices([0, random.randint(1, 4)], weights=[0.8, 0.2])[0]
                
                # Energy consumption calculation
                base_consumption = random.uniform(5.0, 15.0)
                device_consumption = devices_on * random.uniform(0.5, 2.0)
                
                # If occupied, normal consumption + device consumption
                # If vacant but devices on, just device consumption + small phantom load
                # If vacant and no devices, just phantom load
                if occupancy == 1:
                    energy = base_consumption + device_consumption
                elif devices_on > 0:
                    energy = random.uniform(2.0, base_consumption * 0.5) + device_consumption
                else:
                    energy = random.uniform(0.1, 1.5) # Phantom load or HVAC baseline
                
                # Introduce some anomalies (energy waste when unoccupied)
                if occupancy == 0 and random.random() < 0.1:
                    # 10% chance of high energy when empty (e.g., HVAC left on)
                    energy += random.uniform(20.0, 40.0)
                    devices_on += random.randint(1, 5) # Maybe some lights/devices left on too
                
                data.append({
                    "Date": current_date.strftime("%Y-%m-%d"),
                    "Building Name": building,
                    "Room Number": room,
                    "Energy Consumption (kWh)": round(energy, 2),
                    "Occupancy Status": occupancy,
                    "Number of Devices On": devices_on
                })
                
    df = pd.DataFrame(data)
    df.to_excel("campus_energy_data.xlsx", index=False)
    print(f"Successfully generated campus_energy_data.xlsx with {len(df)} rows.")

if __name__ == "__main__":
    generate_data()
