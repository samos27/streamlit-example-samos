

import streamlit as st
from streamlit_calendar import calendar
import pandas as pd

st.set_page_config(layout="wide")

st.title("Mi Calendario de Eventos 📅")

# --- Load and Prepare Data for the Streamlit app ---
# Adjust the path to your Excel file if necessary
excel_file_path = 'Control de Fechas 2025 Auto (1).xlsx'

events_app = [] # Initialize as empty list

try:
    df_app = pd.read_excel(excel_file_path)
    if 'FECHA' in df_app.columns and 'MODELO' in df_app.columns:
        df_app['FECHA'] = pd.to_datetime(df_app['FECHA'])

        for index, row in df_app.iterrows():
            event = {
                "title": str(row['MODELO']),
                "start": row['FECHA'].isoformat(),
                "allDay": True
            }
            events_app.append(event)
    else:
        st.error("Error: The Excel file must contain 'FECHA' and 'MODELO' columns for the calendar.")
except FileNotFoundError:
    st.error(f"Error: The Excel file '{excel_file_path}' was not found. Please check the path.")
except Exception as e:
    st.error(f"An error occurred while loading or processing the Excel file: {e}")

# --- Calendar Configuration ---
calendar_options = {
    "editable": "true",
    "navLinks": "true",
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay"
    },
    "initialView": "dayGridMonth",
    "locale": "es", # Set calendar locale to Spanish
    "height": "auto" # Adjust height automatically
}

# --- Display Calendar ---
if events_app:
    st.subheader(f"Eventos cargados: {len(events_app)}")
    calendar_component = calendar(events=events_app,
                                  options=calendar_options,
                                  custom_css="""
                                      .fc-event-past {
                                          opacity: 0.8;
                                      }
                                      .fc-event-time {
                                          font-style: italic;
                                      }
                                      .fc-event-title {
                                          font-weight: bold;
                                      }
                                      .fc-toolbar-title {
                                          font-size: 2rem;
                                      }
                                  """,
                                  key="fullcalendar")

    st.write(calendar_component)
else:
    st.warning("No events to display in the calendar. Please check data loading and preparation.")

st.write("\n--- Creado con Streamlit y streamlit_calendar ---")
