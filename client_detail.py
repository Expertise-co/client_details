import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(
    page_title="Client Details",
    layout="wide",
    initial_sidebar_state="collapsed"
)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

ONEDRIVE_URL = st.secrets["onedrive"]["share_url"]

@st.cache_data
def load_data():
    direct_url = ONEDRIVE_URL.strip() + "&download=1"
    response = requests.get(direct_url)
    
    if response.status_code != 200:
        raise Exception("❌ Could not load the file from OneDrive. Please check the link.")
    
    excel_file = pd.ExcelFile(BytesIO(response.content))
    df_vr = pd.read_excel(excel_file, sheet_name = 'VR', skiprows = 1)
    df_old_vr = pd.read_excel(excel_file, sheet_name = 'OLD VR DETAILS')
    df_combined = pd.concat([df_vr, df_old_vr], ignore_index = True)

if st.button("⟲ Refresh Data"):
    load_data.clear()
    st.rerun()
    
try:
    df = load_data()
except Exception as e:
    st.error(str(e))
    st.stop()

df['CLIENT'] = df['CLIENT'].astype(str).str.strip()
df['STATUS'] = df['STATUS'].astype(str).str.strip()
df['VENDOR #'] = df['VENDOR #'].astype(str).str.strip()

st.markdown("<h1 style='color:#1f77b4; margin-bottom: 10px; text-align: center;'>📋 Client Details</h1>", unsafe_allow_html=True)

st.markdown("---")

st.markdown("## 📊 View Client Details by Status")

status_counts = df['STATUS'].str.strip().value_counts()
count_registered = status_counts.get('Registered', 0)
count_submitted = status_counts.get('Submitted', 0)
count_inprogress = status_counts.get('In Progress', 0)

col1, col2, col3 = st.columns(3)

show_table = False
status_filter = None

if col1.button(f"✅ Registered ({count_registered})"):
    status_filter = "Registered"
    show_table = True

if col2.button(f"📤 Submitted ({count_submitted})"):
    status_filter = "Submitted"
    show_table = True

if col3.button(f"🔄 In Progress ({count_inprogress})"):
    status_filter = "In Progress"
    show_table = True

# Show table when a button is clicked
if show_table and status_filter:
    filtered_df = df[df['STATUS'].str.strip().str.lower() == status_filter.lower()]
    filtered_df = filtered_df[['CLIENT', 'VENDOR #', 'STATUS']].dropna(how='all')
    filtered_df = filtered_df[
        (filtered_df['CLIENT'].str.strip() != '') &
        (filtered_df['VENDOR #'].str.strip() != '') &
        (filtered_df['STATUS'].str.strip() != '')
    ]
    if not filtered_df.empty:
        st.markdown(f"### 📋 Showing details for: **{status_filter}**")
        filtered_df = filtered_df.fillna('').replace(['nan', 'NaN', 'None'], 'NA')
        st.dataframe(filtered_df.style.hide(axis='index'), use_container_width=True)
    else:
        st.warning(f"No records found for status: **{status_filter}**")


st.markdown("---")

clients = sorted([client for client in df['CLIENT'].dropna().unique() if client.strip().lower() != 'target'])
typed_client = st.selectbox(
    "🔍 Type or select a client name",
    options=[""] + clients,
    index=0,
    format_func=lambda x: "Start typing here..." if x == "" else x
)

if st.button("🔎 Get Details"):
    if typed_client.strip() == "":
        st.warning("Please enter or select a client name.")
    else:
        filtered_df = df[df['CLIENT'].str.lower() == typed_client.strip().lower()]


        filtered_df = filtered_df.dropna(subset=['CLIENT', 'VENDOR #', 'STATUS'], how='all')
        

        filtered_df = filtered_df[
            (filtered_df['CLIENT'].str.strip() != '') &
            (filtered_df['VENDOR #'].str.strip() != '') &
            (filtered_df['STATUS'].str.strip() != '')
        ]

        if not filtered_df.empty:
            display_df = filtered_df[['CLIENT', 'VENDOR #', 'STATUS']].reset_index(drop=True)
            display_df = display_df.fillna('').replace(['nan', 'NaN', 'None'], 'NA')
            st.dataframe(display_df.style.hide(axis='index'), use_container_width=True, height=50)
        else:
            st.error("❌ No valid data found for that client. Please check the name.")

st.markdown("---")
st.markdown(
    "<small style='color:gray;'>© 2025 Expertise C.J.S.C.</small>",
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
