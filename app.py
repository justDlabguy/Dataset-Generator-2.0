import streamlit as st
import pandas as pd
import json
import requests

st.set_page_config(page_title="AI Dataset Generator", layout="centered")
st.title("📊 AI Dataset Generator")

st.markdown("""
Describe any kind of dataset and let AI generate it for you.  
💡 Example: `Generate 100 fake sales records with product name, price, and quantity sold.`  
""")

# === Inputs ===
user_prompt = st.text_area("📦 Dataset Description", placeholder="e.g. Generate 100 fake customer records with name, age, and country.")
record_count = st.slider("📈 Number of Records", min_value=10, max_value=1000, value=100, step=10)

# === API secrets ===
MISTRAL_API_KEY = st.secrets["MISTRAL_API_KEY"]
MISTRAL_ENDPOINT = "https://api.mistral.ai/v1/chat/completions"

# === Cached API Request ===
@st.cache_data(show_spinner="📡 Calling Mistral AI...")
def call_mistral_api_cached(prompt):
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistral-medium",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(MISTRAL_ENDPOINT, headers=headers, json=data, timeout=30)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"API error {response.status_code}: {response.text}")

# === JSON parser ===
def parse_json_output(raw_text):
    try:
        start = raw_text.find("[")
        end = raw_text.rfind("]") + 1
        return json.loads(raw_text[start:end])
    except Exception as e:
        st.error(f"⚠️ Could not parse JSON: {e}")
        return None

# === Generate Dataset ===
if st.button("🚀 Generate Dataset"):
    if not user_prompt.strip():
        st.warning("Please enter a dataset description.")
    else:
        batch_size = 200 if record_count > 200 else record_count
        batches = (record_count + batch_size - 1) // batch_size
        st.info(f"Generating {record_count} records in {batches} batch(es)...")

        all_data = []

        for i in range(batches):
            batch_prompt = (
                f"{user_prompt.strip()}\n"
                f"Generate {min(batch_size, record_count - len(all_data))} records in JSON array format. "
                f"Each record should contain at least 2 fields."
            )
            try:
                raw_response = call_mistral_api_cached(batch_prompt)
                parsed = parse_json_output(raw_response)
                if parsed:
                    all_data.extend(parsed)
                    st.success(f"✅ Batch {i+1} done. Total: {len(all_data)} records.")
                else:
                    st.warning(f"⚠️ Batch {i+1} returned invalid JSON.")
            except Exception as err:
                st.error(f"🚫 API Error: {err}")

        if all_data:
            df = pd.DataFrame(all_data)
            st.success(f"🎉 Generated {len(df)} records.")
            st.dataframe(df.head(100))
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download CSV", csv, "dataset.csv", "text/csv")
