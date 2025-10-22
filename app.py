import streamlit as st
from rag_functions import setup_vector_db, rag_query
import os

# Veri setini ve DB yolunu tanımlayın
DATA_FILE_PATH = "bilgi_kaynagi.txt"

# 1. Uygulama Başlangıcında Veritabanı Kurulumu
# Bu, "Çözüm Mimarisi" ve "Çalışma Kılavuzu"nun bir parçasıdır.
if not os.path.exists(DATA_FILE_PATH):
    st.error(f"HATA: '{DATA_FILE_PATH}' dosyası bulunamadı. Lütfen ekleyin.")
else:
    try:
        # Vektör veritabanını kur/kontrol et
        setup_vector_db(DATA_FILE_PATH)
    except Exception as e:
        st.error(f"Veritabanı kurulum hatası: Lütfen API anahtarınızın (.env) doğru olduğundan ve internet bağlantınızın olduğundan emin olun. Hata: {e}")

# 2. Web Arayüzü (Streamlit)
st.title("Akbank GenAI Bootcamp RAG Space Chatbot")
st.caption("Gemini 2.5 Embedding ve ChromaDB ile TXT Dosyası tabanlı RAG Chatbot")

# Sohbet geçmişini saklamak için
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Merhaba! Bilgi kaynağımdaki konular hakkında bana sorular sorabilirsiniz."}]

# Sohbet geçmişini göster
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Kullanıcıdan girdi al
if prompt := st.chat_input():
    # Kullanıcı mesajını kaydet ve göster
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # RAG Pipeline'ı Çalıştır
    with st.spinner("Düşünüyorum..."):
        response = rag_query(prompt)
    
    # Asistan yanıtını kaydet ve göster
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)