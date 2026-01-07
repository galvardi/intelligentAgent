"""DateTime tool for getting current date and time information."""

from pydantic import BaseModel, Field
from typing import Type, Literal
from datetime import datetime, timezone
from intelligentAgent.tools.base import BaseTool


class DateTimeInput(BaseModel):
    """Input schema for datetime tool."""
    
    format_type: Literal["datetime", "date", "time", "timestamp", "iso"] = Field(
        default="datetime",
        description="Type of datetime format to return: 'datetime' (full), 'date' (date only), 'time' (time only), 'timestamp' (unix timestamp), 'iso' (ISO 8601 format)"
    )
    
    timezone_info: bool = Field(
        default=True,
        description="Whether to include timezone information (UTC)"
    )


class DateTimeTool(BaseTool):
    """Tool for getting current date and time information.
    
    Returns current date/time in various formats.
    """
    
    name: str = "get_datetime"
    description: str = "Get the current date and time in various formats. Useful for answering questions about what time or date it is."
    args_schema: Type[BaseModel] = DateTimeInput
    
    def execute(self, format_type: str = "datetime", timezone_info: bool = True) -> str:
        """Get current datetime in specified format.
        
        Args:
            format_type: Type of format to return
            timezone_info: Whether to include timezone info
            
        Returns:
            Formatted datetime string
        """
        # Get current time
        now = datetime.now(timezone.utc) if timezone_info else datetime.now()
        
        try:
            if format_type == "datetime":
                result = now.strftime("%Y-%m-%d %H:%M:%S")
                if timezone_info:
                    result += " UTC"
                return f"Current datetime: {result}"
            
            elif format_type == "date":
                result = now.strftime("%Y-%m-%d")
                return f"Current date: {result}"
            
            elif format_type == "time":
                result = now.strftime("%H:%M:%S")
                if timezone_info:
                    result += " UTC"
                return f"Current time: {result}"
            
            elif format_type == "timestamp":
                result = int(now.timestamp())
                return f"Current Unix timestamp: {result}"
            
            elif format_type == "iso":
                result = now.isoformat()
                return f"Current datetime (ISO 8601): {result}"
            
            else:
                return f"Unknown format type: {format_type}"
        
        except Exception as e:
            return f"Error getting datetime: {str(e)}"

