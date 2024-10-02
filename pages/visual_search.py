import streamlit as st
from openai import OpenAI

screenshot = 'https://www.aljazeera.com/wp-content/uploads/2024/10/iran-tel-aviv-israel-missiles-1727802640.jpg?resize=1920%2C1280&quality=80'

client = OpenAI()

response = client.chat.completions.create(
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

print(response.choices[0])