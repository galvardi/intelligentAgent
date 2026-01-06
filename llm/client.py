"""LLM client wrapper. currently only OpenAI is supported"""

import json
from typing import List, Optional
from openai import OpenAI
from intelligentAgent.config import AgentConfig
from intelligentAgent.llm.models import LLMResponse
from intelligentAgent.schemas.messages import Message


class LLMClient:
    """Wrapper around OpenAI client with tool calling support.
    
    Provides a clean interface for making LLM calls with dual model support:
    - Reasoning model: For complex reasoning tasks (slower, more capable)
    - Inference model: For simple inference tasks (faster, cheaper)
    
    The appropriate model is selected based on the task type.
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize the LLM client.
        
        Args:
            config: Agent configuration containing API key and model settings
        """
        self._config = config
        self._client = OpenAI(api_key=config.openai_api_key)
        self._reasoning_model = config.openai_reasoning_model
        self._inference_model = config.openai_inference_model
    
    def chat(
        self,
        messages: List[Message],
        tools: Optional[List[dict]] = None,
        tool_choice: str = "auto",
        temperature: Optional[float] = None,
        reason: bool = False
    ) -> LLMResponse:
        """Make a chat completion request.
        
        Args:
            messages: List of conversation messages
            tools: Optional list of tools in OpenAI format
            tool_choice: How the model should choose tools ("auto", "none", or specific tool)
            temperature: Override default temperature
            reason: If True, use reasoning model (more capable, slower). 
                   If False, use inference model (faster, cheaper). Default: False
            
        Returns:
            Parsed LLM response
        """
        # Select appropriate model based on task type
        model = self._reasoning_model if reason else self._inference_model
        
        # Convert messages to OpenAI format
        openai_messages = [self._message_to_openai(msg) for msg in messages]
        
        # Prepare request parameters
        params = {
            "model": model,
            "messages": openai_messages,
        }
        
        # Add tools if provided
        if tools:
            params["tools"] = tools
            params["tool_choice"] = tool_choice
        
        # Make API call
        response = self._client.chat.completions.create(**params)
        
        # Parse and return response
        return LLMResponse.from_openai_response(response)
    
    def _message_to_openai(self, message: Message) -> dict:
        """Convert Message to OpenAI format.
        
        Args:
            message: Message object
            
        Returns:
            Dictionary in OpenAI message format
        """
        result = {"role": message.role}
        
        # Add content if present
        if message.content is not None:
            result["content"] = message.content
        
        # Add tool calls if present
        if message.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": json.dumps(tc.arguments) if isinstance(tc.arguments, dict) else tc.arguments
                    }
                }
                for tc in message.tool_calls
            ]
        
        # Add tool call ID for tool messages
        if message.tool_call_id:
            result["tool_call_id"] = message.tool_call_id
        
        # Add name for tool messages
        if message.name:
            result["name"] = message.name
        
        return result

