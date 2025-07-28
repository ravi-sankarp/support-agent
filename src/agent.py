#!/usr/bin/env python3
"""
SolidWorks Agent Core
Pure business logic layer - no UI dependencies
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import traceback
from perplexity_helper import PerplexityHelper


class MessageType(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ResponseType(Enum):
    SUCCESS = "success"
    CONTEXT_REQUEST = "context_request"
    ERROR = "error"
    VALIDATION_ERROR = "validation_error"


@dataclass
class ChatMessage:
    """Represents a single chat message"""
    role: MessageType
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Represents an agent response with metadata"""
    content: str
    response_type: ResponseType
    processing_time_ms: int = 0
    model_used: str = ""
    metadata: Dict = field(default_factory=dict)


@dataclass
class ChatSession:
    """Represents a chat session"""
    session_id: str
    messages: List[ChatMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)
    
    def add_message(self, message: ChatMessage) -> None:
        """Add a message to the session"""
        self.messages.append(message)
        self.last_activity = datetime.now()
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history in API format"""
        return [
            {"role": msg.role.value, "content": msg.content}
            for msg in self.messages
            if msg.role != MessageType.SYSTEM
        ]
    
    def get_user_message_count(self) -> int:
        """Get number of user messages"""
        return len([msg for msg in self.messages if msg.role == MessageType.USER])


class SolidWorksAgentCore:
    """
    Core SolidWorks agent business logic
    """
    
    def __init__(self, api_key: str, model: str = "sonar-pro"):
        self.perplexity = PerplexityHelper(api_key, model)
        self.sessions: Dict[str, ChatSession] = {}
        
    def create_session(self, session_id: str) -> ChatSession:
        """Create a new chat session"""
        session = ChatSession(session_id=session_id)
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get existing session or None"""
        return self.sessions.get(session_id)
    
    def get_or_create_session(self, session_id: str) -> ChatSession:
        """Get existing session or create new one"""
        session = self.get_session(session_id)
        if session is None:
            session = self.create_session(session_id)
        return session
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def list_sessions(self) -> List[ChatSession]:
        """Get all sessions"""
        return list(self.sessions.values())
    
    def process_message(self, session_id: str, user_input: str) -> Tuple[AgentResponse, ChatSession]:
        """
        Process a user message and return response with updated session
        """
        start_time = datetime.now()
        
        # Get or create session
        session = self.get_or_create_session(session_id)
        
        
        try:
            # Get response from Perplexity
            response_content, is_valid = self.perplexity.send_query(
                user_input, 
                session.get_conversation_history()
            )
            
            # Determine response type
            if not is_valid:
                response_type = ResponseType.ERROR
            elif self._is_context_request(response_content):
                response_type = ResponseType.CONTEXT_REQUEST
            else:
                response_type = ResponseType.SUCCESS
                        
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if is_valid:

                # Add user message to session
                user_message = ChatMessage(
                    role=MessageType.USER,
                    content=user_input,
                    metadata={"processed_at": start_time.isoformat()}
                )
                session.add_message(user_message)

                # Create agent response
                agent_response = AgentResponse(
                    content=response_content,
                    response_type=response_type,
                    processing_time_ms=int(processing_time),
                    model_used=self.perplexity.get_current_model(),
                    metadata={
                        "session_id": session_id,
                        "message_count": session.get_user_message_count()
                    }
                )
                
                print(agent_response)

                # Add assistant message to session if valid
                assistant_message = ChatMessage(
                    role=MessageType.ASSISTANT,
                    content=response_content,
                    metadata={
                        "response_type": response_type.value,
                        "processing_time_ms": agent_response.processing_time_ms,
                        "model_used": agent_response.model_used
                    }
                )
                session.add_message(assistant_message)
            else:
                agent_response = AgentResponse(
                    content=response_content,
                    response_type=response_type,
                    processing_time_ms=int(processing_time),
                    model_used=self.perplexity.get_current_model(),
                    metadata={
                        "session_id": session_id,
                        "message_count": session.get_user_message_count()
                    }
            )
            return agent_response, session
            
        except Exception as e:
            traceback.print_exc()
            print(e)
            # Handle errors
            error_response = AgentResponse(
                content=f"An error occurred while processing your request: {str(e)}",
                response_type=ResponseType.ERROR,
                processing_time_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                model_used=self.perplexity.get_current_model(),
                metadata={"error": str(e)}
            )
            
            return error_response, session
    
    def clear_session(self, session_id: str) -> bool:
        """Clear messages from a session but keep the session"""
        session = self.get_session(session_id)
        if session:
            session.messages = []
            session.last_activity = datetime.now()
            return True
        return False
    
    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """Get session summary statistics"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        user_count = session.get_user_message_count()
        session_duration = datetime.now() - session.created_at
        
        return {
            "session_id": session_id,
            "message_count": len(session.messages),
            "user_questions": user_count,
            "session_duration": str(session_duration).split('.')[0],
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "current_model": self.perplexity.get_current_model()
        }
    
    def switch_model(self, new_model: str) -> bool:
        """Switch Perplexity model"""
        return self.perplexity.switch_model(new_model)
    
    def get_available_models(self) -> List[str]:
        """Get available models"""
        return self.perplexity.get_available_models()
    
    def get_current_model(self) -> str:
        """Get current model"""
        return self.perplexity.get_current_model()
    
    def test_connection(self) -> Tuple[str, bool]:
        """Test API connection"""
        return self.perplexity.test_connection()
    
    def _is_context_request(self, response: str) -> bool:
        """Check if response is asking for more context"""
        context_indicators = [
            "need more information", "can you provide", "please specify", 
            "what version", "which version", "can you tell me more",
            "more details", "specific error", "exactly when", "what exactly",
            "could you clarify", "additional information", "help me understand"
        ]
        return any(phrase in response.lower() for phrase in context_indicators)
    