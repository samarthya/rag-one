"""
Conversation Memory Module
Manages conversation history and context
"""

from typing import List, Dict, Optional
from datetime import datetime
import json
from pathlib import Path

class ConversationMemory:
    """
    Manages conversation history with context window management.
    
    Features:
    - Stores conversation history
    - Manages context window (prevents overwhelming LLM)
    - Persists conversations to disk
    - Provides conversation summary
    """
    
    def __init__(self, max_history: int = 10, persist_dir: Optional[Path] = None):
        """
        Initialize conversation memory.
        
        Args:
            max_history: Maximum number of exchanges to keep in active memory
            persist_dir: Directory to save conversation history
        """
        self.max_history = max_history
        self.messages: List[Dict] = []
        self.persist_dir = persist_dir
        
        if persist_dir:
            persist_dir.mkdir(parents=True, exist_ok=True)
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        Add a message to conversation history.
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
            metadata: Optional metadata (sources, timestamp, etc.)
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.messages.append(message)
        
        # Keep only recent history in active memory
        if len(self.messages) > self.max_history * 2:  # *2 because user+assistant
            self.messages = self.messages[-self.max_history * 2:]
    
    def get_conversation_history(self, last_n: Optional[int] = None) -> List[Dict]:
        """
        Get conversation history.
        
        Args:
            last_n: Number of recent exchanges to return (None = all)
            
        Returns:
            List of message dictionaries
        """
        if last_n:
            return self.messages[-(last_n * 2):]  # *2 for user+assistant pairs
        return self.messages
    
    def get_context_string(self, last_n: int = 3) -> str:
        """
        Get formatted conversation context for LLM prompt.
        
        Args:
            last_n: Number of recent exchanges to include
            
        Returns:
            Formatted string with conversation history
        """
        recent_messages = self.get_conversation_history(last_n)
        
        if not recent_messages:
            return ""
        
        context_parts = ["Previous conversation:"]
        for msg in recent_messages:
            role = "You" if msg['role'] == 'user' else "Assistant"
            context_parts.append(f"{role}: {msg['content']}")
        
        return "\n".join(context_parts)
    
    def get_conversation_summary(self) -> str:
        """
        Generate a summary of the conversation topics.
        Useful for very long conversations.
        """
        if not self.messages:
            return "No conversation yet."
        
        # Extract key topics from user questions
        user_messages = [m['content'] for m in self.messages if m['role'] == 'user']
        
        summary = f"Conversation with {len(user_messages)} questions about: "
        # Simple keyword extraction (you could use LLM for better summaries)
        topics = set()
        keywords = ['project', 'work', 'study', 'skill', 'experience', 'technology']
        
        for msg in user_messages:
            for keyword in keywords:
                if keyword in msg.lower():
                    topics.add(keyword)
        
        return summary + ", ".join(topics) if topics else "various topics"
    
    def clear(self):
        """Clear all conversation history."""
        self.messages = []
    
    def save_conversation(self, filename: str):
        """
        Save conversation to JSON file.
        
        Args:
            filename: Name of file to save to
        """
        if not self.persist_dir:
            raise ValueError("persist_dir not set during initialization")
        
        filepath = self.persist_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump({
                'messages': self.messages,
                'summary': self.get_conversation_summary(),
                'saved_at': datetime.now().isoformat()
            }, f, indent=2)
    
    def load_conversation(self, filename: str):
        """
        Load conversation from JSON file.
        
        Args:
            filename: Name of file to load from
        """
        if not self.persist_dir:
            raise ValueError("persist_dir not set during initialization")
        
        filepath = self.persist_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Conversation file not found: {filename}")
        
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.messages = data['messages']