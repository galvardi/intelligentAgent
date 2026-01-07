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


class ReActLoop(BaseModel):
    """Container for a single ReAct loop iteration containing all messages.
    
    This abstraction encapsulates all messages within a single think-act-observe cycle,
    providing better context control and cleaner separation of loop-scoped data.
    used to allow compaction of previous start of conversaation when context grows
    """
    
    messages: List[Message] = Field(default_factory=list, description="Messages in this loop")
    iteration: int = Field(default=0, description="Loop iteration number")
    tools_used: List[str] = Field(default_factory=list, description="Tools used in this loop")

    
    def add_message(
        self,
        role: str,
        content: Optional[str] = None,
        **kwargs
    ) -> None:
        """Add a message to this loop's conversation.
        
        Args:
            role: Message role (system, user, assistant, tool)
            content: Message content
            **kwargs: Additional message fields (tool_calls, tool_call_id, etc.)
        """
        message = Message(role=role, content=content, **kwargs)
        self.messages.append(message)
        
        # Track tools used
        if kwargs.get('tool_calls'):
            for tc in kwargs['tool_calls']:
                if tc.name not in self.tools_used:
                    self.tools_used.append(tc.name)
    
    def get_messages(self) -> List[Message]:
        """Get all messages in this loop.
        
        Returns:
            List of messages
        """
        return self.messages
    
    def get_user_query(self) -> Optional[str]:
        """Extract the user query from this loop.
        
        Returns:
            User query string or None if not found
        """
        for msg in self.messages:
            if msg.role == "user":
                return msg.content
        return None
    
    def clear(self) -> None:
        """Clear all messages from this loop."""
        self.messages.clear()
        self.tools_used.clear()
    
    def message_count(self) -> int:
        """Get the number of messages in this loop.
        
        Returns:
            Message count
        """
        return len(self.messages)
    
    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True

