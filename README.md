# Financial Analysis Agent 📈

A specialized ReAct (Reasoning + Acting) agent for data-driven market insights and stock analysis. Built with proper OOP principles using OpenAI's API and Pydantic for structured outputs.

The agent provides real-time stock data, financial news, sentiment analysis, and market trends by combining multiple financial APIs (Alpha Vantage and Marketaux) to deliver comprehensive market intelligence.

## Features

- **Financial Analysis Specialist**: Focused on stock market data, news sentiment, and market trends
- **Anti-Hallucination**: Grounds all responses in real-time API data - never guesses prices or fundamentals
- **ReAct Pattern**: Interleaves reasoning (thinking) with actions (tool execution) and chain of thought
- **Multi-Source Data**: Combines stock market data (Alpha Vantage) with financial news (Marketaux)
- **Sentiment Analysis**: Analyzes news sentiment and correlates it with actual price movements
- **Dual Model System**: Uses different OpenAI models for reasoning vs. inference tasks (for cost efficiency)
- **Agnostic to LLM Provider**: LLM calls are made through a wrapper client—add a different provider by implementing a new client.
- **Context Managment**: Reasoning model receives all of conversation history, where action model receives current reAct loop (needs only reasoning to decide tool calls)
- **Context Compaction**: once model context reaches a certin size (hyper parameter needs adjusting) or number of react loops a reach (hyper parameter) a seprate conversation compaction agent starts compacting the reAct loops stating from the begining 
- **Type-Safe Tools**: Pydantic models for automatic validation and schema generation
- **Rich CLI**: Beautiful interactive interface with verbose mode
- **Extensible Architecture**: Clean OOP design with abstract base classes


## See the `example_queries_*.md` files for detailed example outputs (use code view if in github).

### Design Patterns Used

- **Template Method**: Base agent defines the structure, subclasses implement specifics
- **Strategy**: Different thinking strategies per generation type (Reason vs Action vs Summarizer)
- **Registry**: Centralized tool management
- **Composition**: Agent has LLMClient and ToolRegistry
- **Dual Model Pattern**: Reasoning model for complex tasks, inference model for simple tasks

## Installation / Getting started

1. **Clone the repository** (and navigate to the repo directory)

2. **Set up environment variables**:
Copy the `.env.example` file and rename the copy to `.env` in the `intelligentAgent/` directory. Then, open the new `.env` file and add your actual OpenAI API key:

```bash
cp intelligentAgent/.env.example intelligentAgent/.env
```

Edit the `.env` file and set: 
```
OPENAI_API_KEY=your_openai_api_key_here
```
or alternativly export OPENAI_API_KEY=your_openai_api_key_here

3. **Install dependencies**:
   ### using uv:
   ```bash
     uv sync
     uv run main.py 
  ```

   ### Traditional way using pip:
```bash
required python version at least 3.9 

python3 -m venv venv # if you wish to create a venv
source venv/bin/activate  # activate venv

pip install --upgrade pip  # you may need to upgrage pip
pip install -r requirements.txt
pip install -e .
python main.py
```

**Getting API Keys:**
currently set my own free tier api keys for new and stocks

- OpenAI: https://platform.openai.com/api-keys
- Alpha Vantage (free): https://www.alphavantage.co/support/#api-key
- Marketaux (free tier): https://www.marketaux.com/

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



## Project Structure

```
intelligentAgent/
├── agents/
│   ├── base.py              # Abstract BaseAgent class
│   ├── react.py             # ReActAgent implementation (financial analysis)
│   └── summarizer.py        # SummarizerAgent (conversation compaction)
├── llm/
│   ├── client.py            # OpenAI client wrapper with dual model support
│   └── models.py            # LLM response models
├── tools/
│   ├── base.py              # Abstract BaseTool class
│   ├── registry.py          # Tool registry
│   └── examples/
│       ├── stock_tool.py        # Alpha Vantage stock data
│       ├── marketaux_tool.py    # Marketaux financial news
│       ├── calculator.py        # Calculator tool
│       └── datetime_tool.py     # DateTime tool
├── schemas/         
│   ├── messages.py          # Message types
│   └── responses.py         # Response types
├── prompts/
│   ├── react.py             # Financial analysis ReAct prompts
│   └── summarizer.py        # Summarization prompts
├── config.py                # Pydantic settings with API keys
├── main.py                  # CLI entry point
├── example_queries_*.md     # Example outputs
└── .env.example             # Environment template
```

