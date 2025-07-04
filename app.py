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

if st.button("🚀 Generate Dataset"):
    if not user_prompt.strip():
        st.warning("Please enter a dataset description.")
    else:
        remaining = record_count
        all_data = []
        batch_number = 1

        while remaining > 0:
            batch_size = min(200, remaining)  # Limit batch to 200 records max
            batch_prompt = (
                f"{user_prompt.strip()}\n"
                f"Generate {batch_size} records in JSON array format. "
                f"Each record must have at least 2 fields."
            )

            st.info(f"🚧 Generating Batch {batch_number} - Requesting {batch_size} records...")

            try:
                raw_response = call_mistral_api(batch_prompt)
                parsed = parse_json_output(raw_response)

                if parsed:
                    actual_count = len(parsed)
                    all_data.extend(parsed)
                    remaining -= actual_count

                    st.success(f"✅ Batch {batch_number} done: Got {actual_count} records. "
                               f"{remaining} remaining.")

                    # If fewer records returned than requested, retry automatically.
                    if actual_count < batch_size:
                        st.warning(f"⚠️ Batch {batch_number} returned fewer records than requested, retrying...")
                    else:
                        batch_number += 1
                else:
                    st.warning(f"⚠️ Batch {batch_number} returned invalid JSON, retrying...")
            except Exception as e:
                st.error(f"🚫 API Error during Batch {batch_number}: {e}")

        # ✅ Done: Show dataset
        if all_data:
            df = pd.DataFrame(all_data)
            st.success(f"🎉 Completed! Total Records: {len(df)}")
            st.dataframe(df.head(100))
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download CSV", csv, "dataset.csv", "text/csv")
