if 'df' in locals() and not df.empty:
    # Check if 'FECHA' and 'MODELO' columns exist
    if 'FECHA' in df.columns and 'MODELO' in df.columns:
        # Convert 'FECHA' column to datetime objects
        df['FECHA'] = pd.to_datetime(df['FECHA'])

        # Prepare events in the format required by streamlit_calendar
        events = []
        for index, row in df.iterrows():
            event = {
                "title": str(row['MODELO']),
                "start": row['FECHA'].isoformat(),
                "allDay": True # Set to True if events span full days without specific times
            }
            events.append(event)

        print(f"Successfully prepared {len(events)} events for the calendar.")
        print("First 5 prepared events:")
        display(events[:5]) # Display first 5 events to check format
    else:
        print("Error: Columns 'FECHA' or 'MODELO' not found in the DataFrame. Please check your Excel file and adjust the column names in the code if they are different.")
        events = []
else:
    print("DataFrame 'df' is not loaded or is empty. Cannot prepare events.")
    events = []
