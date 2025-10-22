import os
from typing import List
from chromadb import Client, Settings
from chromadb.utils import embedding_functions
import google.generativeai as genai

# Ortam ve modeller
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY bulunamadı.")

genai.configure(api_key=API_KEY)

EMBEDDING_MODEL = "text-multilingual-embedding-002"
GENERATION_MODEL = "gemini-2.0-flash"
CHROMA_COLLECTION_NAME = "akbank_rag_collection"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")
os.makedirs(CHROMA_PATH, exist_ok=True)

# Embedding class
class GeminiEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __call__(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            try:
                response = genai.embed_content(model=EMBEDDING_MODEL, content=text)
                embeddings.append(getattr(response, "embedding", None) or response["embedding"])
            except Exception as e:
                print(f"⚠️ Embedding hatası: {e}")
                embeddings.append([0.0]*768)
        return embeddings

# --------------------------
# ✅ 1. setup_vector_db
def setup_vector_db(file_path: str):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        chunks = [text[i:i+1500] for i in range(0, len(text), 1200)]
        client = Client(Settings(persist_directory=CHROMA_PATH))
        embed_func = GeminiEmbeddingFunction()
        collection = client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            embedding_function=embed_func
        )
        if collection.count() < len(chunks):
            ids = [f"doc_{i}" for i in range(len(chunks))]
            collection.add(documents=chunks, ids=ids)
        print("✅ Vektör DB kuruldu")
    except Exception as e:
        print(f"❌ setup_vector_db hatası: {e}")

# --------------------------
# ✅ 2. rag_query
def rag_query(query: str) -> str:
    try:
        client = Client(Settings(persist_directory=CHROMA_PATH))
        embed_func = GeminiEmbeddingFunction()
        collection = client.get_collection(
            name=CHROMA_COLLECTION_NAME,
            embedding_function=embed_func
        )
        results = collection.query(query_texts=[query], n_results=7, include=["documents","distances"])
        pairs = list(zip(results["documents"][0], results["distances"][0]))
        pairs.sort(key=lambda x: x[1])
        context = "\n---\n".join([p[0] for p in pairs[:5]])
        prompt = f"""Sen bir uzman bilgi asistanısın.
KULLANICI SORUSU:
{query}
BAĞLAM:
{context}
Uzay alanında son derece uzmansın. Tatmin edici cevaplar verirsin.
Veri setinde olmayan sorular için kısa cevaplar üretirsin.
"""
        model = genai.GenerativeModel(GENERATION_MODEL)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ RAG sorgusu hatası: {e}"
