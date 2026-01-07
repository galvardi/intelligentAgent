"""Financial news and market data tool using Marketaux API."""

from pydantic import BaseModel, Field
from typing import Type, Literal, Optional, Dict, Any
from requests import Response
import requests
from intelligentAgent.tools.base import BaseTool
from intelligentAgent.config import AgentConfig


class MarketauxInput(BaseModel):
    """Input schema for marketaux financial news and market data tool."""
    
    symbols: Optional[str] = Field(
        default=None,
        description=(
            "Stock ticker symbols - comma-separated for multiple (e.g., 'TSLA,AAPL,MSFT'). "
            "REQUIRED for 'news' and 'performance' query types to specify which stocks to get data for. "
            "For 'entity_search', provide company name or keywords to search for (e.g., 'Tesla', 'Apple', 'electric vehicles'). "
            "Not needed for 'trending' query type (leave empty or None)."
        )
    )
    
    query_type: Literal["news", "entity_search", "trending", "performance"] = Field(
        default="news",
        description=(
            "Type of data to fetch:\n"
            "• 'news': Get financial news articles about SPECIFIC STOCKS (requires symbols='AAPL,MSFT')\n"
            "• 'entity_search': Search for companies/entities by name or keywords (requires symbols='Tesla' or symbols='AI companies')\n"
            "• 'trending': Get currently trending stocks in the news (no symbols needed)\n"
            "• 'performance': Get sentiment analysis and stats for SPECIFIC STOCKS (requires symbols='TSLA,NVDA')"
        )
    )
    
    sentiment_filter: Optional[Literal["positive", "negative", "neutral"]] = Field(
        default=None,
        description="Filter news by sentiment: 'positive', 'negative', or 'neutral'"
    )
    
    language: str = Field(
        default="en",
        description="Language code for news articles (e.g., 'en' for English)"
    )
    
    limit: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Number of results to return (1-50)"
    )
    
    filter_entities: bool = Field(
        default=True,
        description="When true, only return entities relevant to your query with each article"
    )


