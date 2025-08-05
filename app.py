import streamlit as st
import pandas as pd
import plotly.express as px

# CSS: Paksa tema terang + teks kontras
st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }
    div[data-testid="stSidebar"] {
        background-color: #f8f9fa;
        color: #000000;
    }
    .css-1d391kg {  /* Untuk teks pada card seperti st.success/info */
        color: #000 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Dashboard Penjualan Supermarket",
    page_icon="🛒",
    layout="wide"
)

# --- FUNGSI UNTUK MEMBACA DATA ---
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Time'] = pd.to_datetime(df['Time']).dt.time
    return df

df = load_data('data/SuperMarket Analysis.csv')

# --- HEADER ---
st.markdown("""
    <h1 style='text-align: center; color: #264653;'>📊 Dashboard Analisis Penjualan Supermarket</h1>
    <hr style='border: 1px solid #264653;'>
""", unsafe_allow_html=True)

# --- SIDEBAR UNTUK FILTER ---
st.sidebar.header("🎚 Filter Data:")

city = st.sidebar.multiselect("🗺 Pilih Kota:", options=df["City"].unique(), default=df["City"].unique())
customer_type = st.sidebar.radio("🧍 Tipe Customer:", options=('Semua', 'Member', 'Normal'))
product_line = st.sidebar.multiselect("📦 Pilih Lini Produk:", options=df["Product line"].unique(), default=df["Product line"].unique())

df_selection = df.query("City == @city & Product line == @product_line")
if customer_type != 'Semua':
    df_selection = df_selection[df_selection['Customer type'] == customer_type]

# --- DOWNLOAD BUTTON ---
csv = df_selection.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Data (CSV)", data=csv, file_name='filtered_supermarket_data.csv', mime='text/csv')

# --- METRIK UTAMA ---
total_sales = int(df_selection["Sales"].sum())
average_rating = round(df_selection["Rating"].mean(), 1)
star_rating = "⭐" * int(round(average_rating, 0))

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
        <div style='background-color:#dff5ec; padding:20px; border-radius:10px; text-align:center;'>
            <h3 style='color:#264653;'>💰 Total Penjualan</h3>
            <h1 style='color:#2A9D8F;'>US ${total_sales:,}</h1>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div style='background-color:#fff0e6; padding:20px; border-radius:10px; text-align:center;'>
            <h3 style='color:#264653;'>⭐ Rata-rata Rating</h3>
            <h1 style='color:#F4A261;'>{average_rating} {star_rating}</h1>
        </div>
    """, unsafe_allow_html=True)
    
# --- INSIGHT SINGKAT ---
st.subheader("📌 Insight Singkat")
col1, col2, col3 = st.columns(3)
sales_by_product_line = df_selection.groupby("Product line")["Sales"].sum().sort_values()
df_selection['Hour'] = pd.to_datetime(df_selection['Time'], format='%H:%M:%S').dt.hour
sales_by_hour = df_selection.groupby("Hour")["Sales"].sum().reset_index()

with col1:
    st.success(f"📦 Produk Terlaris: {sales_by_product_line.idxmax()}")
with col2:
    st.info(f"⏰ Jam Tertinggi: {sales_by_hour.loc[sales_by_hour['Sales'].idxmax(), 'Hour']}:00")
with col3:
    st.warning(f"💳 Pembayaran Favorit: {df_selection['Payment'].mode()[0]}")

st.markdown("---")

# --- VISUALISASI ---
sales_by_product_line_df = sales_by_product_line.reset_index()
sales_by_product_line_df.columns = ['Product line', 'Sales']

fig_product_sales = px.bar(
    sales_by_product_line_df,
    x="Sales",
    y="Product line",
    orientation="h",
    title="<b>Penjualan per Lini Produk</b>",
    color_discrete_sequence=["#F4A261"] * len(sales_by_product_line_df),
    template="plotly_white",
    labels={"Sales": "Total Penjualan", "Product line": "Lini Produk"}
)
fig_product_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False)
)

fig_hourly_sales = px.line(
    sales_by_hour,
    x="Hour",
    y="Sales",
    title="<b>Penjualan per Jam</b>",
    color_discrete_sequence=["#2A9D8F"],
    template="plotly_white",
)
fig_hourly_sales.update_layout(xaxis=dict(tickmode="linear"), plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(showgrid=False))

left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_product_sales, use_container_width=True)
right_column.plotly_chart(fig_hourly_sales, use_container_width=True)

# --- TABEL DATA ---
with st.expander("📄 Lihat Data Mentah (Sesuai Filter)"):
    st.dataframe(df_selection, use_container_width=True)

# --- FOOTER ---
st.markdown("<hr style='border-top: 1px solid #ccc;'>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align: center; color: #555;'>"
    "<small>🚀 Dibuat oleh <strong>Dhaifan Arijuddin (DS32B)</strong> dengan 😵❤ Streamlit | 2025</small>"
    "</div>",
    unsafe_allow_html=True
)
