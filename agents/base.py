"""Abstract base class for all agents."""

from abc import ABC, abstractmethod
from typing import List, Optional
from intelligentAgent.llm.client import LLMClient
from intelligentAgent.llm.models import LLMResponse
from intelligentAgent.tools.base import BaseTool
from intelligentAgent.tools.registry import ToolRegistry
from intelligentAgent.config import AgentConfig
from intelligentAgent.schemas.messages import Message
from intelligentAgent.schemas.responses import AgentResponse


class BaseAgent(ABC):
    """Abstract base class for all agents.
    
    Provides common functionality for:
    - Managing LLM client
    - Tool registry management
    - Conversation history
    - Message handling
    
    Subclasses must implement:
    - run(): Main execution loop (agent-specific strategy)
    - _format_system_prompt(): Agent-specific system prompt
    
    Each agent type can define its own internal methods for reasoning,
    planning, acting, etc. based on its specific pattern.
    """
    
    def __init__(
        self,
        llm_client: LLMClient,
        tools: Optional[List[BaseTool]] = None,
        config: Optional[AgentConfig] = None
    ):
        """Initialize the base agent.
        
        Args:
            llm_client: LLM client for making API calls
            tools: Optional list of tools available to the agent
            config: Optional agent configuration (uses defaults if not provided)
        """
        self._llm_client = llm_client
        self._tool_registry = ToolRegistry()
        self._config = config or AgentConfig()
        self._messages: List[Message] = []
        
        # Register tools if provided
        if tools:
            for tool in tools:
                self._tool_registry.register(tool)
    
    def run(self, query: str) -> AgentResponse:
        """Execute the agent's main loop.
        
        Must be implemented by subclasses to define their specific
        execution strategy. Different agent types implement different patterns:
        - ReAct: Reason → Act → Observe loop
        - Plan-and-Execute: Plan → Execute → Monitor
        - Chain-of-Thought: Sequential reasoning steps
        - Tree-of-Thought: Branching exploration
        
        Args:
            query: User's input query
            
        Returns:
            Structured agent response
        """
        pass
    
    @abstractmethod
    def _format_system_prompt(self) -> str:
        """Return the system prompt for this agent type.
        
        Each agent type has its own prompt that defines its behavior,
        capabilities, and interaction patterns.
        
        Returns:
            System prompt string
        """
        pass
    
    def _add_message(
        self,
        role: str,
        content: Optional[str] = None,
        **kwargs
    ) -> None:
        """Add a message to the conversation history.
        
        Args:
            role: Message role (system, user, assistant, tool)
            content: Message content
            **kwargs: Additional message fields (tool_calls, tool_call_id, etc.)
        """
        message = Message(role=role, content=content, **kwargs)
        self._messages.append(message)
    
    def _get_tools_schema(self) -> List[dict]:
        """Get all registered tools in OpenAI format.
        
        Returns:
            List of tool schemas
        """
        return self._tool_registry.get_openai_schemas()
    
    def _reset(self) -> None:
        """Reset conversation state for new query.
        
        Clears message history to start fresh.
        """
        self._messages = []
    
    def get_conversation_history(self) -> List[Message]:
        """Get current conversation history.
        
        Returns:
            List of messages in the conversation
        """
        return self._messages.copy()
    
    @property
    def available_tools(self) -> List[str]:
        """Get list of available tool names.
        
        Returns:
            List of registered tool names
        """
        return self._tool_registry.list_tools()

