# api_utils.py

import requests
import time
import streamlit as st  # Required for reading secrets securely

MISTRAL_API_KEY = st.secrets["MISTRAL_API_KEY"]  # Ensure you have this in your secrets.toml
MISTRAL_ENDPOINT = "https://api.mistral.ai/v1/chat/completions"

def retry_mistral_request(payload, headers, retries=3):
    for attempt in range(retries):
        try:
            response = requests.post(
                MISTRAL_ENDPOINT,
                json=payload,
                headers=headers,
                timeout=60  # Timeout in seconds
            )
            response.raise_for_status()
            return response
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError) as e:
            st.warning(f"⚠️ Retry {attempt + 1}/{retries} failed: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
    raise Exception("🚫 Max retries reached. API request failed.")

def generate_data_from_mistral(prompt: str) -> str:
    """
    Sends a prompt to Mistral and returns the assistant's response content.
    """
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistral-medium",  # Change if needed
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = retry_mistral_request(payload, headers)

    # Preview output for debugging
    print("✅ Mistral API response (first 500 chars):", response.text[:500])

    return response.json()["choices"][0]["message"]["content"]
