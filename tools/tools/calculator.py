"""Calculator tool for mathematical operations."""

from pydantic import BaseModel, Field
from typing import Type
from intelligentAgent.tools.base import BaseTool


class CalculatorInput(BaseModel):
    """Input schema for calculator tool."""
    
    expression: str = Field(
        ...,
        description="Mathematical expression to evaluate (e.g., '2 + 2', '10 * 5 + 3', 'sqrt(16)')"
    )


class CalculatorTool(BaseTool):
    """Tool for performing mathematical calculations.
    
    Supports basic arithmetic operations and common mathematical functions.
    Uses Python's eval() with a restricted namespace for safety.
    """
    
    name: str = "calculator"
    description: str = "Perform mathematical calculations. Supports basic arithmetic (+, -, *, /), exponents (**), and functions like sqrt, sin, cos, etc."
    args_schema: Type[BaseModel] = CalculatorInput
    
    def execute(self, expression: str) -> str:
        """Execute a mathematical calculation.
        
        Args:
            expression: Mathematical expression to evaluate
            
        Returns:
            String result of the calculation
        """
        import math
        
        # Safe namespace with only math functions
        safe_dict = {
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            "pow": pow,
            # Math module functions
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "pi": math.pi,
            "e": math.e,
            "log": math.log,
            "log10": math.log10,
            "exp": math.exp,
            "floor": math.floor,
            "ceil": math.ceil,
        }
        
        try:
            # Evaluate expression with restricted namespace
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            return f"Result: {result}"
        
        except ZeroDivisionError:
            return "Error: Division by zero"
        
        except Exception as e:
            return f"Error evaluating expression: {str(e)}"

