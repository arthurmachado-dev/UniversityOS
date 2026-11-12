from typing import Dict, Any
import datetime

class Falta:
    def __init__(self, disciplina_id: str, data: str = "", quantidade: int = 1, id: str = ""):
        self.id = id
        self.disciplina_id = disciplina_id
        self.data = data or datetime.date.today().isoformat()
        self.quantidade = int(quantidade) if quantidade else 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "disciplina_id": self.disciplina_id,
            "data": self.data,
            "quantidade": self.quantidade
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Falta":
        qty = data.get("quantidade", 1)
        try:
            qty = int(qty)
        except (ValueError, TypeError):
            qty = 1

        return cls(
            id=str(data.get("id", "")),
            disciplina_id=str(data.get("disciplina_id", "")),
            data=str(data.get("data", "")),
            quantidade=qty
        )
