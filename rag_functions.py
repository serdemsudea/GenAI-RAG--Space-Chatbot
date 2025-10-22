import os
from typing import List
from dotenv import load_dotenv
from chromadb import Client, Settings
from chromadb.utils import embedding_functions
from google import genai

# -----------------------------------------------------------
# 0. ORTAM AYARLARI
# -----------------------------------------------------------

# .env'den API anahtarını yükle
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY bulunamadı. Lütfen .env dosyanı kontrol et.")

# Model ve veritabanı sabitleri
EMBEDDING_MODEL = "text-embedding-004"
GENERATION_MODEL = "gemini-2.5-flash"
CHROMA_COLLECTION_NAME = "akbank_rag_collection"
CHROMA_PATH = "chroma_db"


# -----------------------------------------------------------
# 1. GEMINI EMBEDDING SINIFI (ChromaDB Uyumu)
# -----------------------------------------------------------

class GeminiEmbeddingFunction(embedding_functions.EmbeddingFunction):
    """
    Google Gemini'yi kullanarak ChromaDB için embedding üretir.
    Chroma, her __call__ çağrısında metin listesini gönderir.
    """
    def __init__(self, api_key: str, model_name: str = EMBEDDING_MODEL):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def __call__(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            try:
                response = self.client.models.embed_content(
                    model=self.model_name,
                    contents=text,
                    task_type="RETRIEVAL_DOCUMENT"
                )

                # Yeni Google SDK bazen dict bazen data objesi döndürür
                emb = response.get("embedding") if isinstance(response, dict) else response.data[0].embedding
                embeddings.append(emb)
            except Exception as e:
                print(f"⚠️ Embedding hatası: {e}")
                embeddings.append([0.0] * 768)  # Boş embedding fallback
        return embeddings


# -----------------------------------------------------------
# 2. METİN PARÇALAMA FONKSİYONU
# -----------------------------------------------------------

def text_splitter(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Tiktoken kullanarak metni belirli büyüklükte parçalara ayırır.
    """
    from tiktoken import get_encoding
    encoding = get_encoding("cl100k_base")
    tokens = encoding.encode(text)

    chunks = []
    i = 0
    while i < len(tokens):
        chunk_tokens = tokens[i:i + chunk_size]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)

        if i + chunk_size >= len(tokens):
            break
        i += chunk_size - chunk_overlap

    return chunks


# -----------------------------------------------------------
# 3. VEKTÖR VERİTABANI KURULUMU
# -----------------------------------------------------------

def setup_vector_db(file_path: str):
    """
    TXT dosyasını okur, parçalara böler, embedding oluşturur ve ChromaDB'ye kaydeder.
    """
    try:
        print("📦 Vektör veritabanı kuruluyor...")

        # 1. Dosyayı oku
        with open(file_path, "r", encoding="utf-8") as f:
            full_text = f.read()

        # 2. Metni parçalara ayır
        chunks = text_splitter(full_text)
        if not chunks:
            raise ValueError("Metin parçalanamadı veya dosya boş.")

        # 3. Chroma Client ve embedding fonksiyonunu başlat
        client = Client(Settings(persist_directory=CHROMA_PATH))
        gemini_embed_func = GeminiEmbeddingFunction(api_key=API_KEY, model_name=EMBEDDING_MODEL)

        # 4. Koleksiyon oluştur veya al
        collection = client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            embedding_function=gemini_embed_func
        )

        # 5. Eksik verileri ekle
        if collection.count() < len(chunks):
            print(f"{len(chunks)} parça ekleniyor...")
            ids = [f"doc_{i}" for i in range(len(chunks))]
            collection.add(documents=chunks, ids=ids)
            print("✅ Veritabanı kurulumu tamamlandı.")
        else:
            print("ℹ️ Veritabanı zaten mevcut, yeni veri eklenmedi.")

    except Exception as e:
        print(f"❌ Veritabanı kurulum hatası: {e}")
        print("Lütfen API anahtarınızın (.env) doğru olduğundan ve internet bağlantınızın aktif olduğundan emin olun.")


# -----------------------------------------------------------
# 4. RAG SORGULAMA FONKSİYONU
# -----------------------------------------------------------

def rag_query(query: str) -> str:
    """
    Kullanıcı sorgusuna göre ChromaDB'den bağlam çeker ve Gemini ile yanıt üretir.
    """
    try:
        # 1. Client'ları başlat
        client = Client(Settings(persist_directory=CHROMA_PATH))
        gemini_client = genai.Client(api_key=API_KEY)
        gemini_embed_func = GeminiEmbeddingFunction(api_key=API_KEY, model_name=EMBEDDING_MODEL)

        # 2. Koleksiyonu al
        collection = client.get_collection(
            name=CHROMA_COLLECTION_NAME,
            embedding_function=gemini_embed_func
        )

        # 3. Sorguya en yakın 3 belgeyi bul
        results = collection.query(query_texts=[query], n_results=3)
        context = "\n---\n".join(results["documents"][0])

        # 4. Prompt hazırla
        prompt = f"""
        Aşağıdaki BAĞLAM'ı kullanarak kullanıcı sorusuna kapsamlı bir yanıt ver.
        Eğer bağlam yetersizse, "Üzgünüm, bu konuda elimde yeterli veri bulunmamaktadır." de.

        Kullanıcı sorusu: {query}

        --- BAĞLAM ---
        {context}
        """

        # 5. Yanıt üret
        response = gemini_client.models.generate_content(
            model=GENERATION_MODEL,
            contents=prompt,
        )

        return response.text

    except Exception as e:
        return f"❌ RAG sorgusu sırasında hata oluştu: {e}"


# -----------------------------------------------------------
# 5. ÖRNEK KULLANIM
# -----------------------------------------------------------

if __name__ == "__main__":
    # Örnek: veritabanını oluştur
    setup_vector_db("bilgi_kaynagi.txt")  # kendi txt dosyanın yolunu yaz

    # Örnek sorgu
    cevap = rag_query("Yapay zekanın bankacılıktaki uygulamaları nelerdir?")
    print("\n🤖 Yanıt:\n", cevap)
