import streamlit as st
from streamlit_calendar import calendar
import pandas as pd
from datetime import datetime, date
import altair as alt # Import Altair

st.set_page_config(layout="wide")

st.title("Mi Calendario de Eventos 📅")

# --- Load and Prepare Data for the Streamlit app ---
excel_file_path = 'Control de Fechas 2025 Auto Finaaaal.xlsx'

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

    # Model Filter (changed to selectbox with 'Todos los modelos' option)
    unique_models = df_app['MODELO'].unique().tolist() if not df_app.empty else []
    model_options = ['Todos los modelos'] + sorted(unique_models)
    selected_model = st.sidebar.selectbox(
        "Filtrar por Modelo",
        options=model_options,
        index=0 # 'Todos los modelos' selected by default
    )

    if selected_model != 'Todos los modelos':
        filtered_df_app = filtered_df_app[filtered_df_app['MODELO'] == selected_model]

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
    # Calendar View Selector
    selected_calendar_view = st.selectbox(
        "Seleccionar Vista de Calendario",
        ['dayGridMonth', 'timeGridWeek', 'timeGridDay', 'listWeek', 'listDay'],
        index=0 # Default to month view
    )

    # --- Calendar Configuration ---
    calendar_options = {
        "editable": "true",
        "navLinks": "true",
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay,listWeek,listDay" # Added list views
        },
        "initialView": selected_calendar_view, # Use the selected view
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

# --- New Section: Top 5 Inflables Chart ---
st.subheader("Top 5 Inflables Más Rentados por Mes y Año")

if not df_app.empty:
    # Get unique years for the selectbox
    df_app['YEAR'] = df_app['FECHA'].dt.year
    df_app['MONTH'] = df_app['FECHA'].dt.month

    all_years = sorted(df_app['YEAR'].unique().tolist(), reverse=True)
    selected_year = st.selectbox("Selecciona el Año", options=all_years, key="select_year")

    # Filter months based on the selected year
    available_months_for_year = df_app[df_app['YEAR'] == selected_year]['MONTH'].unique().tolist()
    available_months_for_year.sort()

    month_map = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
        7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    month_map_inv = {v: k for k, v in month_map.items()}

    month_options = [month_map[m] for m in available_months_for_year]
    selected_month_name = st.selectbox("Selecciona el Mes", options=month_options, key="select_month")
    selected_month_num = month_map_inv.get(selected_month_name)

    if selected_year and selected_month_num:
        df_filtered_by_date = df_app[
            (df_app['YEAR'] == selected_year) &
            (df_app['MONTH'] == selected_month_num)
        ]

        if not df_filtered_by_date.empty:
            # Calculate top 5 most rented 'MODELO's
            top_5_inflables = df_filtered_by_date['MODELO'].value_counts().nlargest(5).reset_index()
            top_5_inflables.columns = ['MODELO', 'Conteo de Rentas']

            # Create Altair bar chart
            chart = alt.Chart(top_5_inflables).mark_bar().encode(
                x=alt.X('Conteo de Rentas', title='Cantidad de Rentas'),
                y=alt.Y('MODELO', sort='-x', title='Modelo de Inflable')
            ).properties(
                title=f'Top 5 Inflables en {selected_month_name} de {selected_year}'
            ).interactive()

            st.altair_chart(chart, use_container_width=True)
        else:
            st.info(f"No se encontraron rentas para {selected_month_name} de {selected_year}.")
else:
    st.warning("La base de datos está vacía, no se pueden mostrar los inflables más rentados.")

st.write("\n--- Creado con Streamlit y streamlit_calendar ---")
