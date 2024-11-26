import streamlit as st
import json
import requests
from datetime import datetime
import random
import os
from groq_handler import GroqHandler
from image_handler import ImageHandler

# Page configuration
st.set_page_config(
    page_title="ChatMeme.ai - Your Sarcastic Meme Companion",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #2e2e2e;
    }
    .bot-message {
        background-color: #0e48a1;
    }
    .sidebar .element-container {
        background-color: #2e2e2e;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "current_meme" not in st.session_state:
    st.session_state.current_meme = None

# Initialize handlers
groq_handler = GroqHandler(st.secrets["groq_api_key"])
image_handler = ImageHandler()

def generate_meme_response(prompt: str) -> str:
    """Generate a meme response using Groq for analysis and ImageHandler for creation."""
    try:
        # Step 1: Analyze the meme request
        analysis = groq_handler.analyze_meme_request(prompt)
        if not analysis:
            return "I couldn't understand what kind of meme you want. Try being more specific about the subject and what makes it funny!"
            
        # Step 2: Create the meme
        search_query = analysis["search_queries"][0]  # Use first search query
        caption = groq_handler.format_meme_text(analysis["captions"][0])  # Format first caption
        
        meme_bytes = image_handler.create_meme(search_query, caption)
        if meme_bytes:
            st.session_state.current_meme = meme_bytes
            return f"Here's your meme about {analysis['subjects'][0]}! 😎"
        else:
            return "I couldn't find a good image for your meme. Try a different subject or description!"

    except Exception as e:
        print(f"Error generating meme: {str(e)}")
        return "Oops! Something unexpected happened. Please try again with a simpler meme idea!"

def generate_response(prompt: str, play_it_safe: bool = False) -> str:
    """Generate text response using Groq for better formatting."""
    if not play_it_safe:
        # Sarcastic responses for non-play-it-safe mode
        sarcastic_responses = [
            "Oh, you want me to do something? How about... no. Try adding #play-it-safe if you're serious.",
            "Sorry, I only speak in memes, and I don't see a #play-it-safe tag. Try again!",
            "Error 404: Cooperation not found. Have you tried using #play-it-safe?",
            "I'm as helpful as a chocolate teapot right now. Use #play-it-safe for actual help.",
            "I'm currently in 'maximum sass' mode. Use #play-it-safe to switch to 'actually helpful' mode."
        ]
        return random.choice(sarcastic_responses)

    # Use Grok for regular responses
    API_KEY = st.secrets["groq_api_key"]
    API_URL = "https://api.x.ai/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    system_message = """You are MemeGPT, a specialized AI that excels in creating memes and jokes. 
    Your responses should be creative, funny, and meme-worthy. Focus on generating humorous content 
    and meme suggestions."""

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                "model": "grok-beta",
                "stream": False,
                "temperature": 0.7
            }
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return "Sorry, I'm having trouble being creative right now. Try again!"

# Sidebar with chat history
with st.sidebar:
    st.header("💬 Chat History")
    if st.button("Clear History", key="clear"):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.session_state.current_meme = None
        st.experimental_rerun()
    
    for chat in st.session_state.chat_history:
        with st.container():
            st.text(f"🕒 {chat['timestamp']}")
            st.text(f"💭 {chat['query'][:50]}...")

# Main chat interface
st.title("🤖 MemeGPT - Your Sarcastic Meme Companion")
st.markdown("""
    Welcome to MemeGPT! I'm your sarcastic meme-generating companion.
    - Use `#play-it-safe` at the end of your message for meme generation
    - Try prompts like: "Create a meme about coding frustrations #play-it-safe"
    - Without `#play-it-safe`, expect maximum sass!
""")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and st.session_state.current_meme:
            st.image(st.session_state.current_meme)
            st.session_state.current_meme = None

# Chat input
if prompt := st.chat_input("What's on your mind? (Use #play-it-safe for memes)"):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Check if #play-it-safe is in the prompt
    play_it_safe = "#play-it-safe" in prompt.lower()
    
    # Generate response
    if play_it_safe and "meme" in prompt.lower():
        response = generate_meme_response(prompt)
    else:
        response = generate_response(prompt, play_it_safe)
    
    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(response)
        if st.session_state.current_meme:
            st.image(st.session_state.current_meme)
            st.session_state.current_meme = None
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Add to sidebar chat history
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.chat_history.append({
        "timestamp": timestamp,
        "query": prompt
    })
