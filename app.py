import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="AI Dataset Generator", layout="wide")

# === Custom Header ===
st.markdown("""
    <h1 style='text-align: center;'>📊 AI Dataset Generator</h1>
    <p style='text-align: center;'>Describe your dataset below and let AI generate it for you!</p>
""", unsafe_allow_html=True)

# === Instructions (Expander) ===
with st.expander("ℹ️ How It Works"):
    st.markdown("""
    1. Enter a detailed description of the dataset you want.
    2. Choose the number of records.
    3. The AI will generate data in batches if needed.
    """)

# === User Input (Side by Side Layout) ===
col1, col2 = st.columns(2)

with col1:
    user_prompt = st.text_area("📦 Dataset Description", placeholder="Example: Generate 100 fake customer records with name, email, phone")

with col2:
    record_count = st.slider("📈 Number of Records", min_value=10, max_value=1000, value=50, step=10)

# === Helper Functions ===
@st.cache_data(show_spinner=False)
def call_mistral_api(prompt):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {st.secrets['MISTRAL_API_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-medium",
        "messages": [{"role": "user", "content": prompt}],
    }
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def parse_json_output(text):
    try:
        json_start = text.find("[")
        json_end = text.rfind("]") + 1
        return json.loads(text[json_start:json_end])
    except Exception as e:
        st.warning(f"⚠️ Could not parse JSON: {e}")
        return None

# === Generate Dataset Button ===
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
                raw_response = call_mistral_api(batch_prompt)
                parsed = parse_json_output(raw_response)
                if parsed:
                    all_data.extend(parsed)
                    st.success(f"✅ Batch {i+1} done. Total: {len(all_data)} records.")
                else:
                    st.warning(f"⚠️ Batch {i+1} returned invalid JSON.")
            except Exception as e:
                st.error(f"🚫 API Error: {e}")

        if all_data:
            df = pd.DataFrame(all_data)
            st.success(f"🎉 Generated {len(df)} records.")
            st.dataframe(df.head(100))
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download CSV", csv, "dataset.csv", "text/csv")

# === Footer ===
st.markdown("<hr><center>Made OG_TECH</center>", unsafe_allow_html=True)
