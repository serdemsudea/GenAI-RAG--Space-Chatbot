import streamlit as st
from rag_functions import setup_vector_db, rag_query
import os

# ----------------------------
# 1️⃣ Kullanıcı veri dosyası
DATA_FILE_PATH = "bilgi_kaynagi.txt"  # Space’e ekleyeceğin veri dosyası

if not os.path.exists(DATA_FILE_PATH):
    st.error(f"HATA: '{DATA_FILE_PATH}' dosyası bulunamadı. Lütfen Space’e yükleyin.")
else:
    try:
        setup_vector_db(DATA_FILE_PATH)
    except Exception as e:
        st.error(f"Veritabanı kurulum hatası: {e}")

# ----------------------------
# 2️⃣ Web Arayüzü
st.title("Akbank GenAI Bootcamp RAG Space Chatbot")
st.caption("Gemini 2.0 Flash + ChromaDB ile TXT dosyası tabanlı RAG Chatbot")

# session_state ile mesaj geçmişini tut
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Merhaba! Bilgi kaynağımdaki konular hakkında bana sorular sorabilirsiniz."}
    ]

# önceki mesajları göster
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# kullanıcıdan girdi al
if prompt := st.chat_input("Sorunuzu buraya yazın..."):
    # kullanıcı mesajını kaydet ve göster
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # model yanıtını al
    with st.spinner("Düşünüyorum..."):
        response = rag_query(prompt)

    # yanıtı kaydet ve göster
    st.session_state["messages"].append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)
