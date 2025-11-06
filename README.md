🧠 About CU_Assistant

CU_Assistant (Chandigarh University Assistant) is a locally deployable AI-powered learning companion that helps students instantly find answers from their course materials.

The system uses Retrieval-Augmented Generation (RAG) — combining semantic search (using FAISS & Sentence Transformers) with local text generation (GPT-2/Ollama).

Students can upload academic PDFs (like Python, Design and Analysis of Algorithms, AI Tools, and PL/SQL labs), and the assistant retrieves and explains answers with supporting citations — all in a chat-style Tkinter interface.

✨ Features

📚 Upload & index multiple academic PDFs

🔍 Retrieve answers contextually using semantic similarity

⚙️ Uses DAA & AI algorithms like BFS, DFS, A*, Quick Sort, and 0/1 Knapsack for retrieval ranking

💬 Tkinter-based Chat UI with real-time responses

🗃️ SQLite database for chat history and analytics

📊 Matplotlib dashboard for visualizing query trends

🧩 Fully offline & extendable (Flask, WhatsApp Bot, or CU website integration)

🧰 Tech Stack
Category	Tools / Libraries
Language	Python 3
GUI	Tkinter
Embeddings	Sentence Transformers
Vector Store	FAISS / Chroma
Text Generation	GPT-2 (Transformers)
Database	SQLite
Visualization	Matplotlib
Algorithms	BFS, DFS, A*, Quick Sort, 0/1 Knapsack
🚀 Project Goals

To create a personalized academic assistant aligned with CU’s MCA AI/ML curriculum

To integrate key lab concepts from Python, DAA, AI Tools, and PL/SQL

To later scale into a web app or WhatsApp chatbot using local or cloud-hosted RAG systems

🧑‍💻 Future Enhancements

🗣️ Add speech-to-text and voice output

🌐 Create Flask API + deploy on CU internal server

🤖 Integrate with WhatsApp via Twilio

🧮 Add subject-wise performance analytics
