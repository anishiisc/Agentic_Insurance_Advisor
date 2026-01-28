"""
Insurance Advisor AI Agent
===========================
This module implements the core agent logic that:
1. Manages conversations with the Claude API
2. Handles tool calling (agentic behavior)
3. Processes tool results and generates responses

The agent uses Claude's tool use capability to search insurance products
and provide personalized recommendations.
"""
import json
from typing import List, Dict, Any, Optional
from anthropic import Anthropic, APIError, RateLimitError

from tools import TOOLS, execute_tool
from config import ANTHROPIC_API_KEY, MODEL_NAME, SYSTEM_PROMPT


class InsuranceAgent:
    """
    AI Agent for Insurance Policy Recommendations
    
    This agent:
    - Maintains conversation context
    - Decides when to use tools vs respond directly
    - Handles the tool use loop (agentic behavior)
    - Provides personalized insurance recommendations
    """
    
    def __init__(self):
        """Initialize the agent with Anthropic client"""
        if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "your-api-key-here":
            raise ValueError(
                "ANTHROPIC_API_KEY not set. Please add your API key to backend/.env"
            )
        
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = MODEL_NAME
        self.max_tokens = 1024
        self.max_tool_iterations = 5  # Prevent infinite loops
    
    async def process_message(
        self,
        message: str,
        history: List[Dict]
    ) -> str:
        """
        Process a user message and return the agent's response
        
        This is the main entry point for the agent. It:
        1. Builds the message history
        2. Calls Claude API
        3. Handles tool use if needed (agentic loop)
        4. Returns the final text response
        
        Args:
            message: The current user message
            history: List of previous messages in the conversation
            
        Returns:
            The agent's text response
        """
        # Build messages array with history
        messages = self._build_messages(history, message)
        
        try:
            # Initial API call
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages
            )
            
            # Handle tool use loop (agentic behavior)
            iteration = 0
            while response.stop_reason == "tool_use" and iteration < self.max_tool_iterations:
                iteration += 1
                
                # Process tool calls
                tool_results = self._process_tool_calls(response)
                
                # Add assistant response and tool results to messages
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                messages.append({
                    "role": "user",
                    "content": tool_results
                })
                
                # Get next response
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    system=SYSTEM_PROMPT,
                    tools=TOOLS,
                    messages=messages
                )
            
            # Extract and return text response
            return self._extract_text_response(response)
            
        except RateLimitError:
            return (
                "I'm experiencing high demand right now. "
                "Please try again in a few moments."
            )
        except APIError as e:
            print(f"API Error: {e}")
            return (
                "I encountered an issue processing your request. "
                "Please try again or rephrase your question."
            )
        except Exception as e:
            print(f"Unexpected error: {e}")
            return (
                "Something went wrong on my end. "
                "Please try again in a moment."
            )
    
    def _build_messages(
        self,
        history: List[Dict],
        current_message: str
    ) -> List[Dict]:
        """
        Build the messages array for the API call
        
        Args:
            history: Previous conversation messages
            current_message: The current user message
            
        Returns:
            List of message dicts for the API
        """
        messages = []
        
        # Add history
        for msg in history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": current_message
        })
        
        return messages
    
    def _process_tool_calls(self, response) -> List[Dict]:
        """
        Process tool calls from the API response
        
        Args:
            response: The API response containing tool use blocks
            
        Returns:
            List of tool result content blocks
        """
        tool_results = []
        
        for block in response.content:
            if block.type == "tool_use":
                tool_name = block.name
                tool_input = block.input
                tool_use_id = block.id
                
                print(f"[TOOL CALL] {tool_name}: {json.dumps(tool_input)}")
                
                # Execute the tool
                result = execute_tool(tool_name, tool_input)
                
                print(f"[TOOL RESULT] {tool_name}: {json.dumps(result)[:200]}...")
                
                # Add tool result
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": json.dumps(result, ensure_ascii=False)
                })
        
        return tool_results
    
    def _extract_text_response(self, response) -> str:
        """
        Extract text content from the API response
        
        Args:
            response: The API response
            
        Returns:
            Combined text from all text blocks
        """
        text_parts = []
        
        for block in response.content:
            if hasattr(block, "text"):
                text_parts.append(block.text)
        
        if not text_parts:
            return (
                "I apologize, but I couldn't generate a proper response. "
                "Could you please rephrase your question?"
            )
        
        return "\n".join(text_parts)
    
    def get_welcome_message(self) -> str:
        """
        Get the initial welcome message for new conversations
        
        Returns:
            A friendly welcome message introducing the agent
        """
        return (
            "Namaste! 🙏 I'm **Bima Buddy**, your Insurance Advisor.\n\n"
            "I can help you find the right insurance policy for your needs. "
            "I specialize in:\n\n"
            "• **Health Insurance** - Individual, Family Floater, Senior Citizen plans\n"
            "• **Term Life Insurance** - Pure protection plans\n"
            "• **Motor Insurance** - Car and Two-wheeler coverage\n"
            "• **Travel Insurance** - Domestic and International trips\n\n"
            "What type of insurance are you looking for today?"
        )


# Synchronous wrapper for testing
def process_message_sync(
    agent: InsuranceAgent,
    message: str,
    history: List[Dict]
) -> str:
    """
    Synchronous wrapper for testing the agent
    
    Args:
        agent: The InsuranceAgent instance
        message: User message
        history: Conversation history
        
    Returns:
        Agent response
    """
    import asyncio
    return asyncio.run(agent.process_message(message, history))


# ==============================================================================
# Testing
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Insurance Agent")
    print("=" * 60)
    
    try:
        agent = InsuranceAgent()
        print("✓ Agent initialized successfully\n")
        
        # Test conversation
        test_messages = [
            "Hi, I need health insurance for my family",
            "We are 4 members, I'm 35, wife is 32, kids are 8 and 5",
            "Budget is around 20000 per year",
        ]
        
        history = []
        
        for msg in test_messages:
            print(f"\n{'='*60}")
            print(f"USER: {msg}")
            print(f"{'='*60}")
            
            response = process_message_sync(agent, msg, history)
            
            print(f"\nAGENT: {response}")
            
            # Update history
            history.append({"role": "user", "content": msg})
            history.append({"role": "assistant", "content": response})
            
            print("\n" + "-"*40)
            input("Press Enter to continue...")
            
    except ValueError as e:
        print(f"✗ Error: {e}")
        print("\nMake sure to set ANTHROPIC_API_KEY in backend/.env")
