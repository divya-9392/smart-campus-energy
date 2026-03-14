import streamlit as st
from dotenv import load_dotenv
load_dotenv() # Load variables from .env file
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Custom Modules
import data_processing
import energy_waste
import recommendations
import prediction
import auth

# --- Page Configuration ---
st.set_page_config(
    page_title="Smart Campus Energy Optimization",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Styling ---
st.markdown("""
<style>

/* Main Background */
.stApp {
    background-color: #0E1117;
    color: #FFFFFF;
    font-family: 'Inter', sans-serif;
}

/* General Text */
body, p, span, label {
    color: #FFFFFF !important;
}

/* Headers */
h1, h2, h3 {
    color: #00E5FF !important;
    font-weight: 600 !important;
}

/* KPI Numbers */
div[data-testid="stMetricValue"] {
    font-size: 2.5rem !important;
    color: #FFFFFF !important;
}

/* KPI Labels */
div[data-testid="stMetricLabel"] {
    color: #B8C7E0 !important;
    font-size: 1rem !important;
}

/* KPI Card Styling */
.stMetric {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.15);
}

/* Hover effect */
.stMetric:hover {
    transform: translateY(-5px);
    border-color: #00C6FF;
}

/* Warning alert */
.waste-alert {
    background: rgba(255, 75, 75, 0.1);
    border-left: 5px solid #FF4B4B;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)
# --- Authentication ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login to Smart Campus")
    
    tab_login, tab_signup = st.tabs(["Login", "Sign Up (First Time)"])
    
    with tab_login:
        st.subheader("Welcome Back")
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if auth.verify_user(login_email, login_password):
                st.session_state.logged_in = True
                st.session_state.user_email = login_email
                st.rerun()
            else:
                st.error("Invalid email or password.")
                
    with tab_signup:
        st.subheader("Create an Account")
        if 'otp_sent' not in st.session_state:
            st.session_state.otp_sent = False
            
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Password", type="password", key="signup_pass")
        signup_confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")
        
        if not st.session_state.otp_sent:
            if st.button("Send OTP via Email"):
                if signup_password != signup_confirm:
                    st.error("Passwords do not match!")
                elif len(signup_password) < 6:
                    st.error("Password must be at least 6 characters.")
                elif not signup_email or "@" not in signup_email:
                    st.error("Please enter a valid email.")
                else:
                    otp = auth.generate_otp()
                    if auth.send_otp_email(signup_email, otp):
                        st.session_state.otp = otp
                        st.session_state.otp_email = signup_email
                        st.session_state.otp_pass = signup_password
                        st.session_state.otp_sent = True
                        st.success("OTP successfully generated. If you haven't configured an SMTP server in your environment variables, check the console output to see the OTP!")
                        st.rerun()
                    else:
                        st.error("Failed to send OTP.")
                        
        if st.session_state.otp_sent:
            entered_otp = st.text_input("Enter 6-digit OTP", key="entered_otp")
            if st.button("Verify & Create Account"):
                if entered_otp == st.session_state.otp:
                    if auth.create_user(st.session_state.otp_email, st.session_state.otp_pass):
                        st.session_state.logged_in = True
                        st.session_state.user_email = st.session_state.otp_email
                        st.success("Account created successfully!")
                        st.session_state.otp_sent = False
                        st.rerun()
                    else:
                        st.error("Account already exists. Please login instead.")
                        st.session_state.otp_sent = False
                else:
                    st.error("Invalid OTP.")
                    
            if st.button("Cancel / Resend"):
                st.session_state.otp_sent = False
                st.rerun()

    st.stop() # Stop execution here if not logged in

# --- Sidebar ---
st.sidebar.markdown(f"👤 Logged in as: **{st.session_state.user_email}**")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
    
st.sidebar.markdown("---")

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/814/814513.png", width=60)
st.sidebar.title("Smart Campus Setup")
st.sidebar.markdown("Using default campus electricity usage dataset (`campus_energy_data.xlsx`).")
import os

default_file = "campus_energy_data.xlsx"

if not os.path.exists(default_file):
    with st.spinner("Generating default dataset..."):
        import generate_sample_data
        generate_sample_data.generate_data()

# --- Load Data ---
with st.spinner("Analyzing dataset..."):
    df = data_processing.load_data(default_file)

if df is None or df.empty:
    st.error("Error loading data.")
    st.stop()

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard overview",
    "🚨 Waste Detection",
    "💡 Optimization Recommendations",
    "🔮 Future Prediction"
])

# ----------------------------------------------------
# TAB 1
# ----------------------------------------------------

with tab1:

    st.title("Campus Energy Overview")

    total_consumption = data_processing.get_total_campus_consumption(df)
    carbon_emissions = data_processing.calculate_carbon_emissions(df)

    alerts_df_temp = energy_waste.generate_waste_alerts(df)
    efficiency_score = data_processing.calculate_efficiency_score(df, alerts_df_temp)

    cols = st.columns(5)

    with cols[0]:
        st.metric("Total Energy Consumption", f"{total_consumption:,.2f} kWh")

    with cols[1]:
        st.metric("Buildings Monitored", df['Building Name'].nunique())

    with cols[2]:
        st.metric("Rooms Monitored", df['Room Number'].nunique())

    with cols[3]:
        st.metric("Carbon Emissions", f"{carbon_emissions:,.2f} kg CO₂")

    with cols[4]:
        st.metric("Campus Efficiency Score", f"{efficiency_score}%")

    st.markdown("---")

    trend_df = data_processing.get_daily_trend(df)

    st.subheader("Daily Energy Usage Trend")

    fig_trend = px.line(
        trend_df,
        x="Date",
        y="Energy Consumption (kWh)",
        markers=True,
        template="plotly_dark",
        color_discrete_sequence=["#00E5FF"]
    )

    fig_trend.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig_trend, use_container_width=True)

    col_chart, col_table = st.columns([6,4])

    with col_chart:

        st.subheader("Energy Usage by Building")

        building_agg = data_processing.aggregate_by_building(df)

        fig_bar = px.bar(
            building_agg,
            x="Building Name",
            y="Energy Consumption (kWh)",
            color="Energy Consumption (kWh)",
            color_continuous_scale="Blues",
            template="plotly_dark"
        )

        fig_bar.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(fig_bar, use_container_width=True)

    with col_table:

        st.subheader("Top Consuming Rooms")

        room_agg = data_processing.aggregate_by_room(df)

        st.dataframe(
            room_agg.head(10).style.background_gradient(cmap='Blues'),
            use_container_width=True,
            hide_index=True
        )

# ----------------------------------------------------
# TAB 2
# ----------------------------------------------------

with tab2:

    st.title("Energy Waste Detection Alerts")

    alerts_df = energy_waste.generate_waste_alerts(df)

    if alerts_df.empty:
        st.success("No significant energy waste detected.")
    else:

        num_alerts = len(alerts_df)
        total_wasted = alerts_df['Energy Consumption (kWh)'].sum()

        st.markdown(f"""
        <div class="waste-alert">
        <h3>{num_alerts} Potential Energy Waste Instances Detected</h3>
        <p>Estimated Wasted Energy: <strong>{total_wasted:,.2f} kWh</strong></p>
        </div>
        """, unsafe_allow_html=True)

        fig_pie = px.pie(
            alerts_df,
            names="Alert Type",
            values="Energy Consumption (kWh)",
            hole=0.4,
            template="plotly_dark"
        )

        col1, col2 = st.columns([1,2])

        with col1:
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            st.subheader("Alert Log")

            st.dataframe(
                alerts_df.style.highlight_max(
                    subset=['Energy Consumption (kWh)'],
                    color='rgba(255,75,75,0.4)'
                ),
                use_container_width=True,
                hide_index=True
            )

# ----------------------------------------------------
# TAB 3
# ----------------------------------------------------

with tab3:

    st.title("Optimization Recommendations")

    if 'alerts_df' not in locals():
        alerts_df = energy_waste.generate_waste_alerts(df)

    if alerts_df.empty:
        st.info("No room-specific recommendations.")
    else:

        rec_df = recommendations.generate_recommendations(alerts_df)

        total_savings = rec_df['Estimated Savings (kWh)'].sum()

        st.metric("Total Potential Savings", f"{total_savings:,.2f} kWh")

        st.dataframe(
            rec_df.style.format({'Estimated Savings (kWh)': "{:.2f}"}),
            use_container_width=True,
            hide_index=True
        )

    st.markdown("---")

    st.subheader("Campus-Wide Strategies")

    strategies = recommendations.get_scheduling_strategies()

    cols = st.columns(len(strategies))

    for i, strat in enumerate(strategies):

        with cols[i]:

            st.markdown(f"### {strat['Strategy']}")
            st.markdown(f"*{strat['Description']}*")
            st.markdown(f"**Impact:** {strat['Est. Impact']}")

# ----------------------------------------------------
# TAB 4
# ----------------------------------------------------

with tab4:

    st.title("Future Energy Prediction")

    pred_df, msg = prediction.train_and_predict(df, days_to_predict=7)

    if pred_df is None:

        st.warning(msg)

    else:

        historical = data_processing.get_daily_trend(df)
        historical['Type'] = 'Historical'

        pred_df['Type'] = 'Predicted'
        pred_df = pred_df.rename(columns={'Predicted Energy (kWh)': 'Energy Consumption (kWh)'})

        combined_df = pd.concat([historical, pred_df])

        fig_pred = px.line(
            combined_df,
            x="Date",
            y="Energy Consumption (kWh)",
            color="Type",
            markers=True,
            template="plotly_dark",
            color_discrete_map={
                "Historical":"#00E5FF",
                "Predicted":"#FF00FF"
            }
        )

        st.plotly_chart(fig_pred, use_container_width=True)

        st.subheader("Predicted Data")

        st.dataframe(
            pred_df[['Date','Energy Consumption (kWh)']],
            use_container_width=True,
            hide_index=True
        )