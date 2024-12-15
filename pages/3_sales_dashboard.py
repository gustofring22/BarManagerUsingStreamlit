import streamlit as st
import sqlite3
from datetime import date
import altair as alt
import pandas as pd

# Connect to the chomazone database
conn = sqlite3.connect('./Databases/chomazone.db')
cursor = conn.cursor()

# Fetch items for the product filter
cursor.execute("SELECT item_name FROM inventory")
items = [row[0] for row in cursor.fetchall()]

# Date filter
col4, col5, col6 = st.columns(3)
with col4:
    start_date = st.date_input('Start date', value=date(2023, 1, 1))

with col5:
    end_date = st.date_input('End date', value=date.today())

with col6:
    selected_product = st.selectbox('Product', ['All'] + items)

# Convert dates to strings for SQL query
start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

# Time period filter
time_period = st.selectbox('Time Period', ['Weekly', 'Monthly', 'Quarterly', 'Yearly'])

# Fetch total sales and profit based on the selected time period
if selected_product == 'All':
    cursor.execute('''
    SELECT orders.datetime, SUM(total) as total_sales, SUM((inventory.selling_price - inventory.buying_price) * orders.units) as total_profit
    FROM orders
    JOIN inventory ON orders.item = inventory.item_name
    WHERE orders.datetime BETWEEN ? AND ?
    GROUP BY orders.datetime
    ''', (start_date_str, end_date_str))
else:
    cursor.execute('''
    SELECT orders.datetime, SUM(total) as total_sales, SUM((inventory.selling_price - inventory.buying_price) * orders.units) as total_profit
    FROM orders
    JOIN inventory ON orders.item = inventory.item_name
    WHERE orders.item = ? AND orders.datetime BETWEEN ? AND ?
    GROUP BY orders.datetime
    ''', (selected_product, start_date_str, end_date_str))

data = cursor.fetchall()
df = pd.DataFrame(data, columns=['datetime', 'total_sales', 'total_profit'])
df['datetime'] = pd.to_datetime(df['datetime'])

# Resample data based on the selected time period
if time_period == 'Weekly':
    df = df.resample('W-Mon', on='datetime').sum().reset_index().sort_values('datetime')
elif time_period == 'Monthly':
    df = df.resample('M', on='datetime').sum().reset_index().sort_values('datetime')
elif time_period == 'Quarterly':
    df = df.resample('Q', on='datetime').sum().reset_index().sort_values('datetime')
elif time_period == 'Yearly':
    df = df.resample('Y', on='datetime').sum().reset_index().sort_values('datetime')

# Create a bar graph
chart = alt.Chart(df).mark_bar().encode(
    x='datetime:T',
    y='value:Q',
    color='variable:N',
    tooltip=['datetime:T', 'value:Q']
).transform_fold(
    ['total_sales', 'total_profit'],
    as_=['variable', 'value']
).properties(
    width=800,
    height=400
)

# Display the metrics in cards
st.title("Sales Dashboard")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total Sales (KSh)", value=f"{df['total_sales'].sum():,.2f}")

with col2:
    st.metric(label="Total Profit (KSh)", value=f"{df['total_profit'].sum():,.2f}")

with col3:
    st.metric(label="Number of Total Sales", value=len(df))

# Display filters
st.subheader("Filters")
st.write(f"Date range: {start_date} to {end_date}")
st.write(f"Product: {selected_product}")

# Display the bar graph
st.altair_chart(chart)

# Close the database connection
conn.close()