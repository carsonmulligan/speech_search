import os
import streamlit as st
from openai import OpenAI
import requests
import streamlit.components.v1 as components

# Load secrets from Streamlit's secrets management
openai_api_key = st.secrets["general"]["OPENAI_API_KEY"]
perplexity_api_key = st.secrets["general"]["PERPLEXITY_API_KEY"]

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Language dictionary for language codes to language names
language_dict = {
    "zh-cn": "中文",
    "en": "English",
    "es": "español",
    "fr": "français",
    "de": "Deutsch",
    "ja": "日本語",
    "pt": "português"
}

# Function to translate text using OpenAI
def translate_text(text, target_language):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Translate the following text to {language_dict[target_language]}: {text}"}
        ]
    )
    translated_text = response.choices[0].message.content.strip()
    return translated_text

# Function to search for top political speeches
def search_speeches(target_language, target_country):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {perplexity_api_key}"
    }
    language_name = language_dict.get(target_language, target_language)
    query = f"Return YouTube links with {language_name} speeches from leaders in {target_country}. Preferred longer than 20 minutes - complete speeches in {language_name}. Always return a valid YouTube link with ID."
    translated_query = translate_text(query, target_language)
    payload = {
        "model": "llama-3-sonar-small-32k-online",
        "messages": [
            {
                "role": "system", "content": "Be precise and concise."
            },
            {
                "role": "user", "content": translated_query
            }
        ]
    }
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        try:
            data = response.json()
            return data.get('choices', [])
        except ValueError as e:
            print(f"Error decoding JSON from response: {e}")
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")
        return []

# Title of the app
st.title("Target Language, Target Country, Complete Speeches Finder")

# Input for language and country
target_language = st.selectbox("Select Language", list(language_dict.keys()), format_func=lambda x: language_dict[x])
target_country = st.text_input("Enter Country")

# Initialize session state variables
if 'youtube_ids' not in st.session_state:
    st.session_state.youtube_ids = []
if 'current_video_index' not in st.session_state:
    st.session_state.current_video_index = 0
if 'query_count' not in st.session_state:
    st.session_state.query_count = 0

# Search button
if st.button("Search Speeches"):
    if st.session_state.query_count < 5:
        results = search_speeches(target_language, target_country)
        st.write(f"Results for political speeches in {target_country} in {language_dict[target_language]}:")
        youtube_ids = []
        for choice in results:
            video_url = choice['message']['content'].strip()
            video_id = video_url.split('v=')[-1]
            youtube_ids.append(video_id)
            st.write(f"Video URL: {video_url}")
            components.html(f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>', height=315)
            if len(youtube_ids) == 3:
                break
        st.session_state.youtube_ids = youtube_ids
        st.session_state.current_video_index = 0
        st.session_state.query_count += 1
    else:
        st.warning("You have reached the limit of 5 queries. Please restart the app to make more queries.")
