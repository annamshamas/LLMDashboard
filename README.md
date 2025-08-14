# Trending LLM Dashboard

This Streamlit app displays the top trending text-generation models from Hugging Face, filtered by license and model size.

## Features
- Auto-refresh every 5 minutes
- Manual refresh button
- Interactive downloads chart
- Metrics and expandable model details

## Setup
1. Clone the repository:
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

2. Add your Hugging Face token to `.streamlit/secrets.toml`:
```toml
HF_TOKEN = "your_huggingface_token_here"
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the app locally:
```bash
streamlit run app.py
```

## Deploy on Streamlit Cloud
1. Push the project to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Click "New app" and connect your GitHub repo
4. Select `app.py` as the main file and deploy

Enjoy your dashboard! 🚀