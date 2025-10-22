# GenAI-RAG-Space-Chatbot
RAG Tabanlı Chatbot Projesi

🖥️ Canlı Demo
🔗 https://huggingface.co/spaces/AhmetHakanSerdemSude/AKBANKchatbot

🌌 🤖 Akbank GenAI Giriş Bootcamp RAG Space Chatbot
Bu proje, Generative AI Giriş Bootcamp kapsamında geliştirilmiş Türkçe bir RAG (Retrieval-Augmented Generation) tabanlı bilgi asistanıdır.
Chatbot, verilen bir metin dosyasındaki (TXT) bilgileri kullanarak, kullanıcı sorularına Gemini 2.0 Flash modeliyle yanıt verir.
Uygulama Streamlit tabanlı bir web arayüzü üzerinden çalışır.

📋 Proje Hakkında
Bu proje, Google Gemini API, ChromaDB, ve LangChain benzeri RAG pipeline yapısı kullanarak geliştirilmiştir.
Kullanıcıdan alınan bir soru, vektör veritabanı (ChromaDB) üzerinden en alakalı metin parçalarıyla eşleştirilir.
Sonrasında, bu bilgiler Gemini LLM modeli tarafından işlenerek doğal Türkçe bir yanıt üretilir. Proje, veri kaynağı olarak bilgi_kaynagi.txt adlı bir uzay, bilim veya genel bilgi metin dosyasını kullanır. Böylece, kullanıcı “Dünyanın yüzde kaçı sudur?”, “Evren nasıl oluşmuştur?”, “En küçük gezegen hangisidir?” gibi sorulara anlamlı yanıtlar alabilir.

🧠 Kullanılan Teknolojiler
Google Gemini API	(Embedding ve metin üretimi)
ChromaDB	(Vektör tabanlı belge arama)
Streamlit	(Web arayüzü)
dotenv	(API anahtarı yönetimi)
tiktoken	(Metin tokenizasyonu ve parçalama)
Python (typing, os)	(Uygulama mantığı ve sistem yönetimi)

⚙️ Proje Yapısı
.
├── app.py                 # Streamlit tabanlı web arayüzü
├── rag_functions.py       # RAG pipeline ve embedding fonksiyonları
├── bilgi_kaynagi.txt      # Bilgi kaynağı (uzay veya konuya özel metin)
├── requirements.txt       # Python bağımlılıkları
├── .env                   # API KEY
└── README.md              # Bu dosya

🚀 Kurulum
1. Sanal Ortam Oluşturun (Opsiyonel ama önerilir)
python3 -m venv venv
venv\Scripts\activate

2. Gerekli Paketleri Yükleyin
pip install -r requirements.txt

3. API KEY'inizi Ayarlayın
Proje kök dizinine .env adlı bir dosya oluşturun ve aşağıdaki satırı ekleyin:
GEMINI_API_KEY=your_google_api_key_here
🔑 Google API Key: Google AI Studio
 üzerinden alınabilir.

4. Bilgi Kaynağını Ekleyin
Kök dizine bilgi_kaynagi.txt adlı bir dosya oluşturun.
Bu dosya, chatbot’un yanıt vereceği metin bilgisini içermelidir (örnek: uzay, bilim, teknoloji konuları).

5. Uygulamayı Çalıştırın
streamlit run app.py
Uygulama tarayıcınızda otomatik olarak açılacaktır:
👉 http://localhost:8501

💡 Nasıl Çalışır?
Veri Okuma: bilgi_kaynagi.txt dosyası okunur.
Parçalama: Metin tiktoken ile 1000 token’lık bölümlere ayrılır.
Embedding: Her parça, Gemini text-embedding-004 modeliyle vektöre dönüştürülür.
Vektör Veritabanı: Embedding’ler ChromaDB koleksiyonunda saklanır.
Sorgu: Kullanıcının sorusu embedding’e çevrilir ve en benzer 3 metin parçası bulunur.
Yanıt Üretimi: Gemini 2.0 Flash modeli, bu bağlamı kullanarak doğal bir yanıt oluşturur.

⚠️ Önemli Notlar
.env dosyasını asla GitHub’a yüklemeyin.
İlk çalıştırmada embedding işlemi birkaç dakika sürebilir.
bilgi_kaynagi.txt dosyası çok büyükse işlemler yavaşlayabilir.
ChromaDB klasörü (chroma_db/) otomatik olarak oluşturulur.

Örnek Sorular
“Işık yılı ne anlama gelir?”
“En büyük yıldız hangisidir?”
“Kara delikler nasıl oluşur?”
“Mars’ta yaşam mümkün mü?”

📝 Lisans
Bu proje eğitim amaçlıdır ve ticari kullanım için tasarlanmamıştır.

🤝 Katkıda Bulunma
Öneri, hata raporu veya geliştirme isteği için GitHub üzerinden issue açabilirsiniz.
Yıldız 🌟 bırakmayı unutmayın!
