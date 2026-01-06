"""Tool registry for centralized tool management."""

from typing import Dict, List
from intelligentAgent.tools.base import BaseTool


class ToolRegistry:
    """Registry for managing available tools.
    
    Provides centralized registration, lookup, and schema generation for tools.
    """
    
    def __init__(self):
        """Initialize empty tool registry."""
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool) -> None:
        """Register a tool in the registry.
        
        Args:
            tool: Tool instance to register
            
        Raises:
            ValueError: If a tool with the same name is already registered
        """
        if tool.name in self._tools:
            raise ValueError(f"Tool with name '{tool.name}' is already registered")
        
        self._tools[tool.name] = tool
    
    def get(self, name: str) -> BaseTool:
        """Get a tool by name.
        
        Args:
            name: Name of the tool to retrieve
            
        Returns:
            Tool instance
            
        Raises:
            KeyError: If tool with given name is not found
        """
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found in registry. Available tools: {list(self._tools.keys())}")
        
        return self._tools[name]
    
    def get_openai_schemas(self) -> List[dict]:
        """Get all tools in OpenAI function calling format.
        
        Returns:
            List of tool schemas in OpenAI's expected format
        """
        return [tool.to_openai_tool() for tool in self._tools.values()]
    
    def list_tools(self) -> List[str]:
        """Get list of registered tool names.
        
        Returns:
            List of tool names
        """
        return list(self._tools.keys())
    
    def __len__(self) -> int:
        """Get number of registered tools."""
        return len(self._tools)
    
    def __contains__(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._tools
    
    def __repr__(self) -> str:
        """String representation of the registry."""
        return f"ToolRegistry(tools={list(self._tools.keys())})"

