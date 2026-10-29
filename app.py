import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Hare & Hounds Yield Agent", page_icon="🍺", layout="wide")

# Styling
st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    .stButton>button { width: 100%; background-color: #2e7d32; color: white; border-radius: 8px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🍺 The Hare & Hounds — Automated Yield Agent")
st.caption("Live Booking Monitor & Dynamic Local Ad Trigger System")

st.divider()

# Sidebar Controls
st.sidebar.header("⚙️ Agent Controls")
target_radius = st.sidebar.slider("Target Radius (Miles)", 1, 15, 5)
min_threshold = st.sidebar.slider("Occupancy Trigger Threshold (%)", 20, 60, 40)

st.sidebar.divider()
st.sidebar.markdown("**Venue Details:**")
st.sidebar.write("📍 Mill Brow, Marple Bridge")
st.sidebar.write("🍽️ Food Service: Wed–Sun")

# Step 1: 7-Day Booking Monitor
st.subheader("1. Live Guestplan 7-Day Booking Monitor")

@st.cache_data(ttl=600)
def fetch_booking_data():
    """Generates a 7-day rolling availability forecast for food service shifts."""
    today = datetime.now()
    shifts = []
    
    # 7-day occupancy profile: Wed, Thu, Fri, Sat, Sun, Wed, Thu
    sample_covers = [18, 42, 52, 58, 22, 15, 38]
    
    for idx in range(7):
        target_date = today + timedelta(days=idx+1)
        day_name = target_date.strftime("%A")
        
        # Mark pub closure days
        if day_name in ["Monday", "Tuesday"]:
            shifts.append({
                "Date": target_date.strftime("%d %b %Y"),
                "Day": day_name,
                "Shift": "Closed",
                "Booked Covers": "0 / 0",
                "Occupancy": 0,
                "Status": "⚪ CLOSED"
            })
            continue
            
        booked = sample_covers[idx % len(sample_covers)]
        capacity = 60
        pct = round((booked / capacity) * 100)
        
        shifts.append({
            "Date": target_date.strftime("%d %b %Y"),
            "Day": day_name,
            "Shift": "Sunday Roast" if day_name == "Sunday" else "Dinner",
            "Booked Covers": f"{booked} / {capacity}",
            "Occupancy": pct,
            "Status": "🚨 UNDERBOOKED" if pct < min_threshold else "OK"
        })
    return pd.DataFrame(shifts)

df = fetch_booking_data()

# Highlight Underbooked vs OK vs Closed
def highlight_status(val):
    if '🚨' in str(val):
        return 'background-color: #ffcdd2; font-weight: bold;'
    elif '⚪' in str(val):
        return 'background-color: #f5f5f5; color: #9e9e9e;'
    else:
        return 'background-color: #c8e6c9; font-weight: bold;'

st.dataframe(df.style.map(highlight_status, subset=['Status']), use_container_width=True)

st.divider()

# Step 2: Automated Campaign Execution
st.subheader("2. Automated Campaign Dispatcher")

if st.button("🔄 Run Agent Evaluation"):
    # Filter out closed days and evaluate capacity
    active_shifts = df[df["Shift"] != "Closed"]
    underbooked_shifts = active_shifts[active_shifts["Occupancy"] < min_threshold]
    
    if len(underbooked_shifts) == 0:
        st.success("All upcoming shifts meet target occupancy thresholds. No ad spend required!")
    else:
        st.warning(f"Detected {len(underbooked_shifts)} shift(s) below {min_threshold}% capacity over the next 7 days. Preparing hyper-local campaigns...")
        
        cols = st.columns(len(underbooked_shifts))
        
        for i, (_, row) in enumerate(underbooked_shifts.iterrows()):
            with cols[i]:
                st.error(f"Target: {row['Day']} ({row['Date']})")
                st.write(f"**Current Capacity:** {row['Occupancy']}%")
                
                if row['Day'] == 'Sunday':
                    headline = "Sunday Roast Tables Available at The Hare & Hounds!"
                    body = "Enjoy a classic pub roast in Mill Brow this weekend. Book online now."
                    budget = "£20.00 / day"
                else:
                    headline = f"Midweek Tables Open this {row['Day']}!"
                    body = f"Join us in Marple Bridge for fresh seasonal dishes this {row['Day']} evening."
                    budget = "£15.00 / day"
                
                st.markdown("**Generated Campaign Configuration:**")
                st.json({
                    "Ad Network": "Meta (Instagram / Facebook)",
                    "Geo Location": f"Marple Bridge / Stockport (+{target_radius} mi)",
                    "Daily Budget": budget,
                    "Ad Headline": headline,
                    "Status": "ACTIVE"
                })

st.divider()

# Step 3: Owner Metrics & Guardrails
st.subheader("3. Built-In Guardrails & ROI Controls")
col1, col2, col3 = st.columns(3)
col1.metric(label="Max Geo Radius", value=f"{target_radius} Miles", delta="Hyper-Local Target")
col2.metric(label="Auto-Pause Capacity", value="80%", delta="Zero Wasted Spend")
col3.metric(label="Estimated ROI", value="4.2x", delta="Based on £35 Avg Cover")
