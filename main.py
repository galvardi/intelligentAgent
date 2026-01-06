"""Main entry point and CLI for the intelligent agent."""

import sys
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich import print as rprint

from intelligentAgent.config import AgentConfig
from intelligentAgent.llm.client import LLMClient
from intelligentAgent.agents.react import ReActAgent, MaxIterationsError
from intelligentAgent.tools.examples.calculator import CalculatorTool
from intelligentAgent.tools.examples.datetime_tool import DateTimeTool


console = Console()


def print_banner():
    """Print welcome banner."""
    banner = """
    # 🤖 Intelligent Agent
    
    A ReAct agent with chain-of-thought reasoning.
    Type your questions and watch the agent think through solutions step by step.
    
    **Available commands:**
    - `exit` or `quit` - Exit the program
    - `help` - Show this help message
    - `tools` - List available tools
    - `clear` - Clear the screen
    """
    console.print(Panel(Markdown(banner), title="Welcome", border_style="cyan"))


def print_help():
    """Print help information."""
    help_text = """
    ## How to Use
    
    1. **Ask questions**: Type any question and press Enter
    2. **Watch the agent work**: See the reasoning process in real-time (verbose mode)
    3. **Get answers**: The agent will use tools to find accurate information
    
    ## Examples
    
    - "What is 25 * 4 + 100?"
    - "What time is it?"
    - "Calculate the square root of 144"
    - "What is pi times 2?"
    
    ## Tips
    
    - The agent can use multiple tools in sequence
    - Break complex problems into steps for better results
    - If stuck, try rephrasing your question
    """
    console.print(Panel(Markdown(help_text), title="Help", border_style="green"))


def create_agent(verbose: bool = False) -> Optional[ReActAgent]:
    """Create and initialize the ReAct agent.
    
    Args:
        verbose: Enable verbose output
        
    Returns:
        Initialized agent or None if configuration fails
    """
    try:
        # Load configuration
        config = AgentConfig()
        
        # Create LLM client
        llm_client = LLMClient(config)
        
        # Initialize tools
        tools = [
            CalculatorTool(),
            DateTimeTool(),
        ]
        
        # Create agent
        agent = ReActAgent(
            llm_client=llm_client,
            tools=tools,
            max_iterations=config.max_iterations,
            verbose=verbose,
            config=config
        )
        
        return agent
    
    except Exception as e:
        console.print(f"[red]Error initializing agent: {e}[/red]")
        console.print("\n[yellow]Make sure you have:")
        console.print("1. Created a .env file with your OPENAI_API_KEY")
        console.print("2. Installed all dependencies: pip install -r requirements.txt[/yellow]")
        return None


def interactive_mode(verbose: bool = False):
    """Run the agent in interactive mode.
    
    Args:
        verbose: Enable verbose output
    """
    print_banner()
    
    # Create agent
    agent = create_agent(verbose=verbose)
    if not agent:
        return
    
    console.print(f"\n[green]✓ Agent initialized with {len(agent.available_tools)} tools[/green]")
    console.print("[dim]Type 'help' for usage information or 'exit' to quit[/dim]\n")
    
    # Main interaction loop
    while True:
        try:
            # Get user input
            query = Prompt.ask("\n[bold cyan]You[/bold cyan]")
            
            # Handle commands
            if query.lower() in ["exit", "quit"]:
                console.print("\n[yellow]Goodbye! 👋[/yellow]")
                break
            
            elif query.lower() == "help":
                print_help()
                continue
            
            elif query.lower() == "tools":
                console.print(f"\n[bold]Available tools:[/bold] {', '.join(agent.available_tools)}")
                continue
            
            elif query.lower() == "clear":
                console.clear()
                print_banner()
                continue
            
            elif not query.strip():
                continue
            
            # Process query with agent
            try:
                with console.status("[bold magenta]Agent is thinking...", spinner="dots"):
                    response = agent.run(query)
                
                # Display response
                console.print(f"\n[bold magenta]Agent:[/bold magenta]")
                console.print(Panel(response.answer, border_style="magenta"))
                
                # Show execution details if not verbose
                if not verbose and (response.tools_used or response.reasoning_trace):
                    console.print(f"\n[dim]Tools used: {', '.join(response.tools_used) if response.tools_used else 'none'}[/dim]")
                    console.print(f"[dim]Iterations: {response.iterations}[/dim]")
            
            except MaxIterationsError as e:
                console.print(f"\n[red]Error: {e}[/red]")
                console.print("[yellow]Try asking a simpler question or breaking it into steps.[/yellow]")
            
            except Exception as e:
                console.print(f"\n[red]Error processing query: {e}[/red]")
        
        except KeyboardInterrupt:
            console.print("\n\n[yellow]Interrupted. Type 'exit' to quit or continue with a new query.[/yellow]")
        
        except Exception as e:
            console.print(f"\n[red]Unexpected error: {e}[/red]")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Intelligent Agent - A ReAct agent with chain-of-thought reasoning"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output to see reasoning steps"
    )
    parser.add_argument(
        "-q", "--query",
        type=str,
        help="Run a single query and exit (non-interactive mode)"
    )
    
    args = parser.parse_args()
    
    # Single query mode
    if args.query:
        agent = create_agent(verbose=args.verbose)
        if not agent:
            sys.exit(1)
        
        try:
            response = agent.run(args.query)
            console.print(Panel(response.answer, title="Answer", border_style="green"))
            if args.verbose:
                console.print(f"\nTools used: {', '.join(response.tools_used)}")
                console.print(f"Iterations: {response.iterations}")
        
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)
    
    # Interactive mode
    else:
        interactive_mode(verbose=args.verbose)


if __name__ == "__main__":
    main()

