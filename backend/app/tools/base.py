from typing import Callable, Any, Dict, Optional
from pydantic import BaseModel, Field


class ToolDefinition(BaseModel):
    name: str = Field(..., description="Unique tool identifier")
    description: str = Field(..., description="Description of tool functionality and when LLM should invoke it")
    parameters_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema of arguments")


class BaseTravelTool:
    """Base tool wrapper providing schema definition and async execution."""

    def __init__(self, name: str, description: str, func: Callable, schema: Dict[str, Any]):
        self.name = name
        self.description = description
        self.func = func
        self.schema = schema

    async def execute(self, **kwargs) -> Any:
        return await self.func(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.schema,
            }
        }