## How It Works: Anti-Hallucination Design

The agent is designed to **never hallucinate financial data**:

1. **No Guessing**: The agent is explicitly instructed to use tools for all financial data
2. **Real-Time Data**: All prices, fundamentals, and news come from live APIs
3. **Cross-Validation**: News sentiment is compared against actual stock performance
5. **Grounded Responses**: Every claim is backed by tool-retrieved data

Example of the agent's reasoning:
```
Thought: I need Tesla's current stock price. I will NOT guess - I must use get_stock_data.
Action: get_stock_data(symbol="TSLA", query_type="quote")
Observation: Current price is $254.32, up 2.3% today.
```

## Available Tools

### StockTool (Alpha Vantage)
- **Quote**: Real-time stock prices, volume, open/high/low
- **Overview**: Company fundamentals (P/E ratio, market cap, EPS, etc.)
- **Daily**: Historical OHLCV price data
- **Search**: Find ticker symbols by company name

### MarketauxTool
- **News**: Financial news articles with sentiment scores
- **Entity Search**: Find companies/entities by name
- **Trending**: Currently trending stocks in the market
- **Performance**: Market performance with sentiment statistics

### Utility Tools
- **Calculator**: Mathematical calculations
- **DateTime**: Current date/time information

## Configuration

All configuration is managed via `pydantic-settings` in `config.py`:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `OPENAI_REASONING_MODEL` | Model for complex reasoning | `gpt-4o-mini` |
| `OPENAI_INFERENCE_MODEL` | Model for simple tasks | `gpt-4o-nano` |
| `ALPHAVANTAGE_API_KEY` | Alpha Vantage API key | Required |
| `MARKETAUX_API_KEY` | Marketaux API key | Required |
| `MAX_ITERATIONS` | Max agent iterations | `20` |
| `VERBOSE` | Enable verbose output | `false` |
| `COMPACT_AFTER_LOOPS` | Loops before compaction | `15` |
| `COMPACT_CONTEXT_THRESHOLD` | Token threshold for compaction | `50000` |

## Development

### Code Style
The project follows:
- Clean code principles
- OOP best practices
- Type hints throughout
- Comprehensive docstrings

## Key Features Explained

### Dual Model System
The agent uses two OpenAI models:
- **Reasoning Model** (gpt-4o-mini): For complex financial analysis and multi-step reasoning
- **Inference Model** (gpt-4o-nano): For simple tasks like conversation summaries

This optimizes for both quality and cost.

### Conversation Compaction
Long conversations are automatically summarized to maintain context while staying within token limits. The `SummarizerAgent` condenses previous reAct loops while preserving key information such as user prompts, the compaction starts from the first loop.

### Parallel Tool Execution
The agent intelligently decides when to fetch data in parallel vs. sequentially:

## Use Cases

1. **Investment Research**: Comprehensive analysis combining fundamentals and sentiment
2. **Sentiment Analysis**: Compare news sentiment with actual price movements
3. **Market Monitoring**: Track trending stocks and validate with real data
4. **Company Comparison**: Multi-stock analysis with fundamentals and news
5. **Fact-Checking**: Verify financial claims with real-time API data
6. **Portfolio Analysis**: Research multiple holdings simultaneously

## Acknowledgments

- Built with [OpenAI API](https://platform.openai.com/)
- Uses [Pydantic](https://docs.pydantic.dev/) for data validation
- CLI powered by [Rich](https://rich.readthedocs.io/)
- Financial data from [Alpha Vantage](https://www.alphavantage.co/) and [Marketaux](https://www.marketaux.com/)
