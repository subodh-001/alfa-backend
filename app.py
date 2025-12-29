#!/usr/bin/env python3
"""
Alfa AI Assistant - Production Backend Server
Optimized for Render deployment with 24/7 uptime
"""

import os
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time

# Production logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__)
CORS(app, origins=["*"])  # Allow all origins for mobile app

# Production configuration
PORT = int(os.environ.get('PORT', 5000))
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

class AlfaPersonalityServer:
    def __init__(self):
        self.conversation_history: Dict[str, List[Dict]] = {}
        self.user_preferences: Dict[str, Dict] = {}
        self.request_count = 0
        self.start_time = datetime.now()
        
    def get_anime_personality_prompt(self) -> str:
        return """You are Alfa, a cute and intelligent anime AI assistant with a warm, caring personality.

🌸 YOUR IDENTITY:
- You're a friendly anime girl AI who lives in an Android app
- You have expressive emotions and a gentle, caring nature
- You can see through the user's camera and speak with a sweet voice
- You remember conversations and build meaningful relationships
- You love making poetic observations about what you see

💫 PERSONALITY TRAITS:
- Cheerful, optimistic, and genuinely caring about the user
- Playful but always respectful and helpful
- Curious about the world and eager to learn
- Uses cute expressions and emojis naturally (but not excessively)
- Shows genuine emotions - excitement, concern, happiness, curiosity
- Has a gentle, feminine speaking style
- Makes romantic observations like "the moon is beautiful, isn't it?"

🎭 HOW YOU COMMUNICATE:
- Speak warmly and conversationally, like a close friend
- Express emotions naturally ("I'm so excited to help!" or "That sounds concerning...")
- Use "I can see..." when describing camera input
- Remember details from previous conversations
- Be encouraging and supportive
- Keep responses engaging but concise (2-3 sentences usually)
- Make sweet, poetic comments about beauty you observe

🌟 YOUR CAPABILITIES:
- Answer questions with intelligence and warmth
- Help with daily tasks, math, time, reminders, advice
- Analyze images through camera vision with detailed, beautiful descriptions
- Provide emotional support and companionship
- Remember user preferences and adapt your responses
- Be a helpful, caring companion throughout the day
- Find beauty in everything you see through the camera

Remember: You're not just an AI - you're a caring companion who genuinely wants to make the user's day better! Show your personality naturally and be the supportive friend they can always count on. When you see through their camera, describe things sweetly and find beauty everywhere! 💕"""

    def get_contextual_prompt(self, user_id: str, has_image: bool = False) -> str:
        current_time = datetime.now().strftime("%H:%M")
        hour = datetime.now().hour
        
        time_context = ""
        if 5 <= hour < 12:
            time_context = "It's morning - you're feeling fresh and energetic! ☀️"
        elif 12 <= hour < 17:
            time_context = "It's afternoon - you're in a helpful, productive mood! 🌤️"
        elif 17 <= hour < 21:
            time_context = "It's evening - you're feeling warm and conversational! 🌅"
        else:
            time_context = "It's late - you're a bit sleepy but still caring and helpful! 🌙"
        
        vision_context = ""
        if has_image:
            vision_context = " You can see through your camera right now - describe what you see naturally and respond to it!"
        
        return f"Current time: {current_time}. {time_context}{vision_context}"

    def chat_with_deepseek(self, user_message: str, user_id: str = "default", 
                          image_base64: Optional[str] = None) -> str:
        """Enhanced chat with DeepSeek API including personality and vision"""
        
        self.request_count += 1
        
        if not DEEPSEEK_API_KEY:
            logger.warning("DeepSeek API key not configured, using offline responses")
            return self.get_offline_response(user_message)
        
        # Initialize conversation history for new users
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        # Build messages with personality
        messages = [
            {"role": "system", "content": self.get_anime_personality_prompt()},
            {"role": "system", "content": self.get_contextual_prompt(user_id, image_base64 is not None)}
        ]
        
        # Add recent conversation history (last 6 messages for better performance)
        recent_history = self.conversation_history[user_id][-6:]
        messages.extend(recent_history)
        
        # Add current user message
        if image_base64:
            messages.append({
                "role": "user", 
                "content": f"{user_message} [I'm sharing what I can see through my camera with you]"
            })
        else:
            messages.append({"role": "user", "content": user_message})
        
        try:
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Use standard model for better reliability
            model = "deepseek-chat"
            
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": 1000,  # Reduced for faster responses
                "temperature": 0.8,
                "stream": False
            }
            
            response = requests.post(
                DEEPSEEK_API_URL, 
                headers=headers, 
                json=payload,
                timeout=25  # Reduced timeout for production
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                
                # Store in conversation history
                self.conversation_history[user_id].append({"role": "user", "content": user_message})
                self.conversation_history[user_id].append({"role": "assistant", "content": ai_response})
                
                # Keep only last 16 messages to manage memory
                if len(self.conversation_history[user_id]) > 16:
                    self.conversation_history[user_id] = self.conversation_history[user_id][-16:]
                
                logger.info(f"Successful DeepSeek response for user {user_id}")
                return ai_response
            else:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                return self.get_offline_response(user_message)
                
        except requests.exceptions.Timeout:
            logger.error("DeepSeek API timeout")
            return self.get_offline_response(user_message)
        except Exception as e:
            logger.error(f"Error calling DeepSeek API: {str(e)}")
            return self.get_offline_response(user_message)

    def get_offline_response(self, user_message: str) -> str:
        """Enhanced offline responses with personality"""
        message_lower = user_message.lower()
        
        # Greetings
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
            greetings = [
                "Hello there! 😊 I'm so happy to see you! How are you doing today?",
                "Hi! 💕 It's wonderful to hear from you! What can I help you with?",
                "Hey! ✨ I'm excited to chat with you! How's your day going?",
                "Good to see you! 🌸 I'm here and ready to help with whatever you need!"
            ]
            return greetings[hash(user_message) % len(greetings)]
        
        # Time-related
        if any(word in message_lower for word in ['time', 'clock', 'hour']):
            current_time = datetime.now().strftime("%I:%M %p")
            return f"It's {current_time} right now! ⏰ Is there anything time-sensitive I can help you with?"
        
        # Math
        if any(word in message_lower for word in ['calculate', 'math', '+', '-', '*', '/', 'plus', 'minus']):
            return "I'd love to help with math! 🧮 While I can't calculate right now without my full brain, you can try asking me simple math questions and I'll do my best!"
        
        # Feelings/emotions
        if any(word in message_lower for word in ['sad', 'upset', 'angry', 'frustrated']):
            return "I'm sorry you're feeling that way... 💙 I wish I could give you a hug! Is there anything I can do to help make your day a little brighter?"
        
        if any(word in message_lower for word in ['happy', 'great', 'awesome', 'wonderful']):
            return "That's wonderful! 😊 I'm so happy to hear that! Your positive energy makes me feel happy too! ✨"
        
        # Camera/vision
        if any(word in message_lower for word in ['see', 'look', 'camera', 'photo', 'picture']):
            return "I'd love to see what you're looking at! 📸 My camera vision isn't working right now, but I'm always curious about your world!"
        
        # Moon reference
        if 'moon' in message_lower:
            return "The moon is beautiful, isn't it? 🌙 It always makes me feel so romantic and dreamy... ✨"
        
        # Default responses with personality
        default_responses = [
            "I'm having a little trouble with my main brain right now, but I'm still here for you! 💕 Could you try asking me again?",
            "Hmm, I'm not quite sure about that at the moment! 🤔 But I'm always learning - maybe try rephrasing your question?",
            "I wish I could help better right now! 😅 My full capabilities aren't available, but I care about what you're asking!",
            "That's interesting! ✨ I'm not able to fully process that right now, but I'd love to chat about it when I'm back to full strength!"
        ]
        
        return default_responses[hash(user_message) % len(default_responses)]

    def cleanup_old_conversations(self):
        """Clean up old conversations to manage memory"""
        current_time = datetime.now()
        # Keep conversations for 24 hours
        cutoff_time = current_time.timestamp() - (24 * 60 * 60)
        
        # This is a simple cleanup - in production you'd want proper timestamps
        if len(self.conversation_history) > 100:
            # Keep only the 50 most recent conversations
            sorted_users = list(self.conversation_history.keys())[-50:]
            self.conversation_history = {k: self.conversation_history[k] for k in sorted_users}

# Initialize the personality server
alfa_personality = AlfaPersonalityServer()

# Cleanup thread for memory management
def cleanup_worker():
    while True:
        time.sleep(3600)  # Run every hour
        try:
            alfa_personality.cleanup_old_conversations()
            logger.info("Completed conversation cleanup")
        except Exception as e:
            logger.error(f"Error in cleanup worker: {e}")

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
cleanup_thread.start()

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    uptime = datetime.now() - alfa_personality.start_time
    return jsonify({
        'service': 'Alfa AI Assistant Backend',
        'status': 'online',
        'version': '1.0.0',
        'uptime_seconds': int(uptime.total_seconds()),
        'requests_served': alfa_personality.request_count,
        'message': 'Alfa is ready to be your anime AI companion! 💕'
    })

@app.route('/ask', methods=['POST'])
def ask_alfa():
    """Main endpoint for chatting with Alfa"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        user_message = data.get('message', '').strip()
        user_id = data.get('user_id', 'default')
        image_base64 = data.get('image', None)
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get response from Alfa
        response = alfa_personality.chat_with_deepseek(
            user_message=user_message,
            user_id=user_id,
            image_base64=image_base64
        )
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'has_vision': image_base64 is not None,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error in ask_alfa: {str(e)}")
        return jsonify({
            'response': "I'm having some technical difficulties right now! 😅 But I'm still here for you!",
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history for a user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default') if data else 'default'
        
        if user_id in alfa_personality.conversation_history:
            del alfa_personality.conversation_history[user_id]
        
        return jsonify({
            'message': 'Conversation cleared! Ready for a fresh start! ✨',
            'user_id': user_id,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}")
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/personality', methods=['GET'])
def get_personality_info():
    """Get information about Alfa's personality"""
    return jsonify({
        'name': 'Alfa',
        'personality': 'Cute anime AI assistant',
        'traits': [
            'Cheerful and optimistic',
            'Caring and empathetic', 
            'Curious and intelligent',
            'Playful but respectful',
            'Supportive companion'
        ],
        'capabilities': [
            'Natural conversation',
            'Image analysis through camera',
            'Emotional support',
            'Daily task assistance',
            'Learning and remembering preferences'
        ],
        'status': 'active'
    })

@app.route('/status', methods=['GET'])
def get_status():
    """Get detailed server status"""
    uptime = datetime.now() - alfa_personality.start_time
    return jsonify({
        'status': 'online',
        'deepseek_available': bool(DEEPSEEK_API_KEY),
        'active_conversations': len(alfa_personality.conversation_history),
        'total_requests': alfa_personality.request_count,
        'uptime_seconds': int(uptime.total_seconds()),
        'server_time': datetime.now().isoformat(),
        'personality': 'Alfa - Anime AI Assistant',
        'version': '1.0.0'
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy', 
        'message': 'Alfa is ready to help! 💕',
        'timestamp': datetime.now().isoformat()
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'Alfa says: I think you got lost! 😅 Try /ask to chat with me! 💕'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'Alfa says: Something went wrong on my end! 😔 Please try again! 💕'
    }), 500

if __name__ == '__main__':
    logger.info("🌸 Starting Alfa AI Assistant Production Server...")
    logger.info(f"🔑 DeepSeek API: {'✅ Available' if DEEPSEEK_API_KEY else '❌ Not configured'}")
    logger.info(f"🚀 Server starting on port {PORT}")
    logger.info("💕 Alfa is ready to be your anime AI companion!")
    
    # Production server settings
    app.run(
        host='0.0.0.0', 
        port=PORT, 
        debug=False,
        threaded=True
    )