import ast
import operator
from abc import ABC, abstractmethod
from typing import Dict

from duckduckgo_search import DDGS

from services.rag_engine import RAGManager


class BaseTool(ABC):
    name: str
    description: str

    @abstractmethod
    def run(self, action_input: str) -> str:
        pass


class CalculatorTool(BaseTool):
    name = "Calculator"
    description = "Evaluates mathematical expressions. Input should be a valid mathematical string."

    def run(self, action_input: str) -> str:
        try:
            # Secure math evaluation using ast
            allowed_operators = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
                ast.USub: operator.neg,
            }

            def eval_expr(node):
                if isinstance(node, ast.Num):
                    return node.n
                elif isinstance(node, ast.Constant) and isinstance(
                    node.value, (int, float)
                ):
                    # For newer python versions
                    return node.value
                elif isinstance(node, ast.BinOp):
                    return allowed_operators[type(node.op)](
                        eval_expr(node.left), eval_expr(node.right)
                    )
                elif isinstance(node, ast.UnaryOp):
                    return allowed_operators[type(node.op)](eval_expr(node.operand))
                else:
                    raise TypeError(f"Unsupported node type: {type(node)}")

            parsed = ast.parse(action_input, mode="eval").body
            result = eval_expr(parsed)
            return str(result)
        except Exception as e:
            return f"Error computing expression: {e}"


class WebSearchTool(BaseTool):
    name = "Web Search"
    description = (
        "Searches the web for up-to-date information. Input should be a search query."
    )

    def __init__(self):
        import os

        self.tavily_api_key = os.getenv("TAVILY_API_KEY")

    def run(self, action_input: str) -> str:
        # 1. Try Tavily (Primary Search)
        if self.tavily_api_key and self.tavily_api_key != "your_tavily_api_key_here":
            try:
                from tavily import TavilyClient

                client = TavilyClient(api_key=self.tavily_api_key)
                response = client.search(
                    action_input, search_depth="advanced", max_results=3
                )
                results = response.get("results", [])
                if results:
                    formatted = "\n".join(
                        [f"- {r['title']}: {r['content']}" for r in results]
                    )
                    return formatted
            except Exception:
                pass  # Fallback to DDGS on failure

        # 2. Try DuckDuckGo (Fallback Search)
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(action_input, max_results=3))
            if not results:
                return "No results found."
            formatted = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
            return formatted
        except Exception as e:
            return f"Web search failed: {e}"


class DocumentSearchTool(BaseTool):
    name = "Document Search"
    description = "Searches the uploaded PDF document for context. Input should be a search query."

    def __init__(self, rag_manager: RAGManager):
        self.rag_manager = rag_manager

    def run(self, action_input: str) -> str:
        try:
            context, score, time_taken, chunks = self.rag_manager.retrieve_context(
                action_input
            )
            if not context or "No document indexed" in context:
                return "No relevant context found or document not uploaded."
            return context
        except Exception as e:
            return f"Document search failed: {e}"


class ToolRegistry:
    def __init__(self, rag_manager: RAGManager):
        self.tools: Dict[str, BaseTool] = {
            "Calculator": CalculatorTool(),
            "Web Search": WebSearchTool(),
            "Document Search": DocumentSearchTool(rag_manager),
        }

    def get_tool(self, name: str) -> BaseTool:
        return self.tools.get(name)

    def get_descriptions(self) -> str:
        return "\n".join(
            [f"- {name}: {t.description}" for name, t in self.tools.items()]
        )
