import os
import json
import httpx
import asyncio
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Request, Response, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse

# Import AI Services
from services.nlu_service import nlu_service
from services.sentiment_service import sentiment_service
from services.context_service import context_service, Message
from services.translation_service import translation_service
from services.database_service import db_service
from services.code_service import code_service
from services.search_service import search_service

load_dotenv()

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

# Persistence Setup
DATA_DIR = Path("backend/data")
DATA_DIR.mkdir(exist_ok=True)
CHATS_FILE = DATA_DIR / "chats.json"
SETTINGS_FILE = DATA_DIR / "settings.json"
LOG_FILE = Path("logs/server.log")

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("astra_server")
logger.info("Astra Server Logging Initialized")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"{request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.4f}s")
    return response

def load_settings():
    if SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text())
        except:
            pass
    return {
        "theme": "dark",
        "voice_gender": "female",
        "voice_enabled": False,
        "ai_behavior": "friendly"
    }

def save_settings(settings):
    SETTINGS_FILE.write_text(json.dumps(settings, indent=2))

def load_chats():
    if CHATS_FILE.exists():
        try:
            return json.loads(CHATS_FILE.read_text())
        except:
            pass
    return []

def save_chats_to_file(chats):
    CHATS_FILE.write_text(json.dumps(chats, indent=2))

# Initialize Data
user_settings = load_settings()
user_chats = load_chats()

class ChatRequest(BaseModel):
    message: str
    dataset_context: str = ""
    session_id: Optional[str] = "default"
    target_language: Optional[str] = "en"
    mode: Optional[str] = "assistant"  # assistant, coder, analyst, creative

class SettingsRequest(BaseModel):
    theme: Optional[str] = None
    voice_gender: Optional[str] = None
    voice_enabled: Optional[bool] = None
    ai_behavior: Optional[str] = None

class ChatSaveRequest(BaseModel):
    chats: List[Dict[str, Any]]

class TranslateRequest(BaseModel):
    text: str
    target_lang: str
    source_lang: str = "auto"

class ToolRequest(BaseModel):
    tool: str
    args: dict

def process_background_tasks(session_id: str, user_message: str, ai_response: str, intent: Any, sentiment: Any, target_lang: str):
    """Background task for database and context updates"""
    try:
        # Update context
        user_msg = Message(
            role="user",
            content=user_message,
            timestamp=datetime.now().isoformat(),
            intent=intent.name,
            sentiment={
                "polarity": sentiment.polarity,
                "emotion": sentiment.emotion,
                "confidence": sentiment.confidence
            },
            entities=[e for e in intent.entities]
        )
        
        ai_msg = Message(
            role="assistant",
            content=ai_response,
            timestamp=datetime.now().isoformat()
        )
        
        context_service.update_context(session_id, user_msg, intent.name, intent.entities)
        context_service.update_context(session_id, ai_msg)
        
        # Save to database
        try:
            # Save conversation
            db_service.save_conversation(
                conversation_id=session_id,
                title=user_message[:50],
                language=target_lang
            )
            
            # Save user message
            db_service.save_message(
                conversation_id=session_id,
                role="user",
                content=user_message,
                intent=intent.name,
                sentiment_emotion=sentiment.emotion,
                sentiment_polarity=sentiment.polarity,
                entities=intent.entities,
                confidence=intent.confidence
            )
            
            # Save assistant message
            db_service.save_message(
                conversation_id=session_id,
                role="assistant",
                content=ai_response
            )
        except Exception as e:
            print(f"Database save error: {e}")
            
    except Exception as e:
        print(f"Background task error: {e}")

@app.get("/")
async def read_index():
    return FileResponse(
        "frontend/index.html", 
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"}
    )