class MarketauxTool(BaseTool):
    """Tool for fetching financial news and market data using Marketaux API.
    
    Provides access to global financial news, entity search, trending stocks, 
    and market performance data with sentiment analysis.
    """
    
    name: str = "get_market_news"
    description: str = (
        "Get financial news and market data with AI-powered sentiment analysis from 5,000+ global sources. "
        "CRITICAL: The 'symbols' parameter is REQUIRED for most query types.\n\n"
        "QUERY TYPES & REQUIREMENTS:\n"
        "1. 'news' - Financial news articles about specific stocks\n"
        "   → MUST provide: symbols='TSLA' or symbols='AAPL,MSFT,GOOGL'\n"
        "   → Optional: sentiment_filter='positive'/'negative'/'neutral'\n\n"
        "2. 'performance' - Sentiment stats & mention counts for specific stocks\n"
        "   → MUST provide: symbols='NVDA,AMD' or symbols='TSLA'\n\n"
        "3. 'trending' - Currently most-mentioned stocks in recent news\n"
        "   → No symbols needed (analyzes all recent news)\n\n"
        "4. 'entity_search' - Search for companies/entities by name\n"
        "   → MUST provide: symbols='Tesla' or symbols='electric vehicle companies'\n"
        "   → Use company names or keywords, NOT ticker symbols\n\n"
        "EXAMPLES:\n"
        "• News: symbols='TSLA', query_type='news', sentiment_filter='positive'\n"
        "• Performance: symbols='AAPL,MSFT', query_type='performance'\n"
        "• Trending: query_type='trending', limit=10\n"
        "• Search: symbols='artificial intelligence', query_type='entity_search'"
    )
    args_schema: Type[BaseModel] = MarketauxInput
    BASE_URL: str = "https://api.marketaux.com/v1"
    
    def __init__(self):
        """Initialize the marketaux tool with API configuration."""
        super().__init__()
        self.config: AgentConfig = AgentConfig()
        self.api_key: str = self.config.marketaux_api_key
        self.base_url: str = self.BASE_URL
    
    def execute(
        self,
        symbols: Optional[str] = None,
        query_type: str = "news",
        sentiment_filter: Optional[str] = None,
        language: str = "en",
        limit: int = 5,
        filter_entities: bool = True
    ) -> str:
        """Fetch financial news and market data from Marketaux.
        
        Args:
            symbols: Comma-separated stock ticker symbols (e.g., 'AAPL,MSFT,GOOGL').
                    Required for 'news' and 'performance' query types.
            query_type: Type of data to fetch:
                - 'news': Financial news articles about specific stocks with sentiment analysis
                - 'entity_search': Search for companies/entities by name or keywords
                - 'trending': Get currently trending entities/stocks in the market
                - 'performance': Market performance data and statistics
            sentiment_filter: Filter news by sentiment:
                - 'positive': Only positive sentiment news
                - 'negative': Only negative sentiment news
                - 'neutral': Only neutral sentiment news
                - None: All sentiment
            language: Language code for news articles (default: 'en' for English)
            limit: Number of results to return (1-50, default: 5)
            filter_entities: If True, only return entities relevant to query
            
        Returns:
            Formatted string with news/market data appropriate to the query type
        """
        try:
            if query_type == "news":
                if not symbols:
                    return "Error: 'symbols' parameter is required for news queries. Please provide stock ticker symbols (e.g., 'AAPL,MSFT')."
                return self._get_news(symbols, sentiment_filter, language, limit, filter_entities)
            elif query_type == "entity_search":
                if not symbols:
                    return "Error: 'symbols' parameter is required for entity search. Use it as search keywords (e.g., 'Apple', 'Microsoft')."
                return self._search_entity(symbols, limit)
            elif query_type == "trending":
                return self._get_trending(limit)
            elif query_type == "performance":
                if not symbols:
                    return "Error: 'symbols' parameter is required for performance queries. Please provide stock ticker symbols."
                return self._get_performance(symbols, limit)
            else:
                return f"Error: Unknown query_type '{query_type}'"
                
        except Exception as e:
            return f"Error fetching market data: {str(e)}"
    
    def _make_api_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make an API request to Marketaux and return JSON data.
        
        Args:
            endpoint: API endpoint path (e.g., '/news/all')
            params: Dictionary of query parameters for the API request
            
        Returns:
            JSON response data as a dictionary
            
        Raises:
            requests.HTTPError: If the HTTP request fails
        """
        params["api_token"] = self.api_key
        url = f"{self.base_url}{endpoint}"
        response: Response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def _get_news(
        self,
        symbols: str,
        sentiment_filter: Optional[str],
        language: str,
        limit: int,
        filter_entities: bool
    ) -> str:
        """Get financial news articles for specific stock symbols.
        
        Args:
            symbols: Comma-separated stock ticker symbols
            sentiment_filter: Filter by sentiment (positive/negative/neutral)
            language: Language code for articles
            limit: Number of articles to return
            filter_entities: Whether to filter entities in response
            
        Returns:
            Formatted news articles with sentiment analysis
        """
        params = {
            "symbols": symbols,
            "language": language,
            "limit": limit,
            "filter_entities": str(filter_entities).lower()
        }
        
        # Add sentiment filter if specified
        if sentiment_filter:
            if sentiment_filter == "positive":
                params["sentiment_gte"] = "0.1"
            elif sentiment_filter == "negative":
                params["sentiment_lte"] = "-0.1"
            elif sentiment_filter == "neutral":
                params["sentiment_gte"] = "0"
                params["sentiment_lte"] = "0"
        
        data = self._make_api_request("/news/all", params)
        
        if "error" in data:
            error_msg = data["error"].get("message", "Unknown error")
            return f"Error fetching news: {error_msg}"
        
        if "data" not in data or not data["data"]:
            return f"No news articles found for symbols: {symbols}"
        
        articles = data["data"]
        meta = data.get("meta", {})
        
        result = f"📰 Financial News for {symbols.upper()}\n"
        result += f"Found {meta.get('found', len(articles))} articles (showing {len(articles)})\n"
        result += "=" * 80 + "\n\n"
        
        for i, article in enumerate(articles, 1):
            result += f"{i}. {article.get('title', 'No title')}\n"
            result += f"   📅 Published: {article.get('published_at', 'N/A')}\n"
            result += f"   🔗 URL: {article.get('url', 'N/A')}\n"
            result += f"   📰 Source: {article.get('source', 'N/A')}\n"
            
            # Add entity sentiment information
            entities = article.get('entities', [])
            if entities:
                result += f"   📊 Entities mentioned:\n"
                for entity in entities[:3]:  # Show top 3 entities
                    symbol = entity.get('symbol', 'N/A')
                    name = entity.get('name', 'N/A')
                    sentiment = entity.get('sentiment_score', 0)
                    
                    # Format sentiment with emoji
                    if sentiment > 0.1:
                        sentiment_emoji = "📈 Positive"
                    elif sentiment < -0.1:
                        sentiment_emoji = "📉 Negative"
                    else:
                        sentiment_emoji = "➖ Neutral"
                    
                    result += f"      • {name} ({symbol}) - {sentiment_emoji} ({sentiment:.2f})\n"
            
            # Add snippet if available
            description = article.get('description', '')
            if description:
                snippet = description[:150] + "..." if len(description) > 150 else description
                result += f"   📝 {snippet}\n"
            
            result += "\n"
        
        return result
    
    def _search_entity(self, keywords: str, limit: int) -> str:
        """Search for entities/companies by name or keywords.
        
        Uses the news endpoint to find articles mentioning the keywords,
        then extracts entity information from those articles.
        
        Args:
            keywords: Search keywords (company name, etc.)
            limit: Number of results to return
            
        Returns:
            List of matching entities with their details
        """
        # Use the news endpoint with search parameter to find entities
        params = {
            "search": keywords,
            "limit": limit,
            "must_have_entities": "true"
        }
        
        data = self._make_api_request("/news/all", params)
        
        if "error" in data:
            error_msg = data["error"].get("message", "Unknown error")
            return f"Error searching entities: {error_msg}"
        
        if "data" not in data or not data["data"]:
            return f"No entities found for keywords: {keywords}"
        
        articles = data["data"]
        
        # Extract unique entities from articles
        entity_dict = {}
        for article in articles:
            entities = article.get('entities', [])
            for entity in entities:
                symbol = entity.get('symbol')
                if symbol and symbol not in entity_dict:
                    entity_dict[symbol] = entity
        
        if not entity_dict:
            return f"No entities found for keywords: {keywords}"
        
        result = f"🔍 Entity Search Results for '{keywords}'\n"
        result += f"Found {len(entity_dict)} unique entities in recent news\n"
        result += "=" * 80 + "\n\n"
        
        for i, (symbol, entity) in enumerate(list(entity_dict.items())[:limit], 1):
            result += f"{i}. {entity.get('name', 'N/A')}\n"
            result += f"   Symbol: {entity.get('symbol', 'N/A')}\n"
            result += f"   Type: {entity.get('type', 'N/A')}\n"
            result += f"   Industry: {entity.get('industry', 'N/A')}\n"
            result += f"   Country: {entity.get('country', 'N/A')}\n"
            
            if entity.get('exchange'):
                result += f"   Exchange: {entity.get('exchange')}\n"
            
            result += "\n"
        
        return result
    
    def _get_trending(self, limit: int) -> str:
        """Get currently trending entities in the market.
        
        Analyzes recent news articles to identify most mentioned entities.
        
        Args:
            limit: Number of trending entities to return
            
        Returns:
            List of trending entities with mention counts
        """
        # Get recent news with entities to analyze trending topics
        params = {
            "limit": 50,  # Fetch more articles to get better trending analysis
            "must_have_entities": "true",
            "language": "en"
        }
        
        data = self._make_api_request("/news/all", params)
        
        if "error" in data:
            error_msg = data["error"].get("message", "Unknown error")
            return f"Error fetching trending entities: {error_msg}"
        
        if "data" not in data or not data["data"]:
            return "No trending entities found at this time."
        
        articles = data["data"]
        
        # Count entity mentions and calculate average sentiment
        entity_stats = {}
        for article in articles:
            entities = article.get('entities', [])
            for entity in entities:
                symbol = entity.get('symbol')
                if not symbol:
                    continue
                
                if symbol not in entity_stats:
                    entity_stats[symbol] = {
                        'name': entity.get('name', 'N/A'),
                        'symbol': symbol,
                        'type': entity.get('type', 'N/A'),
                        'industry': entity.get('industry', 'N/A'),
                        'mentions': 0,
                        'sentiment_scores': []
                    }
                
                entity_stats[symbol]['mentions'] += 1
                sentiment = entity.get('sentiment_score', 0)
                if sentiment is not None:
                    entity_stats[symbol]['sentiment_scores'].append(sentiment)
        
        # Calculate average sentiment and sort by mentions
        trending_entities = []
        for symbol, stats in entity_stats.items():
            if stats['sentiment_scores']:
                avg_sentiment = sum(stats['sentiment_scores']) / len(stats['sentiment_scores'])
            else:
                avg_sentiment = 0
            
            trending_entities.append({
                'symbol': stats['symbol'],
                'name': stats['name'],
                'type': stats['type'],
                'industry': stats['industry'],
                'mentions': stats['mentions'],
                'sentiment_avg': avg_sentiment
            })
        
        # Sort by mentions (descending)
        trending_entities.sort(key=lambda x: x['mentions'], reverse=True)
        
        # Limit results
        trending_entities = trending_entities[:limit]
        
        if not trending_entities:
            return "No trending entities found at this time."
        
        result = "🔥 Trending Entities in the Market\n"
        result += f"Based on analysis of {len(articles)} recent articles\n"
        result += "=" * 80 + "\n\n"
        
        for i, entity in enumerate(trending_entities, 1):
            symbol = entity['symbol']
            name = entity['name']
            mentions = entity['mentions']
            sentiment_avg = entity['sentiment_avg']
            
            # Format sentiment
            if sentiment_avg > 0.1:
                sentiment_emoji = "📈 Positive"
            elif sentiment_avg < -0.1:
                sentiment_emoji = "📉 Negative"
            else:
                sentiment_emoji = "➖ Neutral"
            
            result += f"{i}. {name} ({symbol})\n"
            result += f"   💬 Mentions: {mentions}\n"
            result += f"   📊 Avg Sentiment: {sentiment_emoji} ({sentiment_avg:.2f})\n"
            
            if entity.get('industry') and entity['industry'] != 'N/A':
                result += f"   🏢 Industry: {entity['industry']}\n"
            
            result += "\n"
        
        return result
    
    def _get_performance(self, symbols: str, limit: int = 50) -> str:
        """Get market performance data for specific symbols.
        
        Analyzes recent news mentions and sentiment for specified symbols.
        
        Args:
            symbols: Comma-separated stock ticker symbols
            limit: Number of articles to analyze per symbol
            
        Returns:
            Market performance statistics and sentiment analysis
        """
        params = {
            "symbols": symbols,
            "limit": limit,  # Analyze more articles for better statistics
            "filter_entities": "true"
        }
        
        data = self._make_api_request("/news/all", params)
        
        if "error" in data:
            error_msg = data["error"].get("message", "Unknown error")
            return f"Error fetching performance data: {error_msg}"
        
        if "data" not in data or not data["data"]:
            return f"No performance data found for symbols: {symbols}"
        
        articles = data["data"]
        
        # Analyze sentiment per symbol
        symbol_stats = {}
        for article in articles:
            entities = article.get('entities', [])
            for entity in entities:
                symbol = entity.get('symbol')
                if not symbol:
                    continue
                
                if symbol not in symbol_stats:
                    symbol_stats[symbol] = {
                        'name': entity.get('name', 'N/A'),
                        'symbol': symbol,
                        'mentions': 0,
                        'positive': 0,
                        'negative': 0,
                        'neutral': 0,
                        'sentiment_scores': []
                    }
                
                symbol_stats[symbol]['mentions'] += 1
                sentiment = entity.get('sentiment_score', 0)
                
                if sentiment is not None:
                    symbol_stats[symbol]['sentiment_scores'].append(sentiment)
                    
                    if sentiment > 0.1:
                        symbol_stats[symbol]['positive'] += 1
                    elif sentiment < -0.1:
                        symbol_stats[symbol]['negative'] += 1
                    else:
                        symbol_stats[symbol]['neutral'] += 1
        
        if not symbol_stats:
            return f"No performance data found for symbols: {symbols}"
        
        result = f"📊 Market Performance for {symbols.upper()}\n"
        result += f"Based on analysis of {len(articles)} recent articles\n"
        result += "=" * 80 + "\n\n"
        
        for i, (symbol, stats) in enumerate(symbol_stats.items(), 1):
            name = stats['name']
            mentions = stats['mentions']
            
            # Calculate average sentiment
            if stats['sentiment_scores']:
                sentiment_avg = sum(stats['sentiment_scores']) / len(stats['sentiment_scores'])
            else:
                sentiment_avg = 0
            
            result += f"{i}. {name} ({symbol})\n"
            result += f"   📰 Total Mentions: {mentions}\n"
            result += f"   📊 Avg Sentiment: {sentiment_avg:.2f}\n"
            result += f"   📈 Positive Articles: {stats['positive']}\n"
            result += f"   📉 Negative Articles: {stats['negative']}\n"
            result += f"   ➖ Neutral Articles: {stats['neutral']}\n"
            
            result += "\n"
        
        return result



