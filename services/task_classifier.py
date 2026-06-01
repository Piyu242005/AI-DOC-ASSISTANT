"""
task_classifier.py – Keyword-based task classifier for intelligent provider routing.
Analyses the user prompt and returns the best provider for that task type.
"""
from typing import Tuple

# Task routing rules: each entry maps task keywords → provider + reason
ROUTING_RULES = [
    {
        "task_type": "coding",
        "provider": "Groq",
        "reason": "Groq (LLaMA) excels at fast code generation and debugging",
        "keywords": [
            "code", "function", "bug", "debug", "error", "implement",
            "programming", "script", "algorithm", "class", "method",
            "python", "javascript", "typescript", "java", "sql", "html",
            "css", "api", "variable", "loop", "syntax", "compile", "runtime",
            "exception", "library", "module", "import", "refactor",
        ],
    },
    {
        "task_type": "reasoning",
        "provider": "OpenRouter",
        "reason": "OpenRouter provides powerful models optimised for deep reasoning",
        "keywords": [
            "analyze", "analysis", "compare", "reasoning", "evaluate",
            "critique", "argue", "hypothesis", "conclusion", "implication",
            "strategic", "investigate", "detailed explanation", "pros and cons",
            "trade-off", "why does", "what causes", "explain in depth",
        ],
    },
    {
        "task_type": "experimentation",
        "provider": "Hugging Face",
        "reason": "Hugging Face is ideal for open-source model experimentation",
        "keywords": [
            "open-source", "open source", "research paper", "neural",
            "transformer", "fine-tune", "embedding", "tokenizer", "train",
            "dataset", "model card", "benchmark", "arxiv",
        ],
    },
]

# Default fallback
DEFAULT_RULE = {
    "task_type": "general",
    "provider": "Gemini",
    "reason": "Gemini is optimised for general document Q&A and summarisation",
}


def classify_task(prompt: str) -> Tuple[str, str, str]:
    """
    Classify the prompt and return (task_type, recommended_provider, reason).
    Checks routing rules in priority order; falls back to Gemini for general tasks.
    """
    prompt_lower = prompt.lower()
    for rule in ROUTING_RULES:
        for kw in rule["keywords"]:
            if kw in prompt_lower:
                return rule["task_type"], rule["provider"], rule["reason"]
    return DEFAULT_RULE["task_type"], DEFAULT_RULE["provider"], DEFAULT_RULE["reason"]
