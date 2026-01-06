"""Models for LLM responses."""

import json
from pydantic import BaseModel, Field
from typing import List, Optional, Any
from openai.types.chat import ChatCompletion
from intelligentAgent.schemas.messages import ToolCall


class LLMResponse(BaseModel):
    """Structured response from the LLM."""
    
    content: Optional[str] = Field(None, description="Text content of the response")
    tool_calls: Optional[List[ToolCall]] = Field(None, description="Tool calls requested by the LLM")
    finish_reason: str = Field(..., description="Reason the model stopped generating")
    
    @property
    def has_tool_calls(self) -> bool:
        """Check if response contains tool calls."""
        return bool(self.tool_calls)
    
    @classmethod
    def from_openai_response(cls, response: ChatCompletion) -> "LLMResponse":
        """Create LLMResponse from OpenAI API response.
        
        Args:
            response: OpenAI ChatCompletion response object
            
        Returns:
            Parsed LLMResponse
        """
        choice = response.choices[0]
        message = choice.message
        
        # Parse tool calls if present
        tool_calls = None
        if hasattr(message, "tool_calls") and message.tool_calls:
            tool_calls = [
                ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments)
                )
                for tc in message.tool_calls
            ]
        
        return cls(
            content=message.content,
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason
        )

