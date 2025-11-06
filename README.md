# 🎓 CU AI Assistant  

An intelligent academic assistant built for **Chandigarh University** students.  
It uses **Retrieval-Augmented Generation (RAG)** with **Gemini 2.5 Flash**  
to answer queries from PDFs, timetables, and study materials.  

---

## 🚀 Features  
- 🧠 AI Answers from CU course PDFs & timetables  
- 💬 Chat memory saved locally  
- ⚙️ Re-index PDFs anytime  
- 🎨 Modern Tkinter UI  
- 🔍 FAISS vector search + Sentence Transformer embeddings  

---

## 🧩 Tech Stack  
- **Python 3.12+**  
- **CustomTkinter** (UI)  
- **Sentence-Transformers** (`all-MiniLM-L6-v2`)  
- **Google Generative AI (Gemini 2.5 Flash)**  
- **FAISS** / Pickle for vector DB  

---

## 🛠️ Setup  

```bash
git clone https://github.com/<your-username>/CU_Assistant.git
cd CU_Assistant
pip install -r requirements.txt

Create .env from .env.example and add your Gemini API key.

Run the app:

python main.py

CU_Assistant/
├── data/               # PDFs, embeddings, chat DB
├── modules/            # AI, retriever, embedder, etc.
├── ui/                 # CustomTkinter UI
├── scripts/            # Indexing scripts
├── assets/             # Logo, icons
├── main.py             # App entry point
└── requirements.txt

MIT License © 2025 Purusattam Mandal

---

### 🧠 6. Double-Check Before Pushing  

Run this safety check:  

```bash
find . -type f -name "*.py" -exec grep -H "GEMINI_KEY" {} \;
