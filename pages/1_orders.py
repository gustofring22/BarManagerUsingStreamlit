import streamlit as st
import sqlite3
from datetime import datetime

def create_database_and_fetch_items():
    # Connect to the chomazone database
    conn = sqlite3.connect('./Databases/chomazone.db')
    cursor = conn.cursor()

    # Create inventory table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        item_name TEXT PRIMARY KEY,
        units INTEGER,
        buying_price REAL,
        selling_price REAL
    )
    ''')

    # Create orders table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT,
        units INTEGER,
        price_per_unit REAL,
        total REAL,
        datetime TEXT
    )
    ''')

    # Fetch items from the inventory table
    cursor.execute("SELECT item_name FROM inventory")
    items = [row[0] for row in cursor.fetchall()]

    return conn, cursor, items

def form_creation(items, cursor):
    with st.form(key='order_form'):
        item = st.selectbox('Item to be ordered', items)
        
        # Fetch the selling price for the selected item
        cursor.execute("SELECT selling_price FROM inventory WHERE item_name = ?", (item,))
        price_per_unit = cursor.fetchone()[0]
        
        units = st.number_input('Units ordered', min_value=1, step=1)
        price_per_unit_input = st.number_input('Price per unit', value=price_per_unit, min_value=0.0, step=0.01)
        
        # Submit button
        submit_button = st.form_submit_button(label='Calculate Total')

    return item, units, price_per_unit_input, submit_button

# Main code
conn, cursor, items = create_database_and_fetch_items()
item, units, price_per_unit_input, submit_button = form_creation(items, cursor)


# Calculate and display the total if the form is submitted
if submit_button:
    # Check the available units in the inventory
    cursor.execute("SELECT units FROM inventory WHERE item_name = ?", (item,))
    available_units = cursor.fetchone()[0]
    
    if units > available_units:
        st.error(f'Not enough units in inventory. Available units: {available_units}')
    else:
        total = units * price_per_unit_input
        st.write(f'Total for {units} units of {item} at {price_per_unit_input} per unit is {total}')
        
        # Insert the order into the database with the current date and time
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
        INSERT INTO orders (item, units, price_per_unit, total, datetime)
        VALUES (?, ?, ?, ?, ?)
        ''', (item, units, price_per_unit_input, total, current_datetime))
        
        # Deduct the ordered units from the inventory
        new_units = available_units - units
        cursor.execute("UPDATE inventory SET units = ? WHERE item_name = ?", (new_units, item))
        
        # Commit the transaction
        conn.commit()
        st.success('Order added successfully!')

# Close the database connection
conn.close()
