"""Response schemas for agent outputs."""

from pydantic import BaseModel, Field
from typing import Any, List


class ToolResult(BaseModel):
    """Result from executing a tool."""
    
    tool_call_id: str = Field(..., description="ID of the tool call this result corresponds to")
    arguments: dict[str, Any] = Field(..., description="Arguments used to execute the tool")
    content: str = Field(..., description="Result content from the tool execution")


class AgentResponse(BaseModel):
    """Structured response from an agent."""
    
    answer: str = Field(..., description="Final answer from the agent")
    reasoning_trace: List[str] = Field(default_factory=list, description="Trace of reasoning steps")
    tools_used: List[str] = Field(default_factory=list, description="List of tools used during execution")
    iterations: int = Field(default=0, description="Number of iterations taken")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "answer": "The result is 42",
                "reasoning_trace": ["Used calculator to compute 6*7", "Verified the result"],
                "tools_used": ["calculator"],
                "iterations": 2
            }
        }

