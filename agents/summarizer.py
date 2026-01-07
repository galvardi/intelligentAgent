"""Summarizer agent for condensing conversation histories."""

from typing import List, Optional, Tuple
from intelligentAgent.agents.base import BaseAgent
from intelligentAgent.llm.client import LLMClient
from intelligentAgent.schemas import ReActLoop
from intelligentAgent.schemas.messages import Message
from intelligentAgent.prompts.summarizer import SUMMARIZER_SYSTEM_PROMPT
from intelligentAgent.config import AgentConfig


class SummarizerAgent(BaseAgent):
    """Agent specialized in summarizing conversation histories.
    
    Takes detailed conversation histories (messages, reasoning, tool usage)
    and produces concise summaries that preserve essential information for
    maintaining context in multi-turn conversations.
    
    Key features:
    - Extracts user questions, key actions, and conclusions
    - Identifies important facts and data points
    - Tracks tool usage
    - Optimizes for token reduction while preserving context
    - No tool usage (pure text summarization)
    """
    
    def __init__(
        self,
        llm_client: LLMClient,
        config: Optional[AgentConfig] = None,
        verbose: bool = False
    ):
        """Initialize the Summarizer agent.
        
        Args:
            llm_client: LLM client for API calls
            config: Optional agent configuration
            verbose: Enable verbose output for debugging
        """
        # No tools needed for summarization
        super().__init__(llm_client, tools=None, config=config)
        self._verbose = verbose
        self._tools_used = []
        self._loop_summerized = 0
        self._system_prompt_msg = Message(role="system", content=self._format_system_prompt())
    
    def compact_conversation(self, loops: List[ReActLoop], loops_to_summarize: int = 1):
        """Compact conversation by summarizing specified number of loops.
        
        from conversation beginning, Modifies the loops list in place by replacing loops with their summarized versions.
        
        Args:
            loops: List of ReActLoop objects to summarize (modified in place)
            loops_to_summarize: Number of loops to summarize from last summarized
            
        Returns:
            None (modifies loops in place)
        """
        for i in range(loops_to_summarize):
            summerized_loop = self.summarize_loop(loops[self._loop_summerized])
            loops[self._loop_summerized] = summerized_loop
            self._loop_summerized += 1
    
    def summarize_loop(
        self,
        loop: ReActLoop,
    ) -> ReActLoop:
        """Summarize a single ReActLoop conversation.
        
        Extracts the user query and creates a condensed summary of the loop's
        messages while preserving tools used.
        
        Args:
            loop: ReActLoop object to summarize
            
        Returns:
            ReActLoop: New loop with user message and summary, preserving tools used
        """        
        
        # Format the loop history for summarization
        conversation_text, tools_used = self._format_messages_for_summary(loop.get_messages())
        
        # Create the summarization request
        messages = [
            self._system_prompt_msg,
            Message(role="user", content=f"Please summarize the following conversation history:\n\n{conversation_text}")
        ]
        
        if self._verbose:
            print(f"_____________________ Summarizing {len(messages)} messages... in loop-{self._loop_summerized} _____________________")
        
        # Get summary from LLM (use summary model from config)
        response = self._llm_client.chat(
            messages=messages,
            tools=None,  # No tools for summarization
        )
        
        summary_text = response.content or "Summary generation failed."
        
        if self._verbose:
            print(f"Summary number of messages: {len(summary_text)} orginal number of messages: {len(conversation_text)}")
        
        # getting user query from the loop
        user_msg = loop.get_messages()[0]
        summerized_loop = ReActLoop(messages=[user_msg], iteration=self._loop_summerized, tools_used=tools_used)
        summerized_loop.add_message("summary", content=summary_text)
        return summerized_loop
    
    def _format_messages_for_summary(self, messages: List[Message]) -> Tuple[str, List[str]]:
        """Format conversation messages into readable text for summarization.
        
        Also extracts tools used during the iteration to avoid double-pass.
        
        Args:
            messages: List of messages to format
            
        Returns:
            Tuple[str, List[str]]: A tuple containing:
                - Formatted conversation text as a string
                - List of unique tool names used during the conversation
        """
        formatted_lines = []
        tools_set = set()
        
        for msg in messages:
            if msg.role == "system":
                # Skip system prompts - they're not part of the conversation
                continue
            
            elif msg.role == "user":
                formatted_lines.append(f"USER: {msg.content}")
            
            elif msg.role == "assistant":
                # Assistant messages can have content, tool_calls, or both
                if msg.tool_calls:
                    # Extract tool names
                    tool_names = [tc.name for tc in msg.tool_calls]
                    for name in tool_names:
                        tools_set.add(name)
                
                    # Format output
                    if msg.content:
                        # Both reasoning and tool calls
                        formatted_lines.append(f"ASSISTANT: {msg.content}")
                    formatted_lines.append(f"ASSISTANT: [Called tools: {', '.join(tool_names)}]")
                elif msg.content:
                    # Only content (reasoning or final answer)
                    formatted_lines.append(f"ASSISTANT: {msg.content}")
            
            elif msg.role == "tool":
                # Tool result
                formatted_lines.append(f"TOOL RESULT: {msg.content}")
        
        return "\n".join(formatted_lines), list(tools_set)
    
    def _format_system_prompt(self) -> str:
        """Return the Summarizer system prompt.
        
        Returns:
            System prompt for summarization
        """
        return SUMMARIZER_SYSTEM_PROMPT

