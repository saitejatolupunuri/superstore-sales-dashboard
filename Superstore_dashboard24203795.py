# --- Importing required libraries ---
import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(page_title="Superstore Dashboard", layout="wide")

# --- Load and Prepare Data for analysis ---
df = pd.read_csv("cleaned_superstore.csv")
df.columns = df.columns.str.strip()
df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
df['Sales'] = pd.to_numeric(df['Sales'].replace('[\$,]', '', regex=True), errors='coerce')
df['Profit'] = pd.to_numeric(df['Profit'].replace('[\$,]', '', regex=True), errors='coerce')
df['Discount'] = pd.to_numeric(df['Discount'], errors='coerce')

# --- Header ---
st.title("🏬 Superstore Sales Dashboard")
st.caption("Track sales performance, profitability, and regional trends across product categories.")

# --- Sidebar Filters (Usability only, NOT counted as advanced) ---
st.sidebar.header("Filters")
regions = st.sidebar.multiselect("Select Region", df['Region'].dropna().unique(), default=df['Region'].dropna().unique())
category = st.sidebar.selectbox("Select Category", df['Category'].dropna().unique())
subcats = df[df['Category'] == category]['Sub-Category'].dropna().unique()
subcategory = st.sidebar.multiselect("Select Sub-Category", subcats, default=subcats)

# --- Filtered Data ---
filtered_df = df[
    (df['Region'].isin(regions)) &
    (df['Category'] == category) &
    (df['Sub-Category'].isin(subcategory))
]

if filtered_df.empty:
    st.warning("No data available for selected filters.")
else:
    # --- Summary Metrics ---
    st.subheader("📌 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    total_sales = filtered_df['Sales'].sum()
    total_profit = filtered_df['Profit'].sum()
    total_orders = filtered_df['Order ID'].nunique()
    profit_margin = (total_profit / total_sales) * 100 if total_sales else 0

    col1.metric("💰 Total Sales", f"${total_sales:,.0f}")
    col2.metric("📈 Total Profit", f"${total_profit:,.0f}")
    col3.metric("🧾 Unique Orders", total_orders)
    col4.metric("📊 Profit Margin", f"{profit_margin:.1f}%")

    st.divider()

    # --- Monthly Trend ---
    st.subheader("📅 Monthly Sales and Profit Trend")
    trend = filtered_df.groupby(filtered_df['Order Date'].dt.to_period('M')).agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
    trend['Order Date'] = trend['Order Date'].astype(str)
    fig_trend = px.line(trend, x='Order Date', y=['Sales', 'Profit'], markers=True, template='plotly_white')
    fig_trend.update_layout(title_text="Monthly Sales and Profit", title_x=0.5)
    st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown("> **Insight:** Sales and profit trends reveal operational variability across months, suggesting shifts in cost efficiency or seasonal demand.")

    # --- Dynamic Metric Chart (Advanced Feature #1) ---
    st.subheader("🛠️ Advanced Feature: Dynamic Metric Selection")
    selected_metric = st.radio("Choose Metric to Compare Across Sub-Categories:", options=["Sales", "Profit", "Discount"])
    metric_data = filtered_df.groupby('Sub-Category')[selected_metric].sum().sort_values(ascending=False).reset_index()
    fig_dynamic = px.bar(metric_data, x='Sub-Category', y=selected_metric, color=selected_metric, template='plotly_white')
    fig_dynamic.update_layout(title_text=f"{selected_metric} by Sub-Category", title_x=0.5)
    st.plotly_chart(fig_dynamic, use_container_width=True)
    st.markdown("> **Insight:** High-revenue sub-categories may not align with profit leaders, indicating potential margin improvement opportunities.")

    # --- Scatter Plot: Discount vs Profit ---
    st.subheader("📉 Discount vs Profitability")
    scatter_data = filtered_df[['Discount', 'Profit', 'Sales', 'Product Name']].dropna()
    fig_scatter = px.scatter(
        scatter_data, x='Discount', y='Profit', size='Sales', color='Sales',
        hover_data=['Product Name'], template='plotly_white', color_continuous_scale='Viridis'
    )
    fig_scatter.update_layout(title_text="Discount Impact on Profitability", title_x=0.5)
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.markdown("> **Insight:** Profitability declines with increasing discount levels, emphasizing the importance of controlled promotional strategies.")

    # --- Map: State-wise Sales ---
    st.subheader("🗺️ Geographic Sales Performance")
    state_map = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
        'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
        'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
        'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
        'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
        'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
        'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
        'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
        'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
        'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
        'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT',
        'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
        'Wisconsin': 'WI', 'Wyoming': 'WY'
    }
    filtered_df['State Code'] = filtered_df['State'].map(state_map)
    map_data = filtered_df.groupby('State Code').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
    fig_map = px.choropleth(
        map_data, locations='State Code', locationmode='USA-states',
        color='Sales', scope='usa', hover_name='State Code',
        hover_data={'Sales': ':,.0f', 'Profit': ':,.0f'},
        color_continuous_scale='Teal', template='plotly_white'
    )
    fig_map.update_layout(title_text="State-Wise Sales Overview", title_x=0.5)
    st.plotly_chart(fig_map, use_container_width=True)
    st.markdown("> **Insight:** Sales and profit are concentrated in select states, highlighting regional performance disparities and growth potential.")

    # --- Conditional Content: Top Products (Advanced Feature #2) ---
    st.subheader("🎚️ Advanced Feature: Conditional Content")
    st.markdown("Enable this to view the Top 10 Products by Sales.")
    if st.checkbox("Show Top 10 Products"):
        top_products = filtered_df.groupby('Product Name')['Sales'].sum().sort_values(ascending=False).head(10).reset_index()
        st.dataframe(top_products.style.highlight_max(axis=0))

    # --- Download Button ---
    st.download_button("📥 Download Filtered Data", filtered_df.to_csv(index=False), "filtered_data.csv")
