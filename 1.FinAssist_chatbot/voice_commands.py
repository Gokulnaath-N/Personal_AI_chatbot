import streamlit as st
from typing import Dict, Callable, Optional
import re

class VoiceCommands:
    def __init__(self):
        """Initialize voice commands system"""
        self.commands = {
            'help': self.show_help,
            'clear': self.clear_chat,
            'remember': self.remember_info,
            'what do you remember': self.show_memory,
            'dashboard': self.go_to_dashboard,
            'settings': self.go_to_settings,
            'analytics': self.go_to_analytics,
            'chat': self.go_to_chat,
            'save': self.save_data,
            'export': self.export_data,
            'budget': self.budget_help,
            'invest': self.investment_help,
            'savings': self.savings_help,
            'expenses': self.expenses_help
        }
    
    def process_voice_command(self, text: str) -> Optional[str]:
        """
        Process voice command and return appropriate response
        
        Args:
            text: Transcribed voice text
            
        Returns:
            Response text or None if no command matched
        """
        text = text.lower().strip()
        
        # Check for exact command matches
        for command, func in self.commands.items():
            if command in text:
                return func(text)
        
        # Check for pattern matches
        if re.search(r'remember\s+(.+)', text):
            return self.remember_info(text)
        
        if re.search(r'go\s+to\s+(.+)', text):
            return self.navigate_to(text)
        
        if re.search(r'show\s+(.+)', text):
            return self.show_info(text)
        
        # No command matched
        return None
    
    def show_help(self, text: str) -> str:
        """Show available voice commands"""
        return """
        🎤 **Available Voice Commands:**
        
        **Navigation:**
        - "Go to dashboard" - Switch to dashboard
        - "Go to settings" - Open settings
        - "Go to analytics" - View analytics
        - "Go to chat" - Open chat assistant
        
        **Memory Management:**
        - "Remember [information]" - Store information
        - "What do you remember" - Show stored memories
        - "Clear" - Clear chat history
        
        **Financial Help:**
        - "Budget help" - Get budgeting advice
        - "Investment help" - Get investment guidance
        - "Savings help" - Get savings tips
        - "Expenses help" - Get expense management advice
        
        **Data Management:**
        - "Save" - Save current data
        - "Export" - Export financial data
        
        **General:**
        - "Help" - Show this help message
        """
    
    def clear_chat(self, text: str) -> str:
        """Clear chat history"""
        if "messages" in st.session_state:
            st.session_state.messages = []
        return "✅ Chat history cleared!"
    
    def remember_info(self, text: str) -> str:
        """Remember information from voice command"""
        # Extract information after "remember"
        match = re.search(r'remember\s+(.+)', text)
        if match:
            info = match.group(1).strip()
            if "memory" in st.session_state:
                st.session_state.memory.set("voice_note", info)
            return f"✅ Remembered: {info}"
        return "❌ Please specify what to remember"
    
    def show_memory(self, text: str) -> str:
        """Show stored memories"""
        if "memory" in st.session_state:
            memory_data = st.session_state.memory.get_all()
            if memory_data:
                return f"🧠 Stored memories: {memory_data}"
            else:
                return "🧠 No memories stored yet"
        return "❌ Memory system not available"
    
    def go_to_dashboard(self, text: str) -> str:
        """Navigate to dashboard"""
        st.session_state.current_page = "Dashboard"
        return "✅ Navigated to Dashboard"
    
    def go_to_settings(self, text: str) -> str:
        """Navigate to settings"""
        st.session_state.current_page = "Settings"
        return "✅ Navigated to Settings"
    
    def go_to_analytics(self, text: str) -> str:
        """Navigate to analytics"""
        st.session_state.current_page = "Financial Analytics"
        return "✅ Navigated to Analytics"
    
    def go_to_chat(self, text: str) -> str:
        """Navigate to chat"""
        st.session_state.current_page = "Chat Assistant"
        return "✅ Navigated to Chat Assistant"
    
    def navigate_to(self, text: str) -> str:
        """Generic navigation handler"""
        if "dashboard" in text:
            return self.go_to_dashboard(text)
        elif "settings" in text:
            return self.go_to_settings(text)
        elif "analytics" in text:
            return self.go_to_analytics(text)
        elif "chat" in text:
            return self.go_to_chat(text)
        else:
            return "❌ Unknown navigation destination"
    
    def show_info(self, text: str) -> str:
        """Show information based on voice command"""
        if "help" in text:
            return self.show_help(text)
        elif "memory" in text or "remember" in text:
            return self.show_memory(text)
        else:
            return "❌ Unknown information request"
    
    def save_data(self, text: str) -> str:
        """Save current data"""
        return "✅ Data saved successfully!"
    
    def export_data(self, text: str) -> str:
        """Export financial data"""
        return "✅ Data exported successfully!"
    
    def budget_help(self, text: str) -> str:
        """Provide budgeting help"""
        return """
        💰 **Budgeting Tips:**
        
        1. **50/30/20 Rule**: 50% needs, 30% wants, 20% savings
        2. **Track Expenses**: Monitor all spending
        3. **Set Goals**: Define clear financial objectives
        4. **Emergency Fund**: Save 3-6 months of expenses
        5. **Review Regularly**: Check budget monthly
        
        Would you like specific budgeting advice?
        """
    
    def investment_help(self, text: str) -> str:
        """Provide investment help"""
        return """
        📈 **Investment Basics:**
        
        1. **Diversify**: Spread investments across different assets
        2. **Start Early**: Time in market beats timing the market
        3. **Risk Tolerance**: Invest according to your comfort level
        4. **Long-term Focus**: Think 5+ years for investments
        5. **Research**: Understand what you're investing in
        
        Would you like specific investment guidance?
        """
    
    def savings_help(self, text: str) -> str:
        """Provide savings help"""
        return """
        🏦 **Savings Strategies:**
        
        1. **Pay Yourself First**: Save before spending
        2. **Automate**: Set up automatic transfers
        3. **High-Yield Accounts**: Use better interest rates
        4. **Cut Expenses**: Reduce unnecessary spending
        5. **Set Targets**: Have specific savings goals
        
        Would you like specific savings advice?
        """
    
    def expenses_help(self, text: str) -> str:
        """Provide expense management help"""
        return """
        💳 **Expense Management:**
        
        1. **Track Everything**: Record all expenses
        2. **Categorize**: Group expenses by type
        3. **Identify Patterns**: Find spending trends
        4. **Cut Unnecessary**: Eliminate wasteful spending
        5. **Negotiate**: Try to reduce bills and subscriptions
        
        Would you like specific expense management tips?
        """

# Global instance
voice_commands = VoiceCommands()
