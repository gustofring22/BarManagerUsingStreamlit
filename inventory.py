import streamlit as st
import sqlite3
from datetime import datetime

def create_database():
    try:
        # Connect to the chomazone database
        conn = sqlite3.connect('./Databases/chomazone.db')
        cursor = conn.cursor()

        # Create inventory table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            item_name TEXT PRIMARY KEY,
            units INTEGER,
            buying_price REAL,
            selling_price REAL,
            datetime TEXT
        )
        ''')

        # Commit the transaction
        conn.commit()

        return conn, cursor
    except sqlite3.Error as e:
        st.error(f"An error occurred: {e}")
        return None, None

def create_inventory_form(cursor):
    with st.form(key='inventory_form'):
        item = st.text_input('Item')
        units_bought = st.number_input('Units bought', min_value=1, step=1)
        buying_price = st.number_input('Buying price', min_value=0.0)
        selling_price = st.number_input('Selling price', min_value=0.0)

        submit_button = st.form_submit_button(label='Add to Inventory')

    if submit_button:
        # Check if the item already exists
        cursor.execute("SELECT units FROM inventory WHERE item_name = ?", (item,))
        result = cursor.fetchone()
        
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if result:
            # Item exists, update the units and datetime
            current_units = result[0]
            new_units = current_units + units_bought
            cursor.execute("UPDATE inventory SET units = ?, buying_price = ?, selling_price = ?, datetime = ? WHERE item_name = ?",
                           (new_units, buying_price, selling_price, current_datetime, item))
            st.write(f'Updated {item}: {units_bought} units added. Total units: {new_units}')
        else:
            # Item does not exist, insert a new record with datetime
            cursor.execute("INSERT INTO inventory (item_name, units, buying_price, selling_price, datetime) VALUES (?, ?, ?, ?, ?)",
                           (item, units_bought, buying_price, selling_price, current_datetime))
            st.write(f'{units_bought} units of {item} have been added to the inventory.')

        # Commit the transaction
        conn.commit()

# Main code
conn, cursor = create_database()
if conn and cursor:
    create_inventory_form(cursor)
    # Close the database connection
    conn.close()