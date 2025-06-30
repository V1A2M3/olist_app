import streamlit as st
import numpy as np
import pickle
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences

# --- Load trained assets ---
model = tf.keras.models.load_model("model.h5")
tokenizer = pickle.load(open("tokenizer.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))

# --- Parameters ---
max_len = 100

# --- Streamlit UI ---
st.title("🛒 Olist Review Satisfaction Predictor")

review_text = st.text_area("✍️ Customer Review Comment", height=150)
price = st.number_input("💰 Product Price", 0.0, 10000.0, step=1.0)
freight = st.number_input("🚚 Freight Value", 0.0, 1000.0, step=0.5)
shipping = st.number_input("📦 Shipping Delay (days)", 0, 60, step=1)

if st.button("Predict Satisfaction"):
    # --- Prepare inputs ---
    seq = tokenizer.texts_to_sequences([review_text])
    padded = pad_sequences(seq, maxlen=max_len)

    struct_input = scaler.transform([[price, freight, shipping]])

    # --- Predict ---
    pred = model.predict([padded, struct_input])[0][0]
    label = "😊 Satisfied (4–5 stars)" if pred > 0.5 else "😠 Not Satisfied (1–3 stars)"

    st.markdown(f"## Prediction: {label}")
    st.write(f"**Confidence:** {pred:.2%}")
