from abc import ABC, abstractmethod
from typing import Dict, Any

class EntidadeAcademica(ABC):
    def __init__(self, id: str = ""):
        self.id = id

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EntidadeAcademica":
        pass

    @abstractmethod
    def get_identificador(self) -> str:
        pass
