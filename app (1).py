
import streamlit as st
import requests
from datetime import datetime, timezone
from huggingface_hub import HfApi
import time
import pandas as pd
import plotly.express as px

# ------------------ Config ------------------
HF_TOKEN = st.secrets["HF_TOKEN"] if "HF_TOKEN" in st.secrets else "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"
HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "User-Agent": "Mozilla/5.0"
}
api = HfApi()

# ------------------ Helper Functions ------------------
def fetch_model_size_and_tensor_type(model_id):
    try:
        api_url = f"https://huggingface.co/api/models/{model_id}"
        response = requests.get(api_url, headers=HEADERS)
        if response.status_code != 200:
            return "N/A", "N/A"

        data = response.json()
        safetensors = data.get("safetensors", {})
        total_size = safetensors.get("total")
        parameters = safetensors.get("parameters", {})

        tensor_types = ", ".join(parameters.keys()) if parameters else "N/A"
        size_str = f"{round(total_size / 1e9, 1)}B" if total_size else "N/A"

        return size_str, tensor_types
    except Exception as e:
        return "N/A", "N/A"

# ------------------ Trending Models ------------------
def fetch_trending_models():
    try:
        models = list(api.list_models(filter="text-generation", sort="likes7d", limit=50, full=True))
    except Exception as e:
        return []

    filtered = []
    for model in models:
        try:
            info = api.model_info(model.modelId, files_metadata=True)
            task = info.pipeline_tag

            if task != "text-generation":
                continue

            license = info.card_data.get("license") if info.card_data else "N/A"
            downloads = info.downloads

            if license.lower() not in ["apache-2.0", "mit"]:
                continue

            parsed_size, tensor_type = fetch_model_size_and_tensor_type(model.modelId)

            try:
                if parsed_size.endswith("B"):
                    num_params = float(parsed_size[:-1])
                    if num_params > 26:
                        continue
            except:
                pass

            filtered.append({
                "Provider": info.author or model.modelId.split("/")[0],
                "Model": model.modelId,
                "License": license,
                "Downloads": downloads,
                "Size (B)": parsed_size,
                "Tensor Type": tensor_type,
                "Task": task or "N/A",
                "Link": f"https://huggingface.co/{model.modelId}"
            })

            if len(filtered) == 10:
                break

        except Exception as e:
            continue
    return filtered

# ------------------ Streamlit Dashboard ------------------
st.set_page_config(page_title="Trending LLM Dashboard", layout="wide")
st.title("🚀 Top 10 Trending Text Generation Models")
st.caption("Filtered by ≤26B parameters and Apache-2.0 or MIT license")

# Auto-refresh every 5 minutes
REFRESH_INTERVAL = 300  # seconds
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > REFRESH_INTERVAL:
    st.session_state.last_refresh = time.time()
    st.experimental_rerun()

with st.spinner("Fetching trending models..."):
    trending = fetch_trending_models()

timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
st.markdown(f"**Dashboard generated at:** {timestamp}")

if trending:
    df = pd.DataFrame(trending)

    # 📊 Downloads Chart
    fig = px.bar(df, x="Model", y="Downloads", color="Provider", title="Model Downloads by Provider")
    st.plotly_chart(fig, use_container_width=True)

    # 🎨 Metrics
    st.subheader("📈 Model Metrics")
    for i, row in df.iterrows():
        st.metric(label=row["Model"], value=row["Size (B)"], delta=f"{row['Downloads']:,} downloads")

    # 📁 Expanders for Details
    st.subheader("🔍 Model Details")
    for i, row in df.iterrows():
        with st.expander(f"{row['Model']} by {row['Provider']}"):
            st.write(f"**License:** {row['License']}")
            st.write(f"**Size:** {row['Size (B)']}")
            st.write(f"**Tensor Type:** {row['Tensor Type']}")
            st.write(f"**Task:** {row['Task']}")
            st.markdown(f"[🔗 View on Hugging Face]({row['Link']})")
else:
    st.warning("No trending models found or failed to fetch.")

st.button("🔄 Refresh Now", on_click=st.experimental_rerun)  # Manual refresh
