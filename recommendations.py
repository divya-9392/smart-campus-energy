import pandas as pd


def generate_recommendations(alerts_df):
    """
    Generate optimization recommendations based on detected energy waste alerts.
    """

    if alerts_df is None or alerts_df.empty:
        return pd.DataFrame()

    recommendations = []

    for _, row in alerts_df.iterrows():

        energy = row.get('Energy Consumption (kWh)', 0)
        alert_type = row.get('Alert Type', 'Unknown Issue')
        severity = row.get('Severity', 'LOW')

        rec = {
            'Date': row.get('Date', ''),
            'Building': row.get('Building Name', 'Unknown'),
            'Room': row.get('Room Number', 'Unknown'),
            'Issue Detected': alert_type,
            'Severity': severity,
            'Current Consumption (kWh)': energy
        }

        # --- Recommendation Logic ---

        if alert_type == 'Unoccupied Energy Waste':

            rec['Action Required'] = (
                "Turn off unnecessary devices, lights, and HVAC systems. "
                "Verify occupancy sensor functionality."
            )

            savings = max(0, energy - 1.0)

        elif alert_type == 'Abnormal Excessive Usage':

            rec['Action Required'] = (
                "Inspect equipment for malfunction or unauthorized high-power usage. "
                "Check HVAC systems and server racks."
            )

            savings = energy * 0.20

        else:

            rec['Action Required'] = "Review room energy schedule and equipment usage."

            savings = 0

        rec['Estimated Savings (kWh)'] = round(savings, 2)

        # --- Priority Score for ranking ---
        if severity == "CRITICAL":
            rec['Priority'] = "Immediate"
        elif severity == "HIGH":
            rec['Priority'] = "High"
        elif severity == "MEDIUM":
            rec['Priority'] = "Moderate"
        else:
            rec['Priority'] = "Low"

        recommendations.append(rec)

    rec_df = pd.DataFrame(recommendations)

    # Sort by priority and savings
    if not rec_df.empty:
        rec_df = rec_df.sort_values(
            by=['Estimated Savings (kWh)'],
            ascending=False
        )

    return rec_df


def get_scheduling_strategies():
    """
    General campus-wide energy optimization strategies.
    """

    return [

        {
            "Strategy": "HVAC Deadband Optimization",
            "Description": "Increase temperature deadband by ±2°C during non-peak hours.",
            "Est. Impact": "Medium"
        },

        {
            "Strategy": "Smart Lighting Automation",
            "Description": "Install motion-based lighting and automatic dimming after 8 PM.",
            "Est. Impact": "High"
        },

        {
            "Strategy": "Weekend Power-Down",
            "Description": "Shut down HVAC and lab equipment in unused academic buildings during weekends.",
            "Est. Impact": "High"
        },

        {
            "Strategy": "Smart Plug Monitoring",
            "Description": "Deploy smart plugs to detect phantom loads from idle electronics.",
            "Est. Impact": "Medium"
        }

    ]