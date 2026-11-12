from typing import Dict, Any

class Aluno:
    def __init__(self, nome: str, curso: str, periodo: str, id: str = ""):
        self.id = id
        self.nome = nome
        self.curso = curso
        self.periodo = periodo

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nome": self.nome,
            "curso": self.curso,
            "periodo": self.periodo
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Aluno":
        return cls(
            id=str(data.get("id", "")),
            nome=str(data.get("nome", "")),
            curso=str(data.get("curso", "")),
            periodo=str(data.get("periodo", ""))
        )
