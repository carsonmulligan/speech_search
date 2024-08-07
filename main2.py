import os
import streamlit as st
from openai import OpenAI
import requests
import streamlit.components.v1 as components

# Load secrets from Streamlit's secrets management
openai_api_key = st.secrets["general"]["OPENAI_API_KEY"]

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

st.title("Ask GPT-4o-mini")

# User input
user_question = st.text_input("Ask a question:")

if st.button("Submit"):
    with st.spinner("Getting response...."):
        response = client.chat_completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_question}
            ]
        )
        answer = response.choices[0].message['content']
        st.write("Response:")
        st.write(answer)
