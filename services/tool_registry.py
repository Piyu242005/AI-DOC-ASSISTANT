import ast
import operator
from abc import ABC, abstractmethod
from typing import Dict

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


class TavilySearchTool:
    @staticmethod
    def search(query: str, api_key: str):
        import time

        from tavily import TavilyClient

        start_time = time.time()
        client = TavilyClient(api_key=api_key)
        response = client.search(query, search_depth="advanced", max_results=5)
        results = response.get("results", [])
        search_time = time.time() - start_time

        formatted_results = []
        for r in results:
            formatted_results.append(
                {
                    "title": r.get("title", "No Title"),
                    "url": r.get("url", ""),
                    "snippet": r.get("content", r.get("snippet", "")),
                }
            )
        return formatted_results, search_time


class DuckDuckGoSearchTool:
    @staticmethod
    def search(query: str):
        import time

        from duckduckgo_search import DDGS

        start_time = time.time()
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        search_time = time.time() - start_time

        formatted_results = []
        for r in results:
            formatted_results.append(
                {
                    "title": r.get("title", "No Title"),
                    "url": r.get("href", r.get("url", "")),
                    "snippet": r.get("body", r.get("snippet", "")),
                }
            )
        return formatted_results, search_time


class MultiSearchTool(BaseTool):
    name = "Web Search"
    description = (
        "Searches the web for up-to-date information. Input should be a search query."
    )

    def run(self, action_input: str) -> str:
        import os
        import time

        import streamlit as st

        from services.db_manager import DBManager

        db = DBManager()
        provider = st.session_state.get("search_provider", "Auto")
        tavily_api_key = os.getenv("TAVILY_API_KEY") or st.secrets.get(
            "TAVILY_API_KEY", ""
        )

        def update_status(msg):
            if (
                "status_callback" in st.session_state
                and st.session_state.status_callback
            ):
                try:
                    st.session_state.status_callback(msg)
                except Exception:
                    pass

        results = []
        search_time = 0.0
        provider_used = ""
        fallback_used = False

        use_tavily = (provider == "Tavily") or (provider == "Auto" and tavily_api_key)
        use_ddg = (provider == "DuckDuckGo") or (
            provider == "Auto" and not tavily_api_key
        )

        if use_tavily:
            try:
                update_status("🔍 Searching Web via Tavily...")
                results, search_time = TavilySearchTool.search(
                    action_input, tavily_api_key
                )
                provider_used = "Tavily"
            except Exception as e:
                if provider == "Auto":
                    update_status("⚠️ Tavily unavailable. Switching to DuckDuckGo...")
                    fallback_used = True
                    try:
                        results, search_time = DuckDuckGoSearchTool.search(action_input)
                        provider_used = "DuckDuckGo"
                    except Exception as ex:
                        return (
                            f"Web search failed: Tavily failed ({e}) "
                            f"and DuckDuckGo fallback failed ({ex})"
                        )
                else:
                    return f"Tavily search failed: {e}"
        elif use_ddg:
            try:
                update_status("🔍 Searching Web via DuckDuckGo...")
                results, search_time = DuckDuckGoSearchTool.search(action_input)
                provider_used = "DuckDuckGo"
            except Exception as e:
                return f"DuckDuckGo search failed: {e}"

        db.log_search(
            query=action_input,
            provider_used=provider_used,
            fallback_used=fallback_used,
            search_time=search_time,
            results_count=len(results),
        )

        st.session_state.last_search_telemetry = {
            "provider_used": provider_used,
            "fallback_used": fallback_used,
            "search_time": search_time,
            "results_count": len(results),
        }

        if not results:
            return "No web search results found."

        formatted = []
        for idx, r in enumerate(results, 1):
            formatted.append(
                f"Source {idx}: [{r['title']}]({r['url']})\nSnippet: {r['snippet']}"
            )

        return "\n\n---\n\n".join(formatted) + f"\n\nSource: {provider_used}"


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
            "Web Search": MultiSearchTool(),
            "Document Search": DocumentSearchTool(rag_manager),
        }

    def get_tool(self, name: str) -> BaseTool:
        return self.tools.get(name)

    def get_descriptions(self) -> str:
        return "\n".join(
            [f"- {name}: {t.description}" for name, t in self.tools.items()]
        )
