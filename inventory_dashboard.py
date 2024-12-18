import streamlit as st
import sqlite3
import pandas as pd
import altair as alt

# Display the title
st.markdown("<h1 style='text-align: center;'>Inventory Dashboard</h1>", unsafe_allow_html=True)

# Connect to the chomazone database
conn = sqlite3.connect('./Databases/chomazone.db')
cursor = conn.cursor()

# Fetch items for the product filter
cursor.execute("SELECT item_name FROM inventory")
items = [row[0] for row in cursor.fetchall()]

# Product filter
selected_product = st.selectbox('Product', ['All'] + items)

# Fetch stock data for bar graph
if selected_product == 'All':
    cursor.execute("SELECT item_name, units, strftime('%Y-%m', datetime) as month FROM inventory")
else:
    cursor.execute("SELECT item_name, units, strftime('%Y-%m', datetime) as month FROM inventory WHERE item_name = ?", (selected_product,))
stock_data = cursor.fetchall()
df_stock = pd.DataFrame(stock_data, columns=['item_name', 'units', 'month'])

# Calculate total units based on the filtered data
total_units = df_stock['units'].sum()

# Fetch value of stocks based on the filtered data
if selected_product == 'All':
    cursor.execute("SELECT SUM(buying_price * units) FROM inventory")
else:
    cursor.execute("SELECT SUM(buying_price * units) FROM inventory WHERE item_name = ?", (selected_product,))
value_of_stocks = cursor.fetchone()[0] or 0

# Fetch inventory turnover rate based on the filtered data
if selected_product == 'All':
    cursor.execute("SELECT SUM(units) FROM orders")
else:
    cursor.execute("SELECT SUM(units) FROM orders WHERE item = ?", (selected_product,))
total_units_sold = cursor.fetchone()[0] or 0
inventory_turnover_rate = total_units_sold / total_units if total_units > 0 else 0

# Fetch top 5 items with 20+ units for horizontal bar graph
cursor.execute("SELECT item_name, units FROM inventory WHERE units >= 20 ORDER BY units ASC LIMIT 5")
top_items_data = cursor.fetchall()
df_top_items = pd.DataFrame(top_items_data, columns=['item_name', 'units'])

# Create a bar graph with stock and months on the axes
stock_chart = alt.Chart(df_stock).mark_bar().encode(
    x='month:T',
    y='units:Q',
    color='item_name:N',
    tooltip=['item_name:N', 'units:Q', 'month:T']
).properties(
    width=400,
    height=400,
    title='Stock Over Time'
)

# Create a horizontal bar graph for top 5 items with 20+ units
top_items_chart = alt.Chart(df_top_items).mark_bar().encode(
    x='units:Q',
    y=alt.Y('item_name:N', sort='-x'),
    tooltip=['item_name:N', 'units:Q']
).properties(
    width=400,
    height=400,
    title='Top 5 Items with 20+ Units'
)

# Display the metrics in styled cards
st.markdown("""
    <style>
    .card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 20px;
    }
    .card h3 {
        margin: 0;
        font-size: 24px;
        color: #333;
    }
    .card p {
        margin: 0;
        font-size: 18px;
        color: #666;
    }
    </style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="card">
        <h3>Total Units</h3>
        <p>{total_units:,.2f}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <h3>Value of Stocks (KSh)</h3>
        <p>{value_of_stocks:,.2f}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card">
        <h3>Inventory Turnover Rate</h3>
        <p>{inventory_turnover_rate:.2f}</p>
    </div>
    """, unsafe_allow_html=True)

# Display the bar graphs side by side
col1, col2 = st.columns(2)

with col1:
    st.altair_chart(stock_chart, use_container_width=True)

with col2:
    st.altair_chart(top_items_chart, use_container_width=True)

# Close the database connection
conn.close()