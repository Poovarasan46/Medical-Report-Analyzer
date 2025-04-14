# Medical-Report-Analyzer

Medical Report Analyzer is a web-based tool that allows users to upload medical PDFs, extract their content, and generate AI-powered insights using the Groq LLaMA3-70B model. Built with Python (Flask) and deployed on Vercel, it provides a smooth, fast, and privacy-friendly experience for quick medical data understanding.

---

## ✨ Features

- 🔍 Extracts disease diagnosis from uploaded reports
- 🧑 Detects patient details like name, age, gender
- 👨‍⚕️ Identifies doctor/hospital information
- 🧠 Uses **LLaMA3-70B** via Groq API for natural language analysis
- 💡 Provides patient instructions and next steps
- 🖥️ Clean and responsive frontend
- 🚀 Deployed on Vercel

---

## 📹 Demo

https://github.com/user-attachments/assets/b5b6fdee-1236-4753-8de1-220ed530eeb4

---

## 📁 Project Structure

<pre>Medical-report-analyzer-ai/ 
├── api/
│   └── index.py # ✅ Your Flask backend 
│ 
├── templates/
│   └── index.html # ✅ Your HTML frontend 
│ 
├── requirements.txt 
├── vercel.json 
├── .gitignore</pre>


---

## 📦 Installation (for local dev)

```bash
git clone https://github.com/Poovarasan46/Medical-Report-Analyzer.git
cd Medical-Report-Analyzer
cd api
pip install -r requirements.txt
python index.py
Then open: http://127.0.0.1:5000
```

## 🔐 Environment Variables (Vercel)

On [Vercel Dashboard](https://vercel.com/dashboard):
- `GROQ_API_KEY` – your Groq API key

The `.env` file is **not uploaded** to GitHub for security.

---

## 🚀 Deployment Steps

1. Push code to GitHub
2. Connect repo to [Vercel](https://vercel.com/)
3. In **Project Settings → Environment Variables**, add your_api_key
4. Deploy ✅

---

## 🛠️ Tech Stack

- **Python + Flask** – Backend framework for serving the app
- **HTML + JS + PDF.js** – Frontend interface and PDF processing
- **Vercel** – Hosting and deployment platform
- **Groq API (LLaMA3-70B)** – LLM for medical report analysis

---
## 🤝 Acknowledgements

- [Groq](https://groq.com/)
- [Vercel](https://vercel.com/)
- [OpenAI's Chat Completions API Format](https://platform.openai.com/docs/guides/chat)
- **You** — for reading this 👀

