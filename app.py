import streamlit as st
from streamlit_option_menu import option_menu

# Custom CSS for the app
st.markdown("""
    <style>
    /* Sidebar customization */
    .css-1d391kg {
        background-color: #e6f7ff !important;
    }
    .css-1d391kg .css-1v3fvcr {
        color: #007acc !important;
    }
    .css-1d391kg .css-1v3fvcr:hover {
        color: #005b99 !important;
    }
    .css-1d391kg .css-1v3fvcr:active {
        color: #003d66 !important;
    }
    .css-1d391kg .css-1v3fvcr:focus {
        color: #003d66 !important;
    }
    .css-1d391kg .css-1v3fvcr:visited {
        color: #003d66 !important;
    }
    .css-1d391kg .css-1v3fvcr:focus-visible {
        color: #003d66 !important;
    }
    /* Main content customization */
    .css-18e3th9 {
        background-color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar with navigation
with st.sidebar:
    st.header("MARTIN'S CHOMA ZONE")
    page = option_menu(menu_title="Main Menu", 
                       options=["Home", "Sales Dashboard", "Inventory Dashboard", "Orders", "Inventory"],
                       icons=['cast', 'currency-dollar', 'database-fill', 'credit-card', 'database-add'])
                       

# Navigation logic
if page == "Home":
    st.title("Welcome to Martin's Choma Zone")
    st.write("This is the home page.")
elif page == "Sales Dashboard":
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

    chart = alt.Chart(df_melted).mark_line().encode(
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
elif page == "Inventory Dashboard":
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
    x=alt.X('month:T', title='Month'),
    y=alt.Y('units:Q', title='Units'),
    color='item_name:N',
    column='item_name:N',
    tooltip=['item_name:N', 'units:Q', 'month:T']
).properties(
    width=200,
    height=400,
    title='Stock Over Time'
).configure_legend(
    orient='bottom'
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
elif page == "Orders":
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
   
elif page == "Inventory":
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