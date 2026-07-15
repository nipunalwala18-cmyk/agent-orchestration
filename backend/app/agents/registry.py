"""Registry for resolving agents by stable names."""

from typing import Dict, Iterable

from app.agents.base import BaseAgent


class AgentRegistry:
    """In-process agent registry suitable for dependency injection."""

    def __init__(self) -> None:
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> BaseAgent:
        if agent.name in self._agents:
            raise ValueError(f"Agent '{agent.name}' is already registered.")
        self._agents[agent.name] = agent
        return agent

    def get(self, name: str) -> BaseAgent:
        try:
            return self._agents[name]
        except KeyError as exc:
            raise KeyError(f"Agent '{name}' is not registered.") from exc

    def names(self) -> Iterable[str]:
        return tuple(self._agents)
