import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="SmartData Football", layout="wide")
st.title("SmartData Football - Big Five")

components.iframe(
    "https://dbc-bd92d678-4eea.cloud.databricks.com/embed/dashboardsv3/01f1cbc95bba1d239922735a2f3351e0?o=7474660439165743",
    height=1000,
    scrolling=True,
)