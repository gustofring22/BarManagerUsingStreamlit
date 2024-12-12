import streamlit as st
import sqlite3

# Connect to the chomazone database
conn = sqlite3.connect('chomazone.db')
cursor = conn.cursor()

# Create orders table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item TEXT,
    units INTEGER,
    price_per_unit REAL,
    total REAL
)
''')

# Fetch items from the inventory table
cursor.execute("SELECT item_name FROM inventory")
items = [row[0] for row in cursor.fetchall()]

# Create a form
with st.form(key='order_form'):
    item = st.selectbox('Item to be ordered', items)
    
    # Fetch the selling price for the selected item
    cursor.execute("SELECT selling_price FROM inventory WHERE item_name = ?", (item,))
    price_per_unit = cursor.fetchone()[0]
    
    units = st.number_input('Units ordered', min_value=1, step=1)
    price_per_unit_input = st.number_input('Price per unit', value=price_per_unit, min_value=0.0, step=0.01)
    
    # Submit button
    submit_button = st.form_submit_button(label='Calculate Total')

# Calculate and display the total if the form is submitted
if submit_button:
    total = units * price_per_unit_input
    st.write(f'Total for {units} units of {item} at {price_per_unit_input} per unit is {total}')
    
    # Insert the order into the database
    cursor.execute('''
    INSERT INTO orders (item, units, price_per_unit, total)
    VALUES (?, ?, ?, ?)
    ''', (item, units, price_per_unit_input, total))
    
    # Commit the transaction
    conn.commit()
    

    st.success('Order added successfully!')


conn.close()