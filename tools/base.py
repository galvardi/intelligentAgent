"""Abstract base class for all tools."""

from abc import ABC, abstractmethod
from typing import Type
from pydantic import BaseModel


class BaseTool(ABC):
    """Abstract base class for all tools.
    
    Subclasses must define:
    - name: Unique identifier for the tool
    - description: What the tool does (used by LLM to decide when to use it)
    - args_schema: Pydantic model defining the tool's input parameters
    - execute(): Method that runs the tool with validated inputs
    """
    
    name: str
    description: str
    args_schema: Type[BaseModel]
    
    def to_openai_tool(self) -> dict:
        """Convert tool to OpenAI function calling format.
        
        Returns:
            Dictionary in OpenAI's tool format with function name, description, and parameters.
        """
        # Get JSON schema from Pydantic model
        schema = self.args_schema.model_json_schema()
        
        # Remove Pydantic-specific fields that aren't needed
        schema.pop("title", None)
        
        # For strict mode, additionalProperties must be false
        schema["additionalProperties"] = False
        
        # For strict mode, ALL properties must be in the required array
        # (even those with defaults)
        if "properties" in schema:
            schema["required"] = list(schema["properties"].keys())
        
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "strict": True,
                "parameters": schema
            }
        }
    
    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Execute the tool with validated arguments.
        
        Args are automatically validated against args_schema before this is called.
        
        Args:
            **kwargs: Arguments matching the args_schema definition
            
        Returns:
            String result to be passed back to the LLM
        """
        pass
    
    def __repr__(self) -> str:
        """String representation of the tool."""
        return f"{self.__class__.__name__}(name='{self.name}')"

