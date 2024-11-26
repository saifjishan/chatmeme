# ChatMeme.AI 🤖

A sophisticated meme generator powered by dual AI engines (Grok & Groq) with advanced computer vision capabilities. This app creates contextually aware, multi-panel meme collages with intelligent image selection and witty captions.

## 🌟 Features

- 🧠 Dual AI Processing
  - Grok AI for vision and context analysis
  - Groq (Llama3 8B) for structured responses
  - Enhanced caption generation
  - Smart context understanding

- 🎯 Intelligent Meme Creation
  - Multi-model approach for better results
  - Contextual image search and selection
  - Dynamic caption generation
  - Fallback mechanisms for reliability

- 🖼️ Advanced Image Processing
  - Multi-panel meme collages (up to 3 images)
  - Smart image caching system
  - Auto-enhancement with contrast and sharpness
  - Professional text overlay with shadow effects
  - Intelligent aspect ratio preservation
  - Optimized image quality and performance
  - Retry mechanisms for reliable image fetching

- 💬 Interactive Chat
  - Sarcastic responses by default
  - #play-it-safe tag for meme generation
  - Chat history tracking
  - Dark mode interface

## 🚀 Usage

1. Visit: https://chatmeme-ai.streamlit.app
2. Type your meme request with #play-it-safe tag
   Examples:
   - "Create a meme about coffee addiction in the morning #play-it-safe"
   - "Make a meme about programmers debugging code #play-it-safe"
   - "Generate a meme about cats being lazy #play-it-safe"
3. The app will:
   - Analyze your request using both AIs
   - Find relevant images
   - Create a meme collage
   - Add witty captions

## 🛠️ Development

### Requirements
- Python 3.11+
- Streamlit 1.40.1
- Requests 2.31.0
- Pillow 11.0.0
- BeautifulSoup4 4.12.2
- Groq 0.4.2

### Local Setup
```bash
# Clone the repository
git clone https://github.com/saifjishan/chatmeme.git

# Install dependencies
pip install -r requirements.txt

# Create cache directory for images
mkdir -p cache

# Run the app
streamlit run app.py
```

### Environment Variables
The app requires the following API keys:
- `GROK_API_KEY`: Your Grok AI API key
- `GROQ_API_KEY`: Your Groq API key
- `SCRAPER_API_KEY`: Your ScraperAPI key

For local development, create a `.streamlit/secrets.toml` file:
```toml
GROK_API_KEY = "your-grok-api-key"
GROQ_API_KEY = "your-groq-api-key"
SCRAPER_API_KEY = "your-scraper-api-key"
```

## 🔄 How It Works

1. **Request Analysis**
   - Groq analyzes the meme request and structures the response
   - Grok provides additional context understanding
   - Together they identify key subjects and generate search queries
   - Smart caption generation using both models

2. **Image Processing**
   - Intelligent image search with quality filters
   - Smart caching system for better performance
   - Auto-enhancement of images:
     - Contrast adjustment
     - Subtle sharpening
     - Aspect ratio preservation
   - Professional text effects:
     - Shadow effects for readability
     - Enhanced border rendering
     - Multiple font options

3. **Meme Generation**
   - Single image: Centered with AI-generated caption
   - Two images: Side by side with contextual captions
   - Three images: Equal width panels with thematic captions
   - Fallback mechanisms ensure reliability

## 🔒 Security

- API keys stored securely in `.streamlit/secrets.toml`
- Environment-specific configuration
- No sensitive data in version control
- Rate limiting and error handling

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

MIT License - feel free to use this project however you'd like!

## 🙏 Acknowledgments

- Grok AI for vision and context analysis
- Groq for the powerful Llama3 language model
- ScraperAPI for image search capabilities
- Streamlit for the awesome web framework
