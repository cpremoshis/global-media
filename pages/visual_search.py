import streamlit as st
from openai import OpenAI

#https://platform.openai.com/docs/guides/vision

screenshot = 'https://www.aljazeera.com/wp-content/uploads/2024/10/iran-tel-aviv-israel-missiles-1727802640.jpg?resize=1920%2C1280&quality=80'

client = OpenAI(api_key=st.secrets['openai_key'])

response = client.chat.completions.create(
  model="gpt-4o-mini",
  messages=[
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "Translate or transcribe the text in this image. Only return the translation or transcription."},
        {
          "type": "image_url",
          "image_url": {
            "url": screenshot,
          },
        },
      ],
    }
  ]
)

st.write(response.choices[0].message.content)