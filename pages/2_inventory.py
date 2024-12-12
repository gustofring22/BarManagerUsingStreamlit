import streamlit as st
import sqlite3

# Connect to the chomazone database
conn = sqlite3.connect('chomazone.db')
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

# Create an inventory form
with st.form(key='inventory_form'):
    item = st.text_input('Item')
    units_bought = st.number_input('Units bought', min_value=1, step=1)
    buying_price = st.number_input('Buying price', min_value=0.0)
    selling_price = st.number_input('Selling price', min_value=0.0)

    submit_button = st.form_submit_button(label='Add to Inventory')

# Handle form submission
if submit_button:
    # Check if the item already exists
    cursor.execute("SELECT units FROM inventory WHERE item_name = ?", (item,))
    result = cursor.fetchone()
    
    if result:
        # Item exists, update the units
        current_units = result[0]
        new_units = current_units + units_bought
        cursor.execute("UPDATE inventory SET units = ?, buying_price = ?, selling_price = ? WHERE item_name = ?", (new_units, buying_price, selling_price, item))
    else:
        # Item does not exist, insert a new record
        cursor.execute("INSERT INTO inventory (item_name, units, buying_price, selling_price) VALUES (?, ?, ?, ?)", (item, units_bought, buying_price, selling_price))
    
    conn.commit()
    st.write(f'{units_bought} units of {item} have been added to the inventory.')

conn.close()