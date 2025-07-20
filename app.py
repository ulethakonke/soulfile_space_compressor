import streamlit as st
import pandas as pd
from PIL import Image
import sqlite3
import os

def init_db():
    conn = sqlite3.connect('soulfile.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS files
                 (name TEXT, path TEXT, compressed_size REAL, domain TEXT)''')
    conn.commit()
    return conn

def load_symbols():
    if not os.path.exists('symbols.csv'):
        default_symbols = pd.DataFrame({
            'symbol': ['α', 'β', 'γ', 'Δ'],
            'physics': ['alpha_particle', 'beta_decay', 'gamma_ray', 'delta_enthalpy'],
            'biology': ['alpha_helix', 'beta_sheet', 'GABA', 'delta_variant'],
            'economics': ['alpha_return', 'beta_volatility', 'gamma_hedging', 'gdp_delta'],
            'triggers': ['radiation, protein, ROI', 'decay, keratin, risk', 'MeV, neurotransmitter, options', 'H=, COVID, %']
        })
        default_symbols.to_csv('symbols.csv', index=False)
    return pd.read_csv('symbols.csv')

def compress_image(file, quality=85):
    img = Image.open(file)
    compressed_path = f"compressed_{file.name}"
    img.save(compressed_path, optimize=True, quality=quality)
    return compressed_path, os.path.getsize(compressed_path)/1024

def process_file(uploaded_file, conn, symbols):
    if uploaded_file.type.startswith('image/'):
        compressed_path, size = compress_image(uploaded_file)
        domain = "image"
    else:
        compressed_path = uploaded_file.name
        size = len(uploaded_file.getvalue())/1024
        domain = "document"
    
    conn.execute("INSERT INTO files VALUES (?, ?, ?, ?)", 
                (uploaded_file.name, compressed_path, size, domain))
    conn.commit()
    return compressed_path, size

def main():
    st.set_page_config(page_title="Soulfile Vault", layout="wide")
    st.title("🧠 Soulfile Vault")
    
    conn = init_db()
    symbols = load_symbols()
    
    uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True)
    
    if uploaded_files:
        for file in uploaded_files:
            with st.spinner(f"Processing {file.name}..."):
                path, size = process_file(file, conn, symbols)
                st.success(f"Compressed {file.name} to {size:.1f}KB")
    
    if st.button("View Compressed Files"):
        files = pd.read_sql("SELECT * FROM files", conn)
        st.dataframe(files)

if __name__ == "__main__":
    main()