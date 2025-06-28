import os
import json
import zipfile
import pandas as pd
import numpy as np
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static

st.set_page_config(layout="wide")
st.title("🛍️ Brazilian E-Commerce Dashboard (Olist)")

# --- Function to download from Kaggle if not already ---
@st.cache_resource
def download_kaggle_dataset():
    dataset_path = "data/olist_orders_dataset.csv"
    if not os.path.exists(dataset_path):
        st.info("📦 Downloading dataset from Kaggle...")
        
        # Write kaggle.json from secrets
       

        kaggle_dict = dict(st.secrets["kaggle_json"])
        os.makedirs(os.path.expanduser("~/.kaggle"), exist_ok=True)
        with open(os.path.expanduser("~/.kaggle/kaggle.json"), "w") as f:
            json.dump(kaggle_dict, f)
        os.chmod(os.path.expanduser("~/.kaggle/kaggle.json"), 0o600)
        # Create data folder
        os.makedirs("data", exist_ok=True)

        # Download and extract
        os.system("kaggle datasets download -d olistbr/brazilian-ecommerce -p data")
        with zipfile.ZipFile("data/brazilian-ecommerce.zip", "r") as zip_ref:
            zip_ref.extractall("data")
        st.success("✅ Dataset downloaded and extracted.")

# --- Load data ---
@st.cache_data
def load_data():
    orders = pd.read_csv("data/olist_orders_dataset.csv", parse_dates=['order_purchase_timestamp', 'order_delivered_customer_date'])
    reviews = pd.read_csv("data/olist_order_reviews_dataset.csv")
    products = pd.read_csv("data/olist_products_dataset.csv")
    cat_map = pd.read_csv("data/product_category_name_translation.csv")
    geo = pd.read_csv("data/olist_geolocation_dataset.csv")
    products = products.merge(cat_map, on="product_category_name", how="left")
    return orders, reviews, products, geo

# --- Run download once ---
download_kaggle_dataset()
orders, reviews, products, geo = load_data()

# --- Sidebar navigation ---
section = st.sidebar.radio("📋 Select Section", [
    "Order Status", "Review Scores", "Top Categories", "Delivery Performance", "Customer Location"
])

# --- Order Status Overview ---
if section == "Order Status":
    st.subheader("📦 Order Status Overview")
    status_counts = orders["order_status"].value_counts()
    fig, ax = plt.subplots()
    sns.barplot(y=status_counts.index, x=status_counts.values, ax=ax)
    ax.set_title("Order Status Distribution")
    st.pyplot(fig)

# --- Review Scores ---
elif section == "Review Scores":
    st.subheader("🌟 Review Score Distribution")
    fig2 = px.histogram(reviews, x="review_score", nbins=5, title="Customer Review Scores")
    st.plotly_chart(fig2)

# --- Top Product Categories ---
elif section == "Top Categories":
    st.subheader("🏆 Top Product Categories")
    top_cats = products["product_category_name_english"].value_counts().head(10)
    fig3 = px.bar(top_cats, orientation="h", title="Top 10 Product Categories")
    st.plotly_chart(fig3)

# --- Delivery Performance ---
elif section == "Delivery Performance":
    st.subheader("⏱ Delivery Time Analysis")
    orders['delivery_days'] = (orders['order_delivered_customer_date'] - orders['order_purchase_timestamp']).dt.days
    delivery = orders[orders['delivery_days'].notna()]
    fig4 = px.histogram(delivery, x="delivery_days", nbins=30, title="Delivery Days Distribution")
    st.plotly_chart(fig4)

# --- Customer Geolocation Heatmap ---
elif section == "Customer Location":
    st.subheader("🌍 Customer Geolocation Heatmap")
    geo_sample = geo[['geolocation_lat', 'geolocation_lng']].dropna().sample(3000)
    m = folium.Map(location=[-14.2, -51.9], zoom_start=4)
    HeatMap(geo_sample.values.tolist(), radius=8).add_to(m)
    folium_static(m)
