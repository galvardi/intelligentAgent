"""ReAct agent implementation with chain of thought reasoning."""

from typing import List
from intelligentAgent.agents.base import BaseAgent
from intelligentAgent.llm.client import LLMClient
from intelligentAgent.llm.models import LLMResponse
from intelligentAgent.tools.base import BaseTool
from intelligentAgent.schemas.messages import Message, ToolCall
from intelligentAgent.schemas.responses import AgentResponse, ToolResult
from intelligentAgent.prompts.react import REACT_SYSTEM_PROMPT
from intelligentAgent.config import AgentConfig


class MaxIterationsError(Exception):
    """Raised when agent exceeds maximum iterations."""
    pass


class ReActAgent(BaseAgent):
    """ReAct agent that interleaves reasoning (thinking) and acting (using tools).
    
    The ReAct pattern:
    1. Think: Reason about what to do next
    2. Act: Execute tools to gather information
    3. Observe: Process tool results
    4. Repeat until task is complete
    """
    
    def __init__(
        self,
        llm_client: LLMClient,
        tools: List[BaseTool],
        max_iterations: int = 10,
        verbose: bool = False,
        config: AgentConfig = None
    ):
        """Initialize the ReAct agent.
        
        Args:
            llm_client: LLM client for API calls
            tools: List of tools available to the agent
            max_iterations: Maximum number of think-act-observe cycles
            verbose: Enable verbose output for debugging
            config: Optional agent configuration
        """
        super().__init__(llm_client, tools, config)
        self._max_iterations = max_iterations
        self._verbose = verbose
    
    def run(self, query: str) -> AgentResponse:
        """Execute the ReAct loop: Reason -> Act -> Observe -> Repeat.
        
        Args:
            query: User's input query
            
        Returns:
            Structured agent response with answer and reasoning trace
            
        Raises:
            MaxIterationsError: If agent doesn't complete within max_iterations
        """
        # Reset state and initialize conversation
        self._reset()
        self._add_message("system", self._format_system_prompt())
        self._add_message("user", query)
        
        # Track execution
        reasoning_trace = []
        tools_used = []
        
        # ReAct loop
        for iteration in range(self._max_iterations):
            if self._verbose:
                print(f"\n--- Iteration {iteration + 1} ---")
            
            # Step 1: REASON - Think about what to do next (no tools)
            reasoning_response = self._reason(self._messages)
            reasoning_text = reasoning_response.content or ""
            
            if self._verbose:
                print(f"Reasoning: {reasoning_text}")
            
            # Track the reasoning
            reasoning_trace.append(f"Thought: {reasoning_text}")
            
            # Add reasoning to conversation history
            self._add_message("assistant", 'Thought: ' + reasoning_text)
            
            # Step 2: ACT - Decide whether to use tools or provide final answer
            action_response = self._decide_action(self._messages)
            
            if action_response.has_tool_calls:
                # Execute requested tools
                if self._verbose:
                    print(f"Tools requested: {[tc.name + ' with arguments: ' + str(tc.arguments) for tc in action_response.tool_calls]}")
                
                results = self._act(action_response.tool_calls)
                tools_used.extend([tc.name for tc in action_response.tool_calls])
                
                # Step 3: OBSERVE - Add results to conversation
                self._observe(action_response.tool_calls, results)
                
                # Track tool usage
                tool_names = [tc.name for tc in action_response.tool_calls]
                reasoning_trace.append(f"Action: Used tools {', '.join(tool_names)}")
                
                if self._verbose:
                    for result in results:
                        print(f"Observation: {result.content[:100]}...")
                
                # Add observation summary to continue reasoning
                observation_summary = self._format_observations(results)
                reasoning_trace.append(f"Observation: {observation_summary}")
            
            else:
                # No more tool calls - agent has final answer
                if self._verbose:
                    print(f"Final answer: {action_response.content}")
                
                return AgentResponse(
                    answer=action_response.content or "No answer provided",
                    reasoning_trace=reasoning_trace,
                    tools_used=list(set(tools_used)),  # Unique tools
                    iterations=iteration + 1
                )
        
        # Exceeded max iterations
        raise MaxIterationsError(
            f"Agent did not complete task in {self._max_iterations} iterations. "
            f"Consider increasing max_iterations or simplifying the query."
        )
    
    def _reason(self, messages: List[Message]) -> LLMResponse:
        """Step 1: Reasoning phase - Think about what to do next (WITHOUT tools).
        
        This is the critical "Think" step in ReAct where the agent reasons
        about the current state and what action might be needed.
        
        Uses the reasoning model for complex, deep thinking.
        
        Args:
            messages: Current conversation messages
            
        Returns:
            LLM response with reasoning (no tool calls)
        """
        # Add a prompt to encourage reasoning
        reasoning_messages = messages + [
            Message(
                role="user",
                content="Think step-by-step: What information do you have? What do you still need? What tool calls should call next and in what order?"
            )
        ]
        
        # Call LLM WITHOUT tools to get pure reasoning (use reasoning model)
        return self._llm_client.chat(
            messages=reasoning_messages,
            tools=self._get_tools_schema(),
            tool_choice='none',
            reason=True  # Use reasoning model for deep thinking
        )
    
    def _decide_action(self, messages: List[Message]) -> LLMResponse:
        """Step 2: Action phase - Decide whether to use tools or answer.
        
        After reasoning, the agent decides whether to:
        - Use tools to gather more information
        - Provide a final answer if it has enough information
        
        Uses the faster inference model since the reasoning is already done.
        
        Args:
            messages: Current conversation messages (includes reasoning)
            
        Returns:
            LLM response with optional tool calls or final answer
        """
        # Now enable tools for the action decision (use faster inference model)
        return self._llm_client.chat(
            messages=messages,
            tools=self._get_tools_schema(),
            tool_choice="auto"  # Let model decide when to use tools
        )
    
    def _act(self, tool_calls: List[ToolCall]) -> List[ToolResult]:
        """Execute each tool call and return results.
        
        Args:
            tool_calls: List of tool calls from the LLM
            
        Returns:
            List of tool execution results
        """
        results = []
        
        for tool_call in tool_calls:
            try:
                # Get tool from registry
                tool = self._tool_registry.get(tool_call.name)
                
                # Validate arguments with Pydantic
                validated_args = tool.args_schema.model_validate(tool_call.arguments)
                
                # Execute tool
                result_content = tool.execute(**validated_args.model_dump())
                
                results.append(
                    ToolResult(
                        tool_call_id=tool_call.id,
                        arguments=tool_call.arguments,
                        content=result_content
                    )
                )
            
            except Exception as e:
                # Return error message to LLM
                results.append(
                    ToolResult(
                        tool_call_id=tool_call.id,
                        arguments=tool_call.arguments,
                        content=f"Error executing tool: {str(e)}"
                    )
                )
        
        return results
    
    def _observe(self, tool_calls: List[ToolCall], results: List[ToolResult]) -> None:
        """Step 3: Observation phase - Add tool results to message history.
        
        Args:
            tool_calls: Original tool calls from the LLM
            results: Results from executing the tools
        """
        # Add assistant message with tool calls
        self._add_message("assistant", content=None, tool_calls=tool_calls)
        
        # Add tool result messages
        for result in results:
            self._add_message(
                "tool",
                content=result.content + " (with arguments: " + str(result.arguments) + ")",
                tool_call_id=result.tool_call_id
            )
    
    def _format_observations(self, results: List[ToolResult]) -> str:
        """Format tool results into a readable observation summary.
        
        Args:
            results: Results from tool execution
            
        Returns:
            Formatted observation text
        """
        observations = []
        for result in results:
            # Truncate long results for reasoning trace
            content = result.content[:200] + "..." if len(result.content) > 200 else result.content
            observations.append(content)
        
        return " | ".join(observations)
    
    def _format_system_prompt(self) -> str:
        """Return the ReAct system prompt.
        
        Returns:
            System prompt for ReAct agent
        """
        return REACT_SYSTEM_PROMPT