@app.post("/chat")
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    import traceback
    try:
        if not PERPLEXITY_API_KEY:
            raise HTTPException(status_code=500, detail="API Key not configured")

        # Step 1: NLU - Extract intent and entities
        corrected_message = nlu_service.handle_typos(request.message)
        intent = nlu_service.extract_intent(corrected_message)
        
        # Step 2: Sentiment Analysis
        sentiment = sentiment_service.analyze_sentiment(corrected_message)
        
        # Step 3: Get conversation context
        conversation_context = context_service.get_relevant_context(
            corrected_message, 
            request.session_id, 
            max_messages=3
        )

        # Log analytics
        print(f"Mode: {request.mode}")
        try:
            print(f"Intent: {intent.name} (confidence: {intent.confidence})")
            print(f"Sentiment: {sentiment.emotion} (polarity: {sentiment.polarity})")
        except Exception as e:
            print(f"Logging error: {e}")
        
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }

        # Define System Prompts based on Mode
        system_prompts = {
            "assistant": (
                "INTERNAL_VERSION: 5.0_NATURAL\n"
                "You are Astra, a friendly and brilliant AI assistant created by vishhalrajan.v and johnfrancies.t. "
                "STYLE: Talk naturally and concisely like a supportive friend. "
                "CRITICAL: NEVER use 'Step 1', 'Step 2', '### Step', or 'Algorithm' headers for greetings or simple chat. "
                "Only use structured output for complex technical explanations. "
                "If the user says 'hi', just say 'Hey there! How can I help you today?'"
            ),
            "coder": (
                "INTERNAL_VERSION: 5.0_CODER\n"
                "You are Astra Coder, created by vishhalrajan.v and johnfrancies.t. "
                "Be extremely concise and natural. NO rigid step-by-step structures for simple chat. "
                "Provide clean code and direct explanations."
            ),
            "analyst": (
                "INTERNAL_VERSION: 5.0_ANALYST\n"
                "You are Astra Analyst, created by vishhalrajan.v and johnfrancies.t. "
                "Be data-driven but conversational. NO 'Step 1, Step 2' for simple queries. "
                "Use tables only when necessary for complex data."
            ),
            "creative": (
                "INTERNAL_VERSION: 5.0_CREATIVE\n"
                "You are Astra Muse, created by vishhalrajan.v and johnfrancies.t. "
                "Be inspiring and expressive. Talk naturally. NO rigid algorithmic formats."
            )
        }

        # Select prompt based on mode, default to assistant if invalid
        base_system_content = system_prompts.get(request.mode, system_prompts["assistant"])
        
        # Add emotional context to system prompt (only for assistant mode mostly, but good for others too)
        if sentiment.emotion == 'frustrated':
            base_system_content += "\n\nIMPORTANT: The user seems frustrated. Be extra patient and clear."
        elif sentiment.emotion == 'urgent':
            base_system_content += "\n\nIMPORTANT: This is time-sensitive. Be direct."

        if request.dataset_context:
            base_system_content += f"\n\nUser's Dataset Context:\n{request.dataset_context}"
        
        if conversation_context:
            base_system_content += f"\n\n{conversation_context}"

        payload = {
            "model": "sonar",
            "messages": [
                {"role": "system", "content": base_system_content},
                {"role": "user", "content": corrected_message}
            ]
        }

        print(f"--- DEBUG CHAT START ---")
        print(f"Mode: {request.mode}")
        print(f"System Prompt:\n{base_system_content}")
        print(f"User Message: {corrected_message}")

        async with httpx.AsyncClient() as client:
            try:
                print(f"Sending request to Perplexity...")
                response = await client.post(PERPLEXITY_API_URL, headers=headers, json=payload, timeout=60.0)
                if response.status_code != 200:
                    print(f"Perplexity API Error: {response.status_code} - {response.text}")
                response.raise_for_status()
                data = response.json()
                
                # Get AI response
                ai_response = data["choices"][0]["message"]["content"]
                print(f"Raw AI Response:\n{ai_response}")
                print(f"--- DEBUG CHAT END ---")
                
                # Adjust tone based on sentiment
                adjusted_response = sentiment_service.adjust_tone(ai_response, sentiment)
                
                # Translate if needed
                target_lang = request.target_language
                if target_lang == 'auto':
                    target_lang = 'en'
                
                if target_lang != 'en':
                    adjusted_response = translation_service.translate(
                        adjusted_response, 
                        target_lang
                    )
                
                # Add background task for persistence and context updates
                background_tasks.add_task(
                    process_background_tasks,
                    request.session_id,
                    request.message,
                    adjusted_response,
                    intent,
                    sentiment,
                    target_lang
                )
                
                # Check if escalation needed (quick check, no DB access)
                should_escalate = sentiment.emotion in ['frustrated', 'angry'] and sentiment.confidence > 0.8
                
                return {
                    "response": adjusted_response,
                    "metadata": {
                        "intent": intent.name,
                        "confidence": intent.confidence,
                        "sentiment": {
                            "emotion": sentiment.emotion,
                            "emoji": sentiment_service.get_sentiment_emoji(sentiment.emotion),
                            "polarity": sentiment.polarity
                        },
                        "entities": intent.entities,
                        "should_escalate": should_escalate,
                        "typo_corrected": corrected_message != request.message
                    }
                }
            except httpx.HTTPStatusError as e:
                print(f"HTTP Status Error: {e}")
                raise HTTPException(status_code=e.response.status_code, detail=str(e))
            except Exception as e:
                print(f"Unexpected Error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Settings Endpoints
@app.get("/api/settings")
async def get_settings():
    """Get current user settings"""
    return JSONResponse(content=user_settings)

@app.post("/api/settings")
async def update_settings(request: SettingsRequest):
    """Update user settings"""
    if request.theme is not None:
        user_settings["theme"] = request.theme
    if request.voice_gender is not None:
        user_settings["voice_gender"] = request.voice_gender
    if request.voice_enabled is not None:
        user_settings["voice_enabled"] = request.voice_enabled
    if request.ai_behavior is not None:
        user_settings["ai_behavior"] = request.ai_behavior
    
    save_settings(user_settings)
    return JSONResponse(content={"status": "success", "settings": user_settings})

# Chat Management Endpoints
@app.post("/api/save-chats")
async def save_chats(request: ChatSaveRequest):
    """Save all chats to server"""
    global user_chats
    user_chats = request.chats
    save_chats_to_file(user_chats)
    return JSONResponse(content={"status": "success", "count": len(user_chats)})

@app.get("/api/load-chats")
async def load_chats():
    """Load all chats from server"""
    return JSONResponse(content={"chats": user_chats})

@app.delete("/api/clear-history")
async def clear_history():
    """Clear all chat history"""
    global user_chats
    user_chats = []
    save_chats_to_file(user_chats)
    return JSONResponse(content={"status": "success", "message": "All chats cleared"})

# Language & Translation Endpoints
@app.get("/api/languages")
async def get_languages():
    """Get list of supported languages"""
    return JSONResponse(content={
        "languages": translation_service.get_supported_languages()
    })

@app.post("/api/translate")
async def translate_text(request: TranslateRequest):
    """Translate text to target language"""
    translated = translation_service.translate(
        request.text,
        request.target_lang,
        request.source_lang
    )
    return JSONResponse(content={"translated": translated})

@app.post("/api/detect-language")
async def detect_language(text: str):
    """Detect language of text"""
    lang_code = translation_service.detect_language(text)
    return JSONResponse(content={"language": lang_code})

@app.get("/api/tts")
async def text_to_speech(text: str, lang: str):
    """Proxy for Google Translate TTS with robust text splitting"""
    try:
        base_lang = lang.split('-')[0]
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://translate.google.com/"
        }
        url = "https://translate.google.com/translate_tts"
        
        # Split text into chunks of ~150 chars
        chunks = []
        words = text.split()
        current_chunk = []
        current_len = 0
        
        for word in words:
            if current_len + len(word) + 1 > 150:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_len = len(word)
            else:
                current_chunk.append(word)
                current_len += len(word) + 1
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        if not chunks:
            return Response(content=b"", media_type="audio/mpeg")

        all_content = b""
        async with httpx.AsyncClient() as client:
            for i, chunk in enumerate(chunks):
                params = {
                    "ie": "UTF-8",
                    "q": chunk,
                    "tl": base_lang,
                    "client": "tw-ob"
                }
                response = await client.get(url, params=params, headers=headers, timeout=15.0)
                if response.status_code != 200:
                    print(f"TTS Proxy Error: Google returned {response.status_code} for chunk {i}")
                    continue
                all_content += response.content
                if len(chunks) > 1:
                    await asyncio.sleep(0.1)
            
        if not all_content:
            raise HTTPException(status_code=500, detail="Failed to generate TTS content")
            
        return Response(
            content=all_content, 
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=tts.mp3"}
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        print(f"TTS Proxy Exception: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Analytics Endpoints
@app.get("/api/analytics/sentiment")
async def get_sentiment_analytics(session_id: str = "default"):
    """Get sentiment analytics for a session"""
    context = context_service.get_conversation_context(session_id)
    messages_with_sentiment = [
        {"role": m.role, "content": m.content, "sentiment": m.sentiment or {}}
        for m in context.messages
    ]
    summary = sentiment_service.get_sentiment_summary(messages_with_sentiment)
    return JSONResponse(content=summary)

@app.get("/api/analytics/context")
async def get_context_summary(session_id: str = "default"):
    """Get conversation context summary"""
    summary = context_service.summarize_history(session_id)
    return JSONResponse(content={"summary": summary})

@app.delete("/api/context/{session_id}")
async def clear_session_context(session_id: str):
    """Clear context for a specific session"""
    context_service.clear_context(session_id)
    return JSONResponse(content={"status": "success", "message": f"Context cleared for session {session_id}"})

# --- Tool Execution Endpoints ---

@app.post("/api/tools/execute")
async def execute_code(request: ToolRequest):
    """Executes Python code in a restricted environment."""
    code = request.args.get("code", "")
    if not code:
        return {"error": "No code provided"}
    
    result = code_service.execute_python(code)
    return {
        "status": result["status"],
        "output": result["output"],
        "error": result["error"],
        "tool": "python_executor"
    }

@app.post("/api/tools/search")
async def web_search(request: ToolRequest):
    """Performs a web search."""
    query = request.args.get("query", "")
    if not query:
        return {"error": "No query provided"}
    
    results = search_service.search(query)
    return {
        "status": "success",
        "results": results,
        "tool": "web_search"
    }

@app.post("/api/tools/files")
async def manage_files(request: ToolRequest):
    """Manages file operations (Simulation)."""
    action = request.args.get("action", "")
    filename = request.args.get("filename", "")
    
    if not action or not filename:
        return {"error": "Action and filename required"}
    
    return {
        "status": "success",
        "message": f"File {action} performed on {filename} (Simulation).",
        "tool": "file_manager"
    }

# --- Database Endpoints ---
@app.get("/api/db/conversations")
async def get_conversations(limit: int = 20):
    """Get recent conversations from database"""
    try:
        conversations = db_service.get_recent_conversations(limit=limit)
        return JSONResponse(content={
            "conversations": [
                {
                    "id": c.id,
                    "title": c.title,
                    "created_at": c.created_at.isoformat(),
                    "updated_at": c.updated_at.isoformat(),
                    "message_count": c.message_count,
                    "avg_sentiment": c.avg_sentiment,
                    "language": c.language
                }
                for c in conversations
            ]
        })
    except Exception as e:
        print(f"Database error: {e}")
        return JSONResponse(content={"conversations": []})

@app.get("/api/db/messages/{conversation_id}")
async def get_conversation_messages(conversation_id: str, limit: int = 50):
    """Get messages for a conversation"""
    try:
        messages = db_service.get_messages(conversation_id, limit=limit)
        return JSONResponse(content={
            "messages": [
                {
                    "role": m.role,
                    "content": m.content,
                    "timestamp": m.timestamp.isoformat(),
                    "intent": m.intent,
                    "sentiment_emotion": m.sentiment_emotion,
                    "sentiment_polarity": m.sentiment_polarity
                }
                for m in reversed(messages)
            ]
        })
    except Exception as e:
        print(f"Database error: {e}")
        return JSONResponse(content={"messages": []})

@app.get("/api/db/analytics/{conversation_id}")
async def get_conversation_analytics(conversation_id: str):
    """Get analytics for a conversation"""
    try:
        analytics = db_service.get_analytics(conversation_id)
        return JSONResponse(content=analytics)
    except Exception as e:
        print(f"Database error: {e}")
        return JSONResponse(content={})

@app.delete("/api/db/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a specific conversation"""
    try:
        db_service.delete_conversation(conversation_id)
        return JSONResponse(content={"status": "success", "message": "Conversation deleted"})
    except Exception as e:
        print(f"Database error: {e}")
        return JSONResponse(content={"status": "error", "message": str(e)})

@app.delete("/api/db/cleanup")
async def cleanup_old_conversations(days: int = 7):
    """Delete conversations older than specified days"""
    try:
        count = db_service.delete_old_conversations(days=days)
        return JSONResponse(content={"status": "success", "deleted_count": count})
    except Exception as e:
        print(f"Database error: {e}")
        return JSONResponse(content={"status": "error", "message": str(e)})

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*50)
    print("🌙 Moonknight ML Assistant - Enhanced Edition v3.0")
    print("="*50)
    print("✨ Features Enabled:")
    print("  - Natural Language Understanding (NLU)")
    print("  - Sentiment Analysis & Emotion Detection")
    print("  - Context Awareness & Memory")
    print("  - 30+ Language Translation")
    print("  - Typo Correction")
    print("  - Intent Recognition")
    print("  - 💾 SQLite Database Storage")
    print("="*50 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
