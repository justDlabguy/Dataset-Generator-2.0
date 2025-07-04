import streamlit as st
import requests
import json
import pandas as pd

st.set_page_config(page_title="AI Dataset Generator", layout="centered")

st.title("📊 AI Dataset Generator")
st.write("""
Describe the dataset you want, and AI will generate it for you.

💡 Example:
*Generate 50 fake patient records with name, age, diagnosis, and address.*

⚠️ For large datasets, we generate in safe batches automatically.
""")

# === User Inputs ===
user_prompt = st.text_area("📦 Dataset Description", placeholder="e.g. Generate 50 sales records with product name, price, and quantity sold.")
record_count = st.slider("📈 Number of Records", min_value=10, max_value=1000, value=50, step=10)

# === Mistral API Call ===
def call_mistral_api(prompt):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {st.secrets['MISTRAL_API_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-medium",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        st.error("🚨 API timed out. Try fewer records or simplify your prompt.")
    except requests.exceptions.RequestException as err:
        st.error(f"🚫 API Error: {err}")
    return None

# === Parse JSON from AI Output ===
def parse_json_output(text):
    try:
        json_start = text.find("[")
        json_end = text.rfind("]") + 1
        json_data = text[json_start:json_end]
        return json.loads(json_data)
    except Exception as e:
        st.error(f"⚠️ Could not parse JSON: {e}")
        return None

# === Generate Dataset ===
if st.button("🚀 Generate Dataset"):
    if not user_prompt.strip():
        st.warning("Please enter a dataset description.")
    else:
        batch_size = 100 if record_count > 100 else record_count
        batches = (record_count + batch_size - 1) // batch_size
        st.info(f"Generating {record_count} records in {batches} batch(es)...")

        all_data = []

        for i in range(batches):
            batch_prompt = (
                f"{user_prompt.strip()}\n"
                f"Generate exactly {min(batch_size, record_count - len(all_data))} records in JSON array format. "
                f"Each record must contain at least 2 fields, such as 'name' and 'value'. "
                f"Output JSON only, no extra explanation."
            )
            raw_response = call_mistral_api(batch_prompt)
            if raw_response:
                parsed = parse_json_output(raw_response)
                if parsed:
                    all_data.extend(parsed)
                    st.success(f"✅ Batch {i+1} done. Total: {len(all_data)} records.")
                else:
                    st.warning(f"⚠️ Batch {i+1} returned invalid JSON.")
                    break
            else:
                st.warning(f"❗ Skipping Batch {i+1} due to timeout or connection error.")
                break

        if all_data:
            df = pd.DataFrame(all_data)
            st.success(f"🎉 Generated {len(df)} records.")
            st.dataframe(df.head(100))
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download CSV", csv, "dataset.csv", "text/csv")
