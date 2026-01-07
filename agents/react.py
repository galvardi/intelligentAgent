"""ReAct agent implementation with chain of thought reasoning."""

from typing import List
from intelligentAgent.agents.base import BaseAgent
from intelligentAgent.agents.summarizer import SummarizerAgent
from intelligentAgent.llm.client import LLMClient
from intelligentAgent.llm.models import LLMResponse
from intelligentAgent.tools.base import BaseTool
from intelligentAgent.schemas.messages import Message, ToolCall, ReActLoop
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
        self._loops: List[ReActLoop] = []
        self._loop_counter = 0  # Track total loop iterations across conversation
        self._current_context_length = 0
        
        # Compaction thresholds from config
        self._compact_after_loops = config.compact_after_loops if config else 3
        self._compact_context_threshold = config.compact_context_threshold if config else 50000
        
        self._add_message("system", self._format_system_prompt())
        self._summarizer = SummarizerAgent(llm_client, config=config, verbose=verbose)
    
    def run(self, query: str) -> AgentResponse:
        """Execute the ReAct loop: Reason -> Act -> Observe -> Repeat.
        
        Args:
            query: User's input query
            
        Returns:
            Structured agent response with answer and reasoning trace
            
        Raises:
            MaxIterationsError: If agent doesn't complete within max_iterations
        """        
        # Initialize a new ReAct loop and add to history
        new_loop = ReActLoop(iteration=self._loop_counter)
        self._loops.append(new_loop)
        
        # Add user query (automatically adds to both global messages and current loop)
        self._add_message("user", query)
        
        # Track execution
        reasoning_trace = []
        tools_used = []
        
        # ReAct loop
        for iteration in range(self._max_iterations):            
            if self._verbose:
                print(f"\n--- Iteration {iteration + 1} ---")
            
            # Step 1: REASON - Think about what to do next (no tools)
            # Receives full conversation from all loops
            reasoning_response = self._reason()
            reasoning_text = reasoning_response.content or ""
            self._current_context_length = reasoning_response.context_length
            
            if self._verbose:
                print(f"Reasoning: {reasoning_text}")
            
            # Track the reasoning
            reasoning_trace.append(f"Thought: {reasoning_text}")
            
            # Add reasoning to conversation history
            self._add_message("assistant", 'Thought: ' + reasoning_text)
            
            # Step 2: ACT - Decide whether to use tools or provide final answer
            action_response = self._decide_action()
            
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
                self._loop_counter += 1  # Increment global loop counter
                if self._verbose:
                    print(f"Final answer: {action_response.content}")
                    print(f"Loop counter: {self._loop_counter}, current context length: {self._current_context_length}")
                
                # Check if conversation compaction is needed based on thresholds
                should_compact = (
                    self._loop_counter >= self._compact_after_loops or
                    self._current_context_length >= self._compact_context_threshold
                )
                
                if should_compact:
                    if self._verbose:
                        print(f"[Compaction triggered: loop_counter={self._loop_counter}, context_length={self._current_context_length}]")
                    self._compact_conversation()
                
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

    def _compact_conversation(self, loops_to_summarize: int = 1) -> None:
        """Compact the conversation history, starting from the first loop"""
        self._summarizer.compact_conversation(self._loops)
        self._messages = self._build_full_conversation_from_loops()
    
    def _add_message(
        self,
        role: str,
        content: str = None,
        **kwargs
    ) -> None:
        """Override to add message to both global history and current loop.
        
        Args:
            role: Message role (system, user, assistant, tool)
            content: Message content
            **kwargs: Additional message fields (tool_calls, tool_call_id, etc.)
        """
        # Add to global message history (parent implementation)
        super()._add_message(role, content, **kwargs)
        
        # Also add to current loop if one exists
        current_loop = self._get_current_loop()
        if current_loop:
            current_loop.add_message(role, content, **kwargs)
    
    def _get_current_loop(self) -> ReActLoop:
        """Get the current (most recent) ReAct loop.
        
        Returns:
            Current ReActLoop or None if no loops exist
        """
        return self._loops[-1] if self._loops else None
    
    def _build_full_conversation_from_loops(self) -> List[Message]:
        """Build the full conversation from all loops.
        
        This combines the system message with all messages from all loops
        to provide complete context for reasoning.
        
        Returns:
            List of all messages across all loops
        """
        # Start with system message
        full_conversation = []
        if self._messages and self._messages[0].role == "system":
            full_conversation.append(self._messages[0])
        
        # Add all messages from all loops
        for loop in self._loops:
            full_conversation.extend(loop.messages)
        
        return full_conversation
    
    def clear_loop_history(self) -> None:
        """Clear all loop history.
        
        This can be useful to free memory for long-running agents.
        """
        self._loops.clear()
    
    def get_total_loop_iterations(self) -> int:
        """Get the total number of loop iterations across the entire conversation.
        
        Returns:
            Total loop counter value
        """
        return self._loop_counter
    
    def _reason(self) -> LLMResponse:
        """Step 1: Reasoning phase - Think about what to do next (WITHOUT tools).
        
        This is the critical "Think" step in ReAct where the agent reasons
        about the current state and what action might be needed.
        
        Uses the reasoning model for complex, deep thinking.
        
        Returns:
            LLM response with reasoning (no tool calls)
        """
        # Add a prompt to encourage reasoning
        reasoning_messages = self._messages + [
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
    
    def _decide_action(self) -> LLMResponse:
        """Step 2: Action phase - Decide whether to use tools or answer.
        
        After reasoning, the agent decides whether to:
        - Use tools to gather more information
        - Provide a final answer if it has enough information
        
        Only sends messages from the current ReAct loop (not full conversation history)
        since tool selection is based on the current thought/reasoning cycle.
        Uses the faster inference model since the reasoning is already done.
        
        Returns:
            LLM response with optional tool calls or final answer
        """
        # Send only current ReAct loop messages for tool decision (use faster inference model)
        current_loop = self._get_current_loop()
        return self._llm_client.chat(
            messages=current_loop.get_messages(),
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

