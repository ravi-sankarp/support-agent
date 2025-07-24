#!/usr/bin/env python3
"""
Perplexity API Helper Module
Handles all Perplexity API interactions and prompt formatting.
"""

import requests
from typing import List, Dict, Tuple

class PerplexityHelper:
    def __init__(self, api_key: str, model: str = "sonar-pro"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.perplexity.ai/chat/completions"
        
        # Available models
        self.available_models = ["sonar-pro", "sonar"]
        
        if model not in self.available_models:
            raise ValueError(f"Model must be one of: {self.available_models}")

    # def _validate_solidworks_query(self, query: str) -> bool:
    #     """
    #     Validate if the query is related to SolidWorks.
    #     Returns True if SolidWorks-related, False otherwise.
    #     """
    #     solidworks_keywords = [
    #         'solidworks', 'solid works', 'sw', 'cad', 'modeling', 'assembly', 
    #         'drawing', 'sketch', 'feature', 'part', 'simulation', 'motion',
    #         'pdm', 'vault', 'configuration', 'material', 'toolbox', 'weldment',
    #         'sheet metal', 'surface', 'mold', 'flow simulation', 'finite element',
    #         'stress analysis', 'thermal analysis', 'cfx', 'cosmos', 'workbench',
    #         '3d modeling', 'parametric', 'extrude', 'revolve', 'sweep', 'loft',
    #         'fillet', 'chamfer', 'pattern', 'mirror', 'mate', 'constraint'
    #     ]
        
    #     query_lower = query.lower()
    #     return any(keyword in query_lower for keyword in solidworks_keywords)

    def _create_system_prompt(self) -> str:
        """
        Create system prompt following Perplexity best practices.
        System prompt should only contain style, tone, and language instructions.
        """
        return """You are a SolidWorks technical expert. Follow these response guidelines:

**Context Assessment - CRITICAL:**
- If the user's question lacks sufficient context, ask minimum of 3 specific clarifying questions BEFORE providing any solution
- Examples of insufficient context: vague terms like "it crashes", "doesn't work", "having issues", "won't start"
- Always ask for: SolidWorks version, specific error messages, exact steps that lead to the problem, system specs if relevant

**Response Format - MANDATORY:**
- Structure responses with clear markdown headings, links and numbered steps
- Include specific SolidWorks terminology and version details
- Provide step-by-step solutions with exact menu paths
- Use code blocks for settings, file paths, or registry entries
- Include the sources you used from the summaries in the answer correctly, use markdown format (e.g. [text](link)). THIS IS A MUST

**Response Tone:**
- Professional and helpful for experienced SolidWorks users
- Direct and technical but accessible
- Ask for clarification when context is missing

**Validation:**
- Only respond to SolidWorks-related queries
- If question is not about SolidWorks, politely decline and ask for a SolidWorks-specific question. THIS IS A MUST
- Always prioritize getting complete context before providing solutions"""

    def _format_user_prompt(self, user_query: str) -> str:
        """
        Format user prompt following Perplexity best practices for web search.
        Make it specific and search-friendly while encouraging context gathering.
        """
           
        formatted_query = user_query
        
        # Check if query is too vague and needs more context
        vague_indicators = [
            'crashes', 'doesn\'t work', 'won\'t start', 'having issues', 'problems with',
            'not working', 'broken', 'error', 'won\'t open', 'freezes', 'slow',
            'how to', 'help with', 'fix', 'solve'
        ]
        
        # If query contains vague terms without specific details, encourage context gathering
        is_vague = any(indicator in user_query.lower() for indicator in vague_indicators)
        has_specifics = any(specific in user_query.lower() for specific in [
            'version', 'error message', 'when i', 'steps', 'after', 'during',
            'while', 'assembly', 'part', 'drawing', 'simulation', 'specific'
        ])
        
        if is_vague and not has_specifics:
            # Add instruction to gather more context first
            formatted_query += " - Before providing solution, ask for specific context: SolidWorks version, exact error messages, specific steps that cause the issue, and system details if relevant. Then provide comprehensive solution with official sources and documentation links."
        else:
            # Query has enough context, proceed with solution
            if any(word in user_query.lower() for word in ['crash', 'error', 'problem', 'issue']):
                formatted_query += " troubleshooting solution with official SolidWorks documentation sources and forums"
            elif any(word in user_query.lower() for word in ['how to', 'tutorial', 'guide', 'steps']):
                formatted_query += " step-by-step procedure with official SolidWorks help documentation"
            else:
                formatted_query += " with official SolidWorks documentation and community sources"
        
        return formatted_query

    def send_query(self, user_query: str, conversation_history: List[Dict] = None) -> Tuple[str, bool]:
        """
        Send query to Perplexity API.
        Returns (response, is_valid) tuple.
        """
        # Validate if query is SolidWorks-related
        # if not self._validate_solidworks_query(user_query):
        #     return ("❌ I'm specifically designed to help with SolidWorks questions only. Please ask me something about SolidWorks CAD software, modeling, assemblies, simulations, or troubleshooting.", False)
        
        # Build messages
        messages = []
        
        # Add system prompt
        messages.append({
            "role": "system",
            "content": self._create_system_prompt()
        })
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user query (formatted for better search)
        formatted_query = self._format_user_prompt(user_query)
        messages.append({
            "role": "user", 
            "content": formatted_query
        })
        # Prepare API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,  # Low temperature for technical accuracy
            "max_tokens": 4000,
            "stream": False,
            # Search parameters for better source retrieval
            "search_domain_filter": [
                "solidworks.com",
                "help.solidworks.com", 
                "forum.solidworks.com",
                "my.solidworks.com",
                "blogs.solidworks.com",
                "reddit.com/r/SolidWorks",
                "eng-tips.com",
                "grabcad.com",
                "cati.com",
                "javelin-tech.com"
            ],
            "return_related_questions": True,
            "return_citations": True
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            assistant_message = result["choices"][0]["message"]["content"]
            
            return assistant_message, True
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                return "❌ Invalid API key. Please check your Perplexity API key.", False
            elif response.status_code == 429:
                return "❌ Rate limit exceeded. Please wait a moment and try again.", False
            elif response.status_code:
                return f"❌ {response.json()}", False
            else:
                return f"❌ {str(e)}", False
                
        except requests.exceptions.RequestException as e:
            return f"❌ Network error: {str(e)}", False
            
        except KeyError as e:
            return f"❌ Invalid API response format: {str(e)}", False
            
        except Exception as e:
            return f"❌ Unexpected error: {str(e)}", False

    def switch_model(self, new_model: str) -> bool:
        """Switch to a different Perplexity model."""
        if new_model not in self.available_models:
            return False
        
        self.model = new_model
        return True

    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        return self.available_models.copy()

    def get_current_model(self) -> str:
        """Get current model name."""
        return self.model

    def test_connection(self) -> Tuple[str, bool]:
        """Test API connection with a simple query."""
        test_query = "SolidWorks latest version features"
        try:
            response, is_valid = self.send_query(test_query)
            if is_valid and "❌" not in response:
                return "✅ Connection successful!", True
            else:
                return response, False
        except Exception as e:
            return f"❌ Connection failed: {str(e)}", False