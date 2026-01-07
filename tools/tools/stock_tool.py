"""Stock market data tool using Alpha Vantage API."""

from pydantic import BaseModel, Field
from typing import Type, Literal, Dict, Any
from requests import Response
import requests
from intelligentAgent.tools.base import BaseTool
from intelligentAgent.config import AgentConfig


class StockInput(BaseModel):
    """Input schema for stock market data tool."""
    
    symbol: str = Field(
        ...,
        description="Stock ticker symbol (e.g., 'IBM', 'AAPL', 'GOOGL')"
    )
    
    query_type: Literal["quote", "overview", "daily", "search"] = Field(
        default="quote",
        description="Type of data to fetch: 'quote' (real-time price), 'overview' (company info), 'daily' (price history), 'search' (find ticker symbols)"
    )
    
    outputsize: Literal["compact"] = Field(
        default="compact",
        description="For daily data: 'compact' returns last 100 data points" # full is not supported in free api
    )


class StockTool(BaseTool):
    """Tool for fetching stock market data using Alpha Vantage API.
    
    Provides real-time quotes, company information, historical prices, and ticker search.
    """
    
    name: str = "get_stock_data"
    description: str = (
        "Get stock market data including real-time quotes, company information, "
        "and historical prices. Use 'quote' for current price, 'overview' for company details, "
        "'daily' for price history, or 'search' to find ticker symbols."
    )
    args_schema: Type[BaseModel] = StockInput
    BASE_URL: str = "https://www.alphavantage.co/query"
    
    def __init__(self):
        """Initialize the stock tool with API configuration."""
        super().__init__()
        self.config: AgentConfig = AgentConfig()
        self.api_key: str = self.config.alphavantage_api_key
        self.base_url: str = self.BASE_URL
    
    def execute(self, symbol: str, query_type: str = "quote", outputsize: str = "compact") -> str:
        """Fetch stock market data from Alpha Vantage.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
            query_type: Type of data to fetch. Options:
                - 'quote': Real-time stock quote with current price, change, volume,
                          open/high/low, and previous close
                - 'overview': Company fundamental data including name, sector, industry,
                             market cap, P/E ratio, EPS, moving averages, and description
                - 'daily': Historical daily price data (OHLCV) for the last 5 trading days
                          with option to get full history via outputsize parameter
                - 'search': Search for stock symbols by company name or keywords,
                           returns matching companies with ticker symbols
            outputsize: Size of data return for 'daily' queries:
                - 'compact': Returns last 100 data points (default)
                - 'full': Returns complete historical data
            
        Returns:
            Formatted string with stock data appropriate to the query type
        """
        try:
            if query_type == "quote":
                return self._get_quote(symbol)
            elif query_type == "overview":
                return self._get_overview(symbol)
            elif query_type == "daily":
                return self._get_daily(symbol, outputsize)
            elif query_type == "search":
                return self._search_symbol(symbol)
            else:
                return f"Error: Unknown query_type '{query_type}'"
                
        except Exception as e:
            return f"Error fetching stock data: {str(e)}"
    
    def _make_api_request(self, params: Dict[str, str]) -> Dict[str, Any]:
        """Make an API request to Alpha Vantage and return JSON data.
        
        Args:
            params: Dictionary of query parameters for the API request
            
        Returns:
            JSON response data as a dictionary
            
        Raises:
            requests.HTTPError: If the HTTP request fails
        """
        response: Response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        return response.json()
    
    def _get_quote(self, symbol: str) -> str:
        """Get real-time quote data for a stock.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Formatted quote information
        """
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        data = self._make_api_request(params)
        
        if "Global Quote" not in data:
            return f"Error: Could not fetch quote for '{symbol}'. {data.get('Note', data.get('Error Message', 'Unknown error'))}"
        
        quote = data["Global Quote"]
        
        if not quote:
            return f"Error: No data found for symbol '{symbol}'. Please verify the ticker symbol."
        
        # Format the response
        result: str = (
            f"Stock Quote for {symbol}:\n"
            f"• Price: ${quote.get('05. price', 'N/A')}\n"
            f"• Change: {quote.get('09. change', 'N/A')} ({quote.get('10. change percent', 'N/A')})\n"
            f"• Open: ${quote.get('02. open', 'N/A')}\n"
            f"• High: ${quote.get('03. high', 'N/A')}\n"
            f"• Low: ${quote.get('04. low', 'N/A')}\n"
            f"• Volume: {quote.get('06. volume', 'N/A')}\n"
            f"• Previous Close: ${quote.get('08. previous close', 'N/A')}\n"
            f"• Latest Trading Day: {quote.get('07. latest trading day', 'N/A')}"
        )
        
        return result
    
    def _get_overview(self, symbol: str) -> str:
        """Get company overview and fundamental data.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Formatted company information
        """
        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        data = self._make_api_request(params)
        
        if not data or "Symbol" not in data:
            return f"Error: Could not fetch overview for '{symbol}'. {data.get('Note', data.get('Error Message', 'Unknown error'))}"
        
        # Format the response with key information
        description: str = data.get('Description', 'N/A')
        if len(description) > 200:
            description = description[:200] + "..."
        
        result: str = f"""Company Overview for {symbol}:
                    • Name: {data.get('Name', 'N/A')}
                    • Sector: {data.get('Sector', 'N/A')}
                    • Industry: {data.get('Industry', 'N/A')}
                    • Market Cap: ${data.get('MarketCapitalization', 'N/A')}
                    • P/E Ratio: {data.get('PERatio', 'N/A')}
                    • EPS: {data.get('EPS', 'N/A')}
                    • 52 Week High: ${data.get('52WeekHigh', 'N/A')}
                    • 52 Week Low: ${data.get('52WeekLow', 'N/A')}
                    • 50 Day MA: ${data.get('50DayMovingAverage', 'N/A')}
                    • 200 Day MA: ${data.get('200DayMovingAverage', 'N/A')}
                    • Dividend Yield: {data.get('DividendYield', 'N/A')}
                    • Exchange: {data.get('Exchange', 'N/A')}
                    • Country: {data.get('Country', 'N/A')}
                    • Description: {description}
                    """
        
        return result
    
    def _get_daily(self, symbol: str, outputsize: str) -> str:
        """Get daily time series price data.
        
        Args:
            symbol: Stock ticker symbol
            outputsize: 'compact' for last 100 days, 'full' for complete history
            
        Returns:
            Formatted daily price data
        """
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": outputsize,
            "apikey": self.api_key
        }
        
        data = self._make_api_request(params)
        
        if "Time Series (Daily)" not in data:
            return f"Error: Could not fetch daily data for '{symbol}'. {data.get('Note', data.get('Error Message', 'Unknown error'))}"
        
        time_series: Dict[str, Dict[str, str]] = data["Time Series (Daily)"]
        meta_data: Dict[str, str] = data.get("Meta Data", {})
        
        # Get the most recent 5 days
        recent_dates = sorted(time_series.keys(), reverse=True)[:5]
        
        result = f"""Daily Price Data for {symbol}:
                Last Refreshed: {meta_data.get('3. Last Refreshed', 'N/A')}
                Timezone: {meta_data.get('5. Time Zone', 'N/A')}

                Recent Trading Days (last 5):
                """
        
        for date in recent_dates:
            day_data = time_series[date]
            result += f"""
                    {date}:
                    Open: ${day_data.get('1. open', 'N/A')}
                    High: ${day_data.get('2. high', 'N/A')}
                    Low: ${day_data.get('3. low', 'N/A')}
                    Close: ${day_data.get('4. close', 'N/A')}
                    Volume: {day_data.get('5. volume', 'N/A')}
                    """
        
        result += f"\nTotal data points available: {len(time_series)}"
        
        return result
    
    def _search_symbol(self, keywords: str) -> str:
        """Search for stock symbols by company name or keywords.
        
        Args:
            keywords: Search keywords (company name, etc.)
            
        Returns:
            List of matching stock symbols
        """
        params = {
            "function": "SYMBOL_SEARCH",
            "keywords": keywords,
            "apikey": self.api_key
        }
        
        data = self._make_api_request(params)
        
        if "bestMatches" not in data:
            return f"Error: Could not search for '{keywords}'. {data.get('Note', data.get('Error Message', 'Unknown error'))}"
        
        matches = data["bestMatches"]
        
        if not matches:
            return f"No matches found for '{keywords}'"
        
        result = f"Search results for '{keywords}':\n\n"
        
        for i, match in enumerate(matches[:10], 1):  # Show top 10 matches
            result += f"""{i}. {match.get('2. name', 'N/A')}
                        Symbol: {match.get('1. symbol', 'N/A')}
                        Type: {match.get('3. type', 'N/A')}
                        Region: {match.get('4. region', 'N/A')}
                        Match Score: {match.get('9. matchScore', 'N/A')}

                        """
        
        return result

