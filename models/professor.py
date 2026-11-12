from typing import Dict, Any

class Professor:
    def __init__(self, nome: str, email: str = "", departamento: str = "", id: str = ""):
        self.id = id
        self.nome = nome
        self.email = email
        self.departamento = departamento

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "departamento": self.departamento
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Professor":
        return cls(
            id=str(data.get("id", "")),
            nome=str(data.get("nome", "")),
            email=str(data.get("email", "")),
            departamento=str(data.get("departamento", ""))
        )
