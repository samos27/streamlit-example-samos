import streamlit as st
from streamlit_calendar import calendar
import pandas as pd
from datetime import datetime, date

st.set_page_config(layout="wide")

st.title("Mi Calendario de Eventos 📅")

# --- Load and Prepare Data for the Streamlit app ---
excel_file_path = 'Control de Fechas 2025 Auto (1).xlsx'

original_events_app = [] # Store all events initially
df_app = pd.DataFrame()

try:
    df_app = pd.read_excel(excel_file_path)
    if 'FECHA' in df_app.columns and 'MODELO' in df_app.columns:
        df_app['FECHA'] = pd.to_datetime(df_app['FECHA'])

        for index, row in df_app.iterrows():
            event = {
                "title": str(row['MODELO']),
                "start": row['FECHA'].isoformat(),
                "allDay": True,
                "extendedProps": { # Add other relevant data here for potential future use or display
                    "direccion": str(row['DIRECCION']),
                    "hora": str(row['HORA']),
                    "superficie": str(row['SUPERFICIE']) # Include superficie for potential future use/display
                }
            }
            original_events_app.append(event)
    else:
        st.error("Error: The Excel file must contain 'FECHA' and 'MODELO' columns for the calendar and filtering.")
except FileNotFoundError:
    st.error(f"Error: The Excel file '{excel_file_path}' was not found. Please check the path.")
except Exception as e:
    st.error(f"An error occurred while loading or processing the Excel file: {e}")

# --- Filtering Options in Sidebar ---
st.sidebar.header("Filtrar Eventos")

# Ensure df_app is not empty before attempting to filter
if not df_app.empty:
    filtered_df_app = df_app.copy()

    # Date Range Filter
    min_date_val = filtered_df_app['FECHA'].min().date() if not filtered_df_app.empty else date.today()
    max_date_val = filtered_df_app['FECHA'].max().date() if not filtered_df_app.empty else date.today()

    date_range = st.sidebar.date_input(
        "Selecciona Rango de Fechas",
        value=(min_date_val, max_date_val),
        min_value=min_date_val,
        max_value=max_date_val
    )

    if date_range and len(date_range) == 2:
        start_date_filter = pd.Timestamp(date_range[0])
        end_date_filter = pd.Timestamp(date_range[1])
        filtered_df_app = filtered_df_app[
            (filtered_df_app['FECHA'] >= start_date_filter) &
            (filtered_df_app['FECHA'] <= end_date_filter)
        ]

    # Model Filter
    unique_models = df_app['MODELO'].unique().tolist() if not df_app.empty else []
    selected_models = st.sidebar.multiselect(
        "Filtrar por Modelo",
        options=unique_models,
        default=unique_models # Select all by default
    )
    if selected_models:
        filtered_df_app = filtered_df_app[filtered_df_app['MODELO'].isin(selected_models)]

    # Re-prepare events based on filtered DataFrame (this is mostly for calendar view)
    events_to_display = []
    if not filtered_df_app.empty:
        for index, row in filtered_df_app.iterrows():
            event = {
                "title": str(row['MODELO']),
                "start": row['FECHA'].isoformat(),
                "allDay": True,
                "extendedProps": {
                    "direccion": str(row['DIRECCION']),
                    "hora": str(row['HORA']),
                    "superficie": str(row['SUPERFICIE'])
                }
            }
            events_to_display.append(event)
else:
    events_to_display = []
    filtered_df_app = pd.DataFrame() # Ensure this is empty too if data not loaded
    st.warning("No se pudo cargar la base de datos para filtrar.")


# --- View Selector ---
view_type = st.radio("Seleccionar Vista", ('Calendario', 'Lista'), index=0)

# --- Display Content based on View Type ---
if view_type == 'Calendario':
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

    if events_to_display:
        st.subheader(f"Eventos cargados: {len(events_to_display)}")
        calendar_component = calendar(events=events_to_display,
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
        st.warning("No hay eventos para mostrar con los filtros seleccionados.")

elif view_type == 'Lista':
    st.subheader("Lista de Eventos")
    if not filtered_df_app.empty:
        # Select relevant columns for the list view
        display_columns = ['MODELO', 'FECHA', 'HORA', 'SUPERFICIE', 'DIRECCION', 'NOMBRE', 'CELULAR']
        st.dataframe(filtered_df_app[display_columns].sort_values(by='FECHA').reset_index(drop=True))
    else:
        st.warning("No hay eventos para mostrar con los filtros seleccionados.")

st.write("\n--- Creado con Streamlit y streamlit_calendar ---")
