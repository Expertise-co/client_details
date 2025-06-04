import streamlit as st
import pandas as pd

# Page config: wide layout, no menu and footer
st.set_page_config(
    page_title="Client Details",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit header and footer via CSS
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Load Excel file
@st.cache_data
def load_data():
    return pd.read_excel('Vendor Registration.xlsx', sheet_name='Sheet1', skiprows=1)

df = load_data()

# Clean data: strip spaces and convert to string to avoid issues
df['CLIENT'] = df['CLIENT'].astype(str).str.strip()
df['STATUS'] = df['STATUS'].astype(str).str.strip()
df['VENDOR #'] = df['VENDOR #'].astype(str).str.strip()

# Page Title
st.markdown("<h1 style='color:#1f77b4; margin-bottom: 10px; text align: center;'>📋 Client Details</h1>", unsafe_allow_html=True)
st.markdown("---")

# Status summary always visible
st.subheader("📊 Overall Status Summary")
col1, col2, col3 = st.columns([1,1,1])
status_counts = df['STATUS'].value_counts()

col1.metric("✅ Registered", status_counts.get('Registered', 0))
col2.metric("📤 Submitted", status_counts.get('Submitted', 0))
col3.metric("🔄 In Progress", status_counts.get('In Progress', 0))

st.markdown("---")

# Client input dropdown with placeholder and empty first option
clients = sorted(df['CLIENT'].dropna().unique())
typed_client = st.selectbox(
    "🔍 Type or select a client name",
    options=[""] + clients,
    index=0,
    format_func=lambda x: "Start typing here..." if x == "" else x
)

# Button for details
if st.button("🔎 Get Details"):
    if typed_client.strip() == "":
        st.warning("Please enter or select a client name.")
    else:
        filtered_df = df[df['CLIENT'].str.lower() == typed_client.strip().lower()]

        # Remove rows where CLIENT, VENDOR # and STATUS are all empty or NaN
        filtered_df = filtered_df.dropna(subset=['CLIENT', 'VENDOR #', 'STATUS'], how='all')
        
        # Remove rows with empty strings in key columns
        filtered_df = filtered_df[
            (filtered_df['CLIENT'].str.strip() != '') &
            (filtered_df['VENDOR #'].str.strip() != '') &
            (filtered_df['STATUS'].str.strip() != '')
        ]

        if not filtered_df.empty:
            display_df = filtered_df[['CLIENT', 'VENDOR #', 'STATUS']].reset_index(drop=True)
            st.dataframe(display_df.style.hide(axis='index'), use_container_width=True, height=50)
        else:
            st.error("❌ No valid data found for that client. Please check the name.")

st.markdown("---")
st.markdown(
    "<small style='color:gray;'>© 2025 Expertise Contracting Co. Ltd</small>",
    unsafe_allow_html=True
)

custom_css = """
    <style>
        /* Remove top padding/margin of the main content */
        .css-18e3th9 {
            padding-top: 0rem;
            margin-top: 0rem;
        }
        /* Optionally reduce padding around container */
        .block-container {
            padding-top: 1rem;
        }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
