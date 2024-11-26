# ChatMeme.AI 🤖

A sophisticated meme generator powered by dual AI engines (Grok & Groq) with advanced computer vision capabilities. This app creates contextually aware, multi-panel meme collages with intelligent image selection and witty captions.

## 🌟 Features

- 🧠 Dual AI Processing
  - Grok AI for vision and context analysis
  - Groq (Llama3 8B) for structured responses and composition
  - Smart workflow separation
  - Intelligent decision making

- 🎯 Advanced Meme Creation
  - Multi-model approach for better results
  - DuckDuckGo image search integration
  - Precise composition control
  - Background removal capabilities

- 🖼️ Advanced Image Processing
  - Multi-panel meme collages (up to 3 images)
  - Smart image caching system
  - Resolution control (500-700 pixels)
  - Text placement optimization (max 400 pixels)
  - Multiple layout options (grid, vertical, horizontal)
  - Optional background removal
  - Professional text overlays with shadows

## 🔄 Workflow

1. **Initial Vision (Grok AI)**
   - Analyzes meme requests
   - Determines text content
   - Suggests visual composition
   - Extracts main subjects

2. **Image Search (DuckDuckGo)**
   - Precise image queries
   - Quality filtering
   - Smart caching
   - Error handling

3. **Composition (Groq)**
   - Layout decisions
   - Resolution control
   - Text placement
   - Background removal choices
   - Style suggestions

4. **Image Processing**
   - Resolution optimization
   - Layout application
   - Text overlay
   - Background removal (if requested)
   - Final composition

## 🛠️ Technical Stack

- **Framework:** Streamlit 1.40.1
- **AI Models:**
  - Grok AI (Vision & Context)
  - Groq/Llama3 8B (Composition)
- **Image Processing:**
  - Pillow 11.0.0
  - rembg 2.0.60
  - numpy 1.26.4
- **Search:**
  - duckduckgo-search 6.3.6
- **Other:**
  - requests 2.31.0
  - beautifulsoup4 4.12.2

## 🚀 Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure API keys in `.streamlit/secrets.toml`:
   ```toml
   GROK_API_KEY = "your-grok-api-key"
   GROQ_API_KEY = "your-groq-api-key"
   ```
4. Run the app:
   ```bash
   streamlit run app.py
   ```

## 🔐 API Keys Required

- **Grok API Key:** For vision and context analysis
- **Groq API Key:** For composition decisions and text generation

## 📝 Usage

1. Enter your meme idea in the text input
2. The app will:
   - Analyze your request using Grok
   - Find relevant images
   - Determine optimal composition with Groq
   - Create a professional meme
3. Use the sidebar toggle to enable/disable background removal
4. View your generated meme and chat history

## 🔧 Development

The project uses a modular architecture:
- `app.py`: Main Streamlit application
- `groq_handler.py`: Groq API integration and composition decisions
- `image_handler.py`: Image processing and meme creation
- `.streamlit/`: Configuration and secrets
- `cache/`: Image cache directory (auto-created)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Grok AI team for vision capabilities
- Groq team for the Llama3 model
- Streamlit for the web framework
- DuckDuckGo for image search API
