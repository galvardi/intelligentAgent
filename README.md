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


See the `example_queries_*.md` files for detailed example outputs (or end of readme).

### Design Patterns Used

- **Template Method**: Base agent defines the structure, subclasses implement specifics
- **Strategy**: Different thinking strategies per generation type (Reason vs Action vs Summarizer)
- **Registry**: Centralized tool management
- **Composition**: Agent has LLMClient and ToolRegistry
- **Dual Model Pattern**: Reasoning model for complex tasks, inference model for simple tasks

## Installation / Getting started

1. **Clone the repository** (or navigate to the project directory)

2. **Install dependencies**:
```bash
pip install -r requirements.txt
pip install -e .
python main.py
```

3. **Set up environment variables**:
Copy the `.env.example` file and rename the copy to `.env` in the `intelligentAgent/` directory. Then, open the new `.env` file and add your actual OpenAI API key:

```bash
cp intelligentAgent/.env.example intelligentAgent/.env
```

Edit the `.env` file and set:
```
OPENAI_API_KEY=your_openai_api_key_here
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

🌟 **Sample Query #1**

💡 _Compare multiple companies using both market sentiment and stock price data._


╭───────────────────────────────────────────────────────────── Welcome ──────────────────────────────────────────────────────────────╮
│                                                                                                                                    │
│  # 📈 Financial Analysis Agent                                                                                                     │
│                                                                                                                                    │
│  A ReAct-powered agent for data-driven market insights and stock analysis.                                                         │
│  Get real-time stock data, financial news, sentiment analysis, and market trends.                                                  │
│                                                                                                                                    │
│  **Example queries:**                                                                                                              │
│  - "What's the current price and sentiment for Tesla?"                                                                             │
│  - "Compare how AAPL, MSFT, and GOOGL are performing in market"                                                                    │
│  - "Is the negative news about [COMPANY] justified by its stock performance?"                                                      │
│                                                                                                                                    │
│  **Available commands:**                                                                                                           │
│  - `exit` or `quit` - Exit the program                                                                                             │
│  - `help` - Show this help message                                                                                                 │
│  - `tools` - List available tools                                                                                                  │
│  - `clear` - Clear the screen                                                                                                      │
│                                                                                                                                    │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

✓ Agent initialized with 4 tools
Type 'help' for usage information or 'exit' to quit


**+ You:** compare Microsoft, Apple, and Google:- Current stock prices and daily performance- Recent news sentiment for each- Key fundamentals (P/E, market cap, dividend yield)- Which has the most positive news coverage?"

**- Agent:**
╭──────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Based on the collected data, here is the comparison of Microsoft, Apple, and Google:                 │
│                                                                                                      │
│ **Current Stock Prices and Daily Performance:**                                                      │
│ - Microsoft (MSFT): $478.51, up 1.197%                                                               │
│ - Apple (AAPL): $262.36, down 1.8334%                                                                │
│ - Google (GOOG): $314.55, down 0.8729%                                                               │
│                                                                                                      │
│ **Fundamentals (Key Metrics):**                                                                      │
│ - Microsoft:                                                                                         │
│   - Market Cap: ~$3.56 trillion                                                                      │
│   - P/E Ratio: 34.01                                                                                 │
│   - Dividend Yield: 0.72%                                                                            │
│ - Apple:                                                                                             │
│   - Market Cap: ~$3.89 trillion                                                                      │
│   - P/E Ratio: 35.22                                                                                 │
│   - Dividend Yield: 0.38%                                                                            │
│ - Google:                                                                                            │
│   - Fundamentals data unavailable after multiple attempts.                                           │
│                                                                                                      │
│ **Recent News Sentiment:**                                                                           │
│ - Microsoft:                                                                                         │
│   - 2 positive articles, average sentiment 0.35                                                      │
│   - Mentions: 3                                                                                      │
│ - Apple:                                                                                             │
│   - 1 positive article, average sentiment 0.61                                                       │
│   - Mentions: 3                                                                                      │
│ - Google:                                                                                            │
│   - 3 articles, 2 positive, 1 neutral, average sentiment 0.25                                        │
│   - Mentions: 3                                                                                      │
│                                                                                                      │
│ **Most Positive News Coverage:**                                                                     │
│ - Apple has the highest average sentiment score, indicating more positive news coverage relative to  │
│ its mentions.                                                                                        │
│ - Microsoft also has positive coverage but slightly lower sentiment on average.                      │
│ - Google, while having more mentions, has slightly lower sentiment scores.                           │
│                                                                                                      │
│ **Conclusion:**                                                                                      │
│ Apple currently has the most positive news coverage based on sentiment scores, followed by Microsoft │
│ and Google.                                                                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────╯

Tools used: get_stock_data, get_market_news
Iterations: 15

**+ You:** which of three currently has the lowest sentiment

**- Agent:**
╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Google/Alphabet (GOOG) currently has the lowest sentiment with an average sentiment score of 0.25.                                   │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Tools used: none
Iterations: 1

**+ You:** what are the other twos sentiment score

**- Agent:**
╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ The sentiment scores for the other two companies are:                                                                                │
│ - Microsoft (MSFT): 0.35                                                                                                             │
│ - Apple (AAPL): 0.61                                                                                                                 │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Tools used: none
Iterations: 1

**+ You:** what is the sentiment sentiment score of amazon

**- Agent:**
╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ The recent average sentiment score for Amazon (AMZN) based on market news is approximately 0.12, indicating a slightly positive      │
│ sentiment.                                                                                                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Tools used: get_market_news
Iterations: 2

**+ You:** so out of all the companies we spoke about who has the lowest sentiment in the news

**- Agent:**
╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Based on the recent news sentiment data, Amazon (AMZN) has the lowest sentiment with an average score of 0.12. The other companies   │
│ have higher sentiment scores: Google (0.25), Microsoft (0.35), and Apple (0.61).                                                     │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Tools used: none
Iterations: 1

**+ You:** 




🌟 **Sample Query #1 (Verbose)**


╭───────────────────────────────────────────────────────────── Welcome ──────────────────────────────────────────────────────────────╮
│                                                                                                                                    │
│  # 📈 Financial Analysis Agent                                                                                                     │
│                                                                                                                                    │
│  A ReAct-powered agent for data-driven market insights and stock analysis.                                                         │
│  Get real-time stock data, financial news, sentiment analysis, and market trends.                                                  │
│                                                                                                                                    │
│  **Example queries:**                                                                                                              │
│  - "What's the current price and sentiment for Tesla?"                                                                             │
│  - "Compare how AAPL, MSFT, and GOOGL are performing in market"                                                                    │
│  - "Is the negative news about [COMPANY] justified by its stock performance?"                                                      │
│                                                                                                                                    │
│  **Available commands:**                                                                                                           │
│  - `exit` or `quit` - Exit the program                                                                                             │
│  - `help` - Show this help message                                                                                                 │
│  - `tools` - List available tools                                                                                                  │
│  - `clear` - Clear the screen                                                                                                      │
│                                                                                                                                    │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

✓ Agent initialized with 4 tools
Type 'help' for usage information or 'exit' to quit


**+ You:** compare Microsoft, Apple, and Google:- Current stock prices and daily performance- Recent news sentiment for each- Key fundamentals (P/E, market cap, dividend yield)- Which has the most positive news coverage?"

--- Iteration 1 ---
____REASON:

I have the company names Microsoft, Apple, and Google. I need the following information for each:

1. Current stock prices and daily performance.
2. Recent news sentiment.
3. Key fundamentals: P/E ratio, market cap, dividend yield.

To get this information, I need their respective ticker symbols:
- Microsoft: MSFT
- Apple: AAPL
- Alphabet (Google): GOOGL

I can fetch stock data (quote for prices and overview for fundamentals) for MSFT, AAPL, and GOOGL in parallel.

Similarly, I can fetch recent news sentiment for these three symbols.

I will make parallel tool calls for:
- Stock data (quotes and overview)
- Market news sentiment analysis for MSFT, AAPL, GOOGL

This approach will optimize time and get all data needed for comparison.

Next step: Call get_stock_data for quote and overview for MSFT, AAPL, GOOGL, and get_market_news for performance
sentiment.
__________Tools requested: ["get_stock_data with arguments: {'symbol': 'MSFT', 'query_type': 'quote', 
'outputsize': 'compact'}", "get_stock_data with arguments: {'symbol': 'AAPL', 'query_type': 'quote', 
'outputsize': 'compact'}", "get_stock_data with arguments: {'symbol': 'GOOGL', 'query_type': 'quote', 
'outputsize': 'compact'}", "get_stock_data with arguments: {'symbol': 'MSFT', 'query_type': 'overview', 
'outputsize': 'compact'}", "get_stock_data with arguments: {'symbol': 'AAPL', 'query_type': 'overview', 
'outputsize': 'compact'}", "get_stock_data with arguments: {'symbol': 'GOOGL', 'query_type': 'overview', 
'outputsize': 'compact'}", "get_market_news with arguments: {'symbols': 'MSFT', 'query_type': 'performance', 
'sentiment_filter': None, 'language': 'en', 'limit': 3, 'filter_entities': True}", "get_market_news with 
arguments: {'symbols': 'AAPL', 'query_type': 'performance', 'sentiment_filter': None, 'language': 'en', 'limit':
3, 'filter_entities': True}", "get_market_news with arguments: {'symbols': 'GOOGL', 'query_type': 'performance',
'sentiment_filter': None, 'language': 'en', 'limit': 3, 'filter_entities': True}"]
Observation: Stock Quote for MSFT:
• Price: $478.5100
• Change: 5.6600 (1.1970%)
• Open: $473.8000
• High: $478.7...
Observation: Stock Quote for AAPL:
• Price: $262.3600
• Change: -4.9000 (-1.8334%)
• Open: $267.0000
• High: $267...
Observation: Error: Could not fetch quote for 'GOOGL'. Unknown error...
Observation: Error: Could not fetch overview for 'MSFT'. Unknown error...
Observation: Error: Could not fetch overview for 'AAPL'. Unknown error...
Observation: Error: Could not fetch overview for 'GOOGL'. Unknown error...
Observation: 📊 Market Performance for MSFT
Based on analysis of 3 recent articles
===============================...
Observation: 📊 Market Performance for AAPL
Based on analysis of 3 recent articles
===============================...
Observation: 📊 Market Performance for GOOGL
Based on analysis of 3 recent articles
==============================...

--- Iteration 2 ---
____REASON:

1. What information do I have so far?
- Current stock prices and daily performance for MSFT and AAPL:
  - MSFT: $478.51 (+1.20%)
  - AAPL: $262.36 (-1.83%)
- Could not fetch current stock price for GOOGL.
- Recent news sentiment performance (from 3 articles each):
  - MSFT average sentiment: 0.35, with 2 positive articles, 0 negative.
  - AAPL average sentiment: 0.54, with 3 positive articles, 0 negative.
  - GOOGL average sentiment: 0.21, with 2 positive articles, 0 negative, 1 neutral.
- Could not fetch key fundamentals (P/E, market cap, dividend yield) for any of the three.

2. What do I still need?
- Current stock price and daily performance for GOOGL.
- Key fundamentals (P/E ratio, market cap, dividend yield) for MSFT, AAPL, GOOGL.

3. What tool calls should I make next and in what order?
- The previous errors for overview and GOOGL quote may be due to symbol GOOGL (Alphabet) not being recognized as
expected by the data source. Sometimes "GOOG" is used as ticker symbol alongside "GOOGL".
- To get correct stock data for Alphabet, I will try to search for correct ticker for "Alphabet" using 
get_stock_data search.
- Then fetch the correct quote and overview for Alphabet.
- I'll also retry overview for MSFT and AAPL to get fundamentals.
- I will run these searches and data fetches in parallel to save time.

Next step:
- Use get_stock_data search to find the correct ticker symbol for Alphabet.
- Then use get_stock_data to fetch quote and overview for the correct Alphabet ticker.
- Retry get_stock_data overview for MSFT and AAPL.
__________Tools requested: ["get_stock_data with arguments: {'symbol': 'Alphabet', 'query_type': 'search', 
'outputsize': 'compact'}", "get_stock_data with arguments: {'symbol': 'MSFT', 'query_type': 'overview', 
'outputsize': 'compact'}", "get_stock_data with arguments: {'symbol': 'AAPL', 'query_type': 'overview', 
'outputsize': 'compact'}"]
Observation: Search results for 'Alphabet':

1. Alphabet Inc
                        Symbol: ABEC.DEX
           ...
Observation: Company Overview for MSFT:
                    • Name: Microsoft Corporation
                    • S...
Observation: Company Overview for AAPL:
                    • Name: Apple Inc
                    • Sector: TECHN...

--- Iteration 3 ---
____REASONING STEP-BY-STEP:

1. What information do I have now?
- For Microsoft (MSFT):
  - Current price: $478.51 (+1.20%)
  - Key fundamentals: Market cap $3.56T, P/E 34.01, Dividend yield 0.72%
- For Apple (AAPL):
  - Current price: $262.36 (-1.83%)
  - Key fundamentals: Market cap $3.89T, P/E 35.22, Dividend yield 0.38%
- For Alphabet (Google):
  - Search results show multiple tickers, including "GOOGL" (U.S., Class A shares) with moderate match score.
  - No current price or fundamentals fetched yet.
- News sentiment from recent articles:
  - MSFT: Average 0.35, 2 positive, 0 negative mentions
  - AAPL: Average 0.54, 3 positive, 0 negative mentions
  - GOOGL: Average 0.21, 2 positive, 0 negative, 1 neutral mentions

2. What do I still need?
- Current stock price and daily performance for Alphabet’s U.S. ticker "GOOGL".
- Key fundamentals (P/E, market cap, dividend yield) for Alphabet "GOOGL".
- Confirm daily price change to compare performance fully.

3. What tool calls should I make next and in what order?
- Since the ticker "GOOGL" is confirmed for Alphabet Inc. (Class A) in the U.S. exchange:
  - Fetch stock quote for "GOOGL" (for current price and daily performance).
  - Fetch company overview (fundamentals) for "GOOGL".
  
These two calls can be made in parallel to save time.

Once I have this data, I can complete the full comparison.
__________Tools requested: ["get_stock_data with arguments: {'symbol': 'GOOGL', 'query_type': 'quote', 
'outputsize': 'compact'}", "get_stock_data with arguments: {'symbol': 'GOOGL', 'query_type': 'overview', 
'outputsize': 'compact'}"]
Observation: Stock Quote for GOOGL:
• Price: $314.3400
• Change: -2.2000 (-0.6950%)
• Open: $316.4000
• High: $32...
Observation: Company Overview for GOOGL:
                    • Name: Alphabet Inc Class A
                    • S...

--- Iteration 4 ---
____Step-by-step analysis:

1. What information do I have now?
- Microsoft (MSFT):
  - Current price: $478.51, up 1.20% today.
  - Market cap: $3.56 trillion.
  - P/E ratio: 34.01.
  - Dividend yield: 0.72%.
  - News sentiment: average 0.35 from 3 articles, all positive or neutral.
- Apple (AAPL):
  - Current price: $262.36, down 1.83% today.
  - Market cap: $3.89 trillion.
  - P/E ratio: 35.22.
  - Dividend yield: 0.38%.
  - News sentiment: average 0.54 from 3 articles, all positive.
- Alphabet (GOOGL):
  - Current price: $314.34, down 0.695% today.
  - Market cap: $3.81 trillion.
  - P/E ratio: 31.06.
  - Dividend yield: 0.32%.
  - News sentiment: average 0.21 from 3 articles, mostly positive but one neutral.

2. What do I still need?
- I have comprehensive price, fundamentals, and sentiment data for all three companies now.
- To complete the analysis, I should cross-verify if there is any additional trending or more recent news 
coverage that could affect current sentiment.
- I could also provide a clear summary of which company has the most positive news coverage overall.

3. What tool calls should I make next and in what order?
- I could call get_market_news with query_type='trending' to see if any of these three companies are currently 
trending in the news.
- Alternatively, no further calls are strictly necessary for the basic comparison requested.

Given that I have all requested data, I will proceed to provide a concise comparative summary including current 
prices, market performance, fundamentals, news sentiment, and identify who has the most positive news coverage.
__________Loop counter: 1, current context length: 5346

**- Agent:**
╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Based on the data:                                                                                           │
│                                                                                                              │
│ **Microsoft (MSFT):**                                                                                        │
│ - Current price: $478.51 (+1.20%)                                                                            │
│ - Market cap: $3.56 trillion                                                                                 │
│ - P/E ratio: 34.01                                                                                           │
│ - Dividend yield: 0.72%                                                                                      │
│ - Recent news sentiment: Average 0.35, mostly positive                                                       │
│                                                                                                              │
│ **Apple (AAPL):**                                                                                            │
│ - Current price: $262.36 (-1.83%)                                                                            │
│ - Market cap: $3.89 trillion                                                                                 │
│ - P/E ratio: 35.22                                                                                           │
│ - Dividend yield: 0.38%                                                                                      │
│ - Recent news sentiment: Highest average at 0.54, all positive                                               │
│                                                                                                              │
│ **Google/Alphabet (GOOGL):**                                                                                 │
│ - Current price: $314.34 (-0.695%)                                                                           │
│ - Market cap: $3.81 trillion                                                                                 │
│ - P/E ratio: 31.06                                                                                           │
│ - Dividend yield: 0.32%                                                                                      │
│ - Recent news sentiment: Lowest at 0.21, mostly positive but with some neutral coverage                      │
│                                                                                                              │
│ **Conclusion:**                                                                                              │
│ - Among the three, **Apple** has the most positive recent news coverage, followed by Microsoft and then      │
│ Google/Alphabet.                                                                                             │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────


🌟 **Sample Query #2**

💡 _News-Driven Trading Signals_

╭─────────────────────────────────────────────────────────────────── Welcome ───────────────────────────────────────────────────────────────────╮
│                                                                                                                                               │
│  # 📈 Financial Analysis Agent                                                                                                                │
│                                                                                                                                               │
│  A ReAct-powered agent for data-driven market insights and stock analysis.                                                                    │
│  Get real-time stock data, financial news, sentiment analysis, and market trends.                                                             │
│                                                                                                                                               │
│  **Example queries:**                                                                                                                         │
│  - "What's the current price and sentiment for Tesla?"                                                                                        │
│  - "Compare how AAPL, MSFT, and GOOGL are performing in the market"                                                                           │
│  - "Is the negative news about [COMPANY] justified by its stock performance?"                                                                 │
│                                                                                                                                               │
│  **Available commands:**                                                                                                                      │
│  - `exit` or `quit` - Exit the program                                                                                                        │
│  - `help` - Show this help message                                                                                                            │
│  - `tools` - List available tools                                                                                                             │
│  - `clear` - Clear the screen                                                                                                                 │
│                                                                                                                                               │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

✓ Agent initialized with 4 tools
Type 'help' for usage information or 'exit' to quit


**+ You:** Find me stocks with overwhelmingly positive news sentiment past week but check what movement there stock has made this week

**- Agent:**
╭───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ The stock of Costco Wholesale Corporation (COST) has increased by approximately 9.49% over the past week, indicating a positive price         │
│ movement that aligns with the overwhelmingly positive news sentiment. Similarly, GoldHaven Resources Corp (GHVNF) showed a positive price     │
│ change from $0.0822 to $0.0900, reflecting a positive trend consistent with the positive news articles. Overall, the data suggests that       │
│ positive news sentiment this past week is associated with upward price movements for both stocks.                                             │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Tools used: calculator, get_market_news, get_stock_data
Iterations: 7

**+ You:** out of the stocks with positve news sentiment is there a stock that its price hasnt moved yet    

**- Agent:**
╭───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Based on the current data, the stock GoldHaven Resources Corp. (GHVNF) with positive news sentiment has experienced a significant increase of │
│ approximately 9.49% in its price over the past week. Similarly, Costco Wholesale Corporation (COST), also with positive sentiment, has shown  │
│ a minimal price change of about 0.97%, indicating very little movement.                                                                       │
│                                                                                                                                               │
│ Therefore, among the stocks with positive news sentiment, COST’s price has not moved substantially and can be considered as a stock whose     │
│ price has remained relatively stable despite positive news.                                                                                   │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Tools used: calculator
Iterations: 4

**+ You:** are there stocks that a have positive sentiment but there price has decreased         

**- Agent:**
╭───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ The weekly price change for TAP (Molson Coors) is approximately -1.33%. This indicates that despite positive news sentiment, the stock        │
│ experienced a slight decrease in price over the past week.                                                                                    │
│                                                                                                                                               │
│ Summary of findings:                                                                                                                          │
│ - GHVNF and ONCY had significant positive price movements (+9.49% and +10.39%, respectively) despite their positive news sentiment.           │
│ - COST's price increased slightly (+0.97%) with positive sentiment.                                                                           │
│ - TAP experienced a small decline (~-1.33%) despite positive news sentiment.                                                                  │
│                                                                                                                                               │
│ Conclusion:                                                                                                                                   │
│ Among the stocks analyzed, TAP shows a positive news sentiment but a decrease in price over the past week. Other stocks with positive         │
│ sentiment generally experienced price increases.                                                                                              │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Tools used: calculator, get_market_news, get_stock_data
Iterations: 8

**+ You:** 






🌟 **Sample Query #3**

💡 _Fact-Checking Financial Claims_

╭─────────────────────────────────────────────────────────────────────── Welcome ───────────────────────────────────────────────────────────────────────╮
│                                                                                                                                                       │
│  # 📈 Financial Analysis Agent                                                                                                                        │
│                                                                                                                                                       │
│  A ReAct-powered agent for data-driven market insights and stock analysis.                                                                            │
│  Get real-time stock data, financial news, sentiment analysis, and market trends.                                                                     │
│                                                                                                                                                       │
│  **Example queries:**                                                                                                                                 │
│  - "What's the current price and sentiment for Tesla?"                                                                                                │
│  - "Compare how AAPL, MSFT, and GOOGL are performing in the market"                                                                                   │
│  - "Is the negative news about [COMPANY] justified by its stock performance?"                                                                         │
│                                                                                                                                                       │
│  **Available commands:**                                                                                                                              │
│  - `exit` or `quit` - Exit the program                                                                                                                │
│  - `help` - Show this help message                                                                                                                    │
│  - `tools` - List available tools                                                                                                                     │
│  - `clear` - Clear the screen                                                                                                                         │
│                                                                                                                                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

✓ Agent initialized with 4 tools
Type 'help' for usage information or 'exit' to quit


**+ You:** I heard Tesla is at an all-time high. Verify this by checking current price against 52-week high data

**- Agent:**
╭───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Based on the current data:                                                                                                                            │
│                                                                                                                                                       │
│ - Tesla's current stock price is approximately $432.96.                                                                                               │
│ - The 52-week high for Tesla is approximately $498.83.                                                                                                │
│ - Tesla's stock is below its 52-week high, indicating it is not at an all-time high.                                                                  │
│ - Recent news and analyst sentiment are mixed but do not suggest that Tesla is currently at its peak value.                                           │
│                                                                                                                                                       │
│ Therefore, Tesla is not at an all-time high currently.                                                                                                │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Tools used: get_stock_data, get_market_news
Iterations: 5

**+ You:** 



