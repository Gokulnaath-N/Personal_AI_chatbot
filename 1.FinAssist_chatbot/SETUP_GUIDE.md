# FinAssist Setup Guide

## 🚀 Quick Start

Your FinAssist application is now running! Follow these steps to get the AI assistant working:

### 1. Access the Application
- Open your browser and go to: `http://localhost:8504`
- The application should be running with a beautiful dashboard interface

### 2. Configure AI Assistant
1. **Go to Settings**: Click on "Settings" in the sidebar navigation
2. **Enter Your Token**: In the "HuggingFace Token" field, enter your token:
   ```
   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
   ```
3. **Save Settings**: The token will be automatically saved
4. **Go to Chat Assistant**: Navigate to "Chat Assistant" in the sidebar

### 3. Start Chatting
- The AI model will load automatically
- Ask questions like:
  - "How do I create a budget?"
  - "What are the basics of investing?"
  - "How can I save money as a student?"

## 🔧 Configuration Options

### Model Settings
- **Model ID**: `ibm-granite/granite-3.3-2b-instruct` (default)
- **Device**: Choose "auto", "cpu", or "cuda" based on your system
- **Persona**: Select your financial knowledge level

### Memory Management
- Use `/remember key=value` to store information
- Use `/clear` to clear all memories
- Ask "what do you remember?" to see stored data

## 🎯 Features Available

### Dashboard
- ✅ Financial metrics and KPIs
- ✅ Interactive charts
- ✅ Recent activity feed
- ✅ Professional UI design

### Chat Assistant
- ✅ AI-powered financial advice
- ✅ Personalized responses
- ✅ Memory system
- ✅ Secure token management

### Settings
- ✅ Secure configuration
- ✅ Model customization
- ✅ Memory management tools

## 🛠️ Troubleshooting

### If AI Model Won't Load:
1. Check your internet connection
2. Verify your HuggingFace token is correct
3. Ensure you have enough RAM (8GB+ recommended)
4. Try using "cpu" instead of "auto" for device setting

### If Application Won't Start:
1. Make sure all packages are installed in the virtual environment
2. Check that the virtual environment is activated
3. Verify Python version compatibility

## 📞 Support

If you encounter any issues:
1. Check the terminal output for error messages
2. Ensure all dependencies are properly installed
3. Verify your HuggingFace token is valid

## 🎉 Success!

Once configured, you'll have a fully functional AI-powered financial assistant with:
- Professional dashboard interface
- Secure AI chat capabilities
- Memory system for personalized responses
- Beautiful, modern UI design

Enjoy your FinAssist experience! 💰✨
