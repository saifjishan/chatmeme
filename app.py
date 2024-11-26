import streamlit as st
import json
import requests
from datetime import datetime
import random
import os
from image_handler import ImageHandler
from groq_handler import GroqHandler

# Page configuration
st.set_page_config(
    page_title="MemeGPT - Your Sarcastic Meme Companion",
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
image_handler = ImageHandler(
    scraper_api_key=st.secrets["SCRAPER_API_KEY"],
    grok_api_key=st.secrets["GROK_API_KEY"]
)

groq_handler = GroqHandler(
    api_key=st.secrets["GROQ_API_KEY"]
)

def generate_meme_response(prompt):
    """Generate a meme response using both Grok and Groq."""
    try:
        # Use Groq to analyze the request and format the response
        context_data = groq_handler.analyze_meme_request(prompt)
        
        if not context_data:
            return "I couldn't understand the meme request. Try another prompt!"
            
        # Search for images based on the queries
        image_urls = []
        for query in context_data["search_queries"]:
            results = image_handler.search_images(query, num_images=1)
            if results:
                image_urls.append(results[0])
            if len(image_urls) >= 3:
                break
        
        if not image_urls:
            return "I couldn't find any suitable images for your meme. Try a different prompt!"

        # Use Grok to analyze images and refine captions if needed
        captions = context_data["captions"][:len(image_urls)]
        
        # Create the meme collage
        meme_image = image_handler.create_collage(
            image_urls,
            captions
        )
        
        if meme_image:
            st.session_state.current_meme = meme_image
            return "Here's your meme collage! How do you like it? 😎"
        else:
            return "I created the meme concept but had trouble with the image processing. Try again!"

    except Exception as e:
        st.error(f"Error generating meme: {str(e)}")
        return "Sorry, I encountered an error while creating your meme. Please try again!"

def generate_response(prompt, play_it_safe=False):
    """Generate text response using Groq for better formatting."""
    if not play_it_safe:
        # Use existing sarcastic responses
        sarcastic_responses = [
            "Oh, you want me to do something? How about... no. Try adding #play-it-safe if you're serious.",
            "Sorry, I only speak in memes, and I don't see a #play-it-safe tag. Try again!",
            "Error 404: Cooperation not found. Have you tried using #play-it-safe?",
            "I'm as helpful as a chocolate teapot right now. Use #play-it-safe for actual help.",
            "I'm currently in 'maximum sass' mode. Use #play-it-safe to switch to 'actually helpful' mode."
        ]
        return random.choice(sarcastic_responses)

    try:
        # Use Groq for structured responses
        completion = groq_handler.client.chat.completions.create(
            model=groq_handler.model,
            messages=[
                {"role": "system", "content": "You are a witty and creative meme assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return "Sorry, I'm having trouble being creative right now. Try again!"

# Sidebar with chat history
with st.sidebar:
    st.header("💬 Chat History")
    if st.button("Clear History", key="clear"):
        st.session_state.messages = []
        st.session_state.chat_history = []
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
    - Without `#play-it-safe`, expect maximum sass!
    - Try prompts like: "Create a meme about the struggles of coding #play-it-safe"
""")

# Display chat messages and handle meme display
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and st.session_state.current_meme:
            st.image(st.session_state.current_meme, caption="Generated Meme")
            st.session_state.current_meme = None  # Clear the current meme after displaying

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
            st.image(st.session_state.current_meme, caption="Generated Meme")
            st.session_state.current_meme = None
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Add to sidebar chat history
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.chat_history.append({
        "timestamp": timestamp,
        "query": prompt
    })
