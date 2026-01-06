# Quick Start Guide

Get up and running with the Intelligent Agent in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure OpenAI API Key

Create a `.env` file in the project root:

```bash
# On macOS/Linux
echo "OPENAI_API_KEY=your_api_key_here" > .env

# Or manually create the file with:
# OPENAI_API_KEY=your_actual_api_key
# OPENAI_MODEL=gpt-4o
```

Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys).

## Step 3: Run the Agent

Interactive mode:
```bash
python -m intelligentAgent.main
```

With verbose output (see reasoning steps):
```bash
python -m intelligentAgent.main --verbose
```

Single query:
```bash
python -m intelligentAgent.main --query "What is 15 * 23?"
```

## Step 4: Try Some Examples

Once running, try these queries:

1. **Simple calculation**:
   ```
   What is 144 / 12?
   ```

2. **Complex math**:
   ```
   Calculate the square root of 256 plus 10
   ```

3. **Current time**:
   ```
   What time is it?
   ```

4. **Multi-step**:
   ```
   What is the current time and what is 100 + 50?
   ```

## Understanding the Output

### Normal Mode
```
You: What is 25 * 4?

Agent:
The result is 100.

Tools used: calculator
Iterations: 1
```

### Verbose Mode
```
You: What is 25 * 4?

--- Iteration 1 ---
Tools requested: ['calculator']
Tool result: Result: 100...

Agent:
The result is 100.

Tools used: calculator
Iterations: 1
```

## Next Steps

- **Add custom tools**: See README.md for creating your own tools
- **Create specialized agents**: Extend `BaseAgent` for custom behavior
- **Adjust configuration**: Modify `.env` for different models or settings

## Troubleshooting

### "Import could not be resolved" warnings
Run `pip install -r requirements.txt` to install dependencies.

### "Error initializing agent"
Make sure you have:
1. Created a `.env` file
2. Added your `OPENAI_API_KEY` to the `.env` file
3. Have a valid OpenAI API key with available credits

### Agent doesn't complete tasks
Try increasing `MAX_ITERATIONS` in your `.env` file:
```
MAX_ITERATIONS=20
```

## Architecture Overview

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ ReActAgent  │ ← Chain of Thought System Prompt
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  LLMClient  │ ← OpenAI API (Tool Calling)
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ Tool System │ ← Calculator, DateTime, etc.
└─────────────┘
```

The agent follows a simple loop:
1. **Think**: Reason about what to do (via LLM)
2. **Act**: Execute tools if needed
3. **Observe**: Process results
4. **Repeat**: Until task is complete

Happy coding! 🚀

