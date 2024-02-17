# Code module for the initial generator which creates the initial attempt
from langchain.schema import ChatMessage
from src.llm import LLM


class InitialGenerator:
    def __init__(self, model: str, strategy: str):
        self.strategy = strategy
        self.llm = LLM(
            model=model, config={"temperature": 0, "max_retries": 10}
        ).llm

    def generate(self, problem: str) -> str:
        if self.strategy == "zero-shot":
            return self.llm.invoke(
                [ChatMessage(content=problem, role="assistant")]
            )
        elif self.strategy == "plan-and-solve":
            return self._empty(problem)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
