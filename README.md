# 📊 AI Dataset Generator

A simple AI-powered tool that generates synthetic datasets based on your natural language prompt using the Mistral API.

Built with [Streamlit](https://streamlit.io), this app lets users describe the kind of data they want (e.g. "Generate 100 fake patient records") and get downloadable structured datasets in CSV format.

---

## 🚀 Live Demo

👉 [Try the app](https://your-username-your-repo.streamlit.app/) ← *(Replace with your actual link)*

---

## ✨ Features

- 🧠 Natural language to structured dataset
- 📈 Supports 10 to 1000+ records
- 📥 Download CSV of results
- 🔁 Generates in batches for large datasets
- 🛠️ Works for any domain: health, finance, e-commerce, etc.

---

## 🖼 Example Prompts

```text
Generate 50 fake sales records with product name, price, and quantity sold.
Generate 100 startup profiles with name, sector, funding, and founding year.
Generate 200 fake hospital patients with name, age, diagnosis, and phone number.

📦 Installation
bash
Copy
Edit
git clone https://github.com/your-username/ai-dataset-generator.git
cd ai-dataset-generator
pip install -r requirements.txt
streamlit run app.py

🔐 API Key Setup
Create a .streamlit/secrets.toml file:
toml
Copy
Edit
MISTRAL_API_KEY = "your_mistral_api_key"
Alternatively, set this in your Streamlit Cloud secrets.

🛠 Tech Stack
🧠 Mistral API (via Together or direct)

🎈 Streamlit

📊 Pandas

🌐 Requests

🤝 Contribute
Found a bug or have a feature request? Feel free to open an issue or submit a PR.

📄 License
MIT License © 2025 justDlabguy