# Intelligent Agent 🤖

A ReAct (Reasoning + Acting) agent with chain-of-thought reasoning, built with proper OOP principles using OpenAI's API and Pydantic for structured outputs.

## Features

- **ReAct Pattern**: Interleaves reasoning (thinking) with actions (tool execution)
- **Chain of Thought**: Explicit step-by-step reasoning before taking actions
- **Type-Safe Tools**: Pydantic models for automatic validation and schema generation
- **OpenAI Native**: Uses OpenAI's tool calling API (no text parsing)
- **Extensible Architecture**: Easy to create specialized agents by inheriting from `BaseAgent`
- **Rich CLI**: Beautiful interactive interface with verbose mode
- **Clean OOP Design**: Abstract base classes, composition, and design patterns

## Architecture

```
BaseAgent (Abstract)
├── ReActAgent (Think → Act → Observe loop)
└── [Your Custom Agents]

BaseTool (Abstract)
├── CalculatorTool
├── DateTimeTool
└── [Your Custom Tools]
```

### Design Patterns Used

- **Template Method**: Base agent defines the structure, subclasses implement specifics
- **Strategy**: Different thinking strategies per agent type
- **Registry**: Centralized tool management
- **Composition**: Agent has LLMClient and ToolRegistry

## Installation

1. **Clone the repository** (or navigate to the project directory)

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.7
MAX_ITERATIONS=10
VERBOSE=false
```

## Usage

### Interactive Mode

Run the agent in interactive mode:
```bash
python -m intelligentAgent.main
```

With verbose output to see reasoning steps:
```bash
python -m intelligentAgent.main --verbose
```

### Single Query Mode

Run a single query and exit:
```bash
python -m intelligentAgent.main --query "What is 25 * 4 + 100?"
```

## Example Interactions

```
You: What is the square root of 144?

Agent:
The square root of 144 is 12.

Tools used: calculator
Iterations: 1
```

```
You: What time is it and what is 2 + 2?

Agent:
The current time is 14:32:15 UTC, and 2 + 2 equals 4.

Tools used: get_datetime, calculator
Iterations: 2
```

## Project Structure

```
intelligentAgent/
├── agents/
│   ├── base.py          # Abstract BaseAgent class
│   └── react.py         # ReActAgent implementation
├── llm/
│   ├── client.py        # OpenAI client wrapper
│   └── models.py        # LLM response models
├── tools/
│   ├── base.py          # Abstract BaseTool class
│   ├── registry.py      # Tool registry
│   └── examples/
│       ├── calculator.py    # Calculator tool
│       └── datetime_tool.py # DateTime tool
├── schemas/
│   ├── messages.py      # Message types
│   └── responses.py     # Response types
├── prompts/
│   └── react.py         # ReAct system prompts
├── config.py            # Pydantic settings
└── main.py              # CLI entry point
```

## Creating Custom Tools

Creating a new tool is simple:

```python
from pydantic import BaseModel, Field
from typing import Type
from intelligentAgent.tools.base import BaseTool

class MyToolInput(BaseModel):
    """Input schema for my tool."""
    param1: str = Field(..., description="Description of param1")
    param2: int = Field(default=0, description="Description of param2")

class MyTool(BaseTool):
    """My custom tool."""
    
    name: str = "my_tool"
    description: str = "What my tool does"
    args_schema: Type[BaseModel] = MyToolInput
    
    def execute(self, param1: str, param2: int = 0) -> str:
        """Execute the tool."""
        # Your logic here
        return f"Result: {param1} with {param2}"
```

Then register it with your agent:
```python
from intelligentAgent.agents.react import ReActAgent
from intelligentAgent.llm.client import LLMClient
from intelligentAgent.config import AgentConfig

config = AgentConfig()
client = LLMClient(config)
agent = ReActAgent(client, tools=[MyTool()])
```

## Creating Custom Agents

Extend `BaseAgent` to create specialized agents:

```python
from intelligentAgent.agents.base import BaseAgent
from intelligentAgent.schemas.responses import AgentResponse

class MyCustomAgent(BaseAgent):
    """My custom agent with specialized behavior."""
    
    def run(self, query: str) -> AgentResponse:
        """Custom execution logic."""
        # Implement your agent's unique behavior
        pass
    
    def _think(self, messages):
        """Custom thinking strategy."""
        pass
    
    def _format_system_prompt(self) -> str:
        """Custom system prompt."""
        return "Your custom prompt here"
```

## OpenAI Tool Calling Format

Tools are automatically converted to OpenAI's format:

```json
{
  "type": "function",
  "function": {
    "name": "calculator",
    "description": "Perform mathematical calculations",
    "parameters": {
      "type": "object",
      "properties": {
        "expression": {
          "type": "string",
          "description": "Math expression to evaluate"
        }
      },
      "required": ["expression"]
    }
  }
}
```

Pydantic generates the `parameters` schema automatically from your `args_schema`.

## Configuration

All configuration is managed via `pydantic-settings`:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `OPENAI_MODEL` | Model to use | `gpt-4o` |
| `OPENAI_TEMPERATURE` | Temperature (0-2) | `0.7` |
| `MAX_ITERATIONS` | Max agent iterations | `10` |
| `VERBOSE` | Enable verbose output | `false` |

## Development

### Running Tests
```bash
# Add your test command here when you create tests
```

### Code Style
The project follows:
- Clean code principles
- OOP best practices
- Type hints throughout
- Comprehensive docstrings

## Contributing

Feel free to:
- Add new tools
- Create specialized agents
- Improve prompts
- Enhance error handling
- Add tests

## License

[Your License Here]

## Acknowledgments

- Built with [OpenAI API](https://platform.openai.com/)
- Uses [Pydantic](https://docs.pydantic.dev/) for data validation
- CLI powered by [Rich](https://rich.readthedocs.io/)

