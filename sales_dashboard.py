import streamlit as st
import sqlite3
from datetime import date
import altair as alt
import pandas as pd

# Display the title
st.markdown("<h1 style='text-align: center;'>Sales Dashboard</h1>", unsafe_allow_html=True)

# Connect to the chomazone database
conn = sqlite3.connect('./Databases/chomazone.db')
cursor = conn.cursor()

# Fetch items for the product filter
cursor.execute("SELECT item_name FROM inventory")
items = [row[0] for row in cursor.fetchall()]

# Date filter
col4, col5, col6, col7 = st.columns(4)
with col4:
    start_date = st.date_input('Start date', value=date(2023, 1, 1))

with col5:
    end_date = st.date_input('End date', value=date.today())

with col6:
    selected_product = st.selectbox('Product', ['All'] + items)

with col7:
    time_period = st.selectbox('Time Period', ['Weekly', 'Monthly', 'Quarterly', 'Yearly'])

# Convert dates to strings for SQL query
start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

# Fetch total sales and profit based on the selected time period
if selected_product == 'All':
    cursor.execute('''
    SELECT orders.datetime, orders.item, SUM(total) as total_sales, SUM((inventory.selling_price - inventory.buying_price) * orders.units) as total_profit, SUM(orders.units) as total_units
    FROM orders
    JOIN inventory ON orders.item = inventory.item_name
    WHERE orders.datetime BETWEEN ? AND ?
    GROUP BY orders.datetime, orders.item
    ''', (start_date_str, end_date_str))
else:
    cursor.execute('''
    SELECT orders.datetime, orders.item, SUM(total) as total_sales, SUM((inventory.selling_price - inventory.buying_price) * orders.units) as total_profit, SUM(orders.units) as total_units
    FROM orders
    JOIN inventory ON orders.item = inventory.item_name
    WHERE orders.item = ? AND orders.datetime BETWEEN ? AND ?
    GROUP BY orders.datetime, orders.item
    ''', (selected_product, start_date_str, end_date_str))

data = cursor.fetchall()
df = pd.DataFrame(data, columns=['datetime', 'item', 'total_sales', 'total_profit', 'total_units'])
df['datetime'] = pd.to_datetime(df['datetime'])
df.set_index('datetime', inplace=True)

# Resample data based on the selected time period
if time_period == 'Weekly':
    df = df.resample('W-Mon').sum().reset_index().sort_values('datetime')
elif time_period == 'Monthly':
    df = df.resample('M').sum().reset_index().sort_values('datetime')
elif time_period == 'Quarterly':
    df = df.resample('Q').sum().reset_index().sort_values('datetime')
elif time_period == 'Yearly':
    df = df.resample('Y').sum().reset_index().sort_values('datetime')

# Create a comparative bar graph
df_melted = df.melt(id_vars=['datetime'], value_vars=['total_sales', 'total_profit'], var_name='Metric', value_name='Value')

chart = alt.Chart(df_melted).mark_bar().encode(
    x=alt.X('datetime:T', title='Date'),
    y=alt.Y('Value:Q', title='Amount (KSh)'),
    color='Metric:N',
    tooltip=['datetime:T', 'Value:Q']
).properties(
    width=800,
    height=400,
    title='Total Sales and Profit Over Time'
).configure_legend(
    orient='bottom'
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
        <h3>Total Sales (KSh)</h3>
        <p>{df['total_sales'].sum():,.2f}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <h3>Total Profit (KSh)</h3>
        <p>{df['total_profit'].sum():,.2f}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card">
        <h3>Number of Total Sales</h3>
        <p>{len(df)}</p>
    </div>
    """, unsafe_allow_html=True)



# Display the bar graph and DataFrame side by side
col1, col2 = st.columns(2, gap='small')

with col1:
    st.altair_chart(chart, use_container_width=True)

with col2:
    st.dataframe(df, height=250)

# Close the database connection
conn.close()