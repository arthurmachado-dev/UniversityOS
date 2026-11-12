from typing import Dict, Any

class Nota:
    def __init__(self, disciplina_id: str, nome_avaliacao: str, nota: float, peso: float = 1.0, id: str = ""):
        self.id = id
        self.disciplina_id = disciplina_id
        self.nome_avaliacao = nome_avaliacao
        self.nota = float(nota) if nota is not None else 0.0
        self.peso = float(peso) if peso is not None else 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "disciplina_id": self.disciplina_id,
            "nome_avaliacao": self.nome_avaliacao,
            "nota": self.nota,
            "peso": self.peso
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Nota":
        try:
            val_nota = float(data.get("nota", 0.0))
        except (ValueError, TypeError):
            val_nota = 0.0

        try:
            val_peso = float(data.get("peso", 1.0))
        except (ValueError, TypeError):
            val_peso = 1.0

        return cls(
            id=str(data.get("id", "")),
            disciplina_id=str(data.get("disciplina_id", "")),
            nome_avaliacao=str(data.get("nome_avaliacao", "")),
            nota=val_nota,
            peso=val_peso
        )
