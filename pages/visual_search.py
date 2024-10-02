import streamlit as st
import openai

screenshot = 'https://www.aljazeera.com/wp-content/uploads/2024/10/iran-tel-aviv-israel-missiles-1727802640.jpg?resize=1920%2C1280&quality=80'

openai.api_key = st.secrets['openai_key']

response = openai.chat.completions.create(
    model='gpt-4o-mini',
    messages={
        'role':'user',
        'content':[
            {'type':'text', 'text':'Summarize the text in this image.'},
            {
                'type':'image_url',
                'image_url':{
                    'url':screenshot,
                }
            }
        ]
    }
)

st.write(response)
print(response)