"""Message schema for conversation history."""

from pydantic import BaseModel, Field
from typing import Optional, List, Any


class ToolCall(BaseModel):
    """Represents a tool call from the LLM."""
    
    id: str = Field(..., description="Unique identifier for the tool call")
    name: str = Field(..., description="Name of the tool to call")
    arguments: dict[str, Any] = Field(default_factory=dict, description="Arguments for the tool")


class Message(BaseModel):
    """A message in the conversation history."""
    
    role: str = Field(..., description="Role of the message sender (system, user, assistant, tool)")
    content: Optional[str] = Field(None, description="Content of the message")
    tool_calls: Optional[List[ToolCall]] = Field(None, description="Tool calls made by the assistant")
    tool_call_id: Optional[str] = Field(None, description="ID of the tool call this message responds to")
    name: Optional[str] = Field(None, description="Name of the tool for tool messages")
    
    def to_openai_format(self) -> dict:
        """Convert to OpenAI API message format."""
        message = {"role": self.role}
        
        if self.content is not None:
            message["content"] = self.content
        
        if self.tool_calls:
            message["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": tc.arguments if isinstance(tc.arguments, str) else str(tc.arguments)
                    }
                }
                for tc in self.tool_calls
            ]
        
        if self.tool_call_id:
            message["tool_call_id"] = self.tool_call_id
        
        if self.name:
            message["name"] = self.name
        
        return message

