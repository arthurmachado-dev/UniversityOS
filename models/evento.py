from typing import Dict, Any

class Evento:
    def __init__(self, titulo: str, data: str, hora: str = "", local: str = "",
                 disciplina_id: str = "", descricao: str = "", tipo: str = "Evento", id: str = ""):
        self.id = id
        self.titulo = titulo
        self.data = data
        self.hora = hora
        self.local = local
        self.disciplina_id = disciplina_id
        self.descricao = descricao
        self.tipo = tipo

    def get_cor_badge(self) -> str:
        return "primary"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "data": self.data,
            "hora": self.hora,
            "local": self.local,
            "disciplina_id": self.disciplina_id,
            "descricao": self.descricao,
            "tipo": self.tipo
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Evento":
        tipo = str(data.get("tipo", "Evento"))
        args = {
            "id": str(data.get("id", "")),
            "titulo": str(data.get("titulo", "")),
            "data": str(data.get("data", "")),
            "hora": str(data.get("hora", "")),
            "local": str(data.get("local", "")),
            "disciplina_id": str(data.get("disciplina_id", "")),
            "descricao": str(data.get("descricao", "")),
            "tipo": tipo
        }
        
        if tipo == "Prova":
            return Prova(**args)
        elif tipo == "Trabalho":
            return Trabalho(**args)
        elif tipo == "Aula":
            return Aula(**args)
        elif tipo == "Seminário":
            return Seminario(**args)
        elif tipo == "Entrega":
            return Entrega(**args)
        return cls(**args)


class Prova(Evento):
    def __init__(self, **kwargs):
        kwargs["tipo"] = "Prova"
        super().__init__(**kwargs)

    def get_cor_badge(self) -> str:
        return "error"


class Trabalho(Evento):
    def __init__(self, **kwargs):
        kwargs["tipo"] = "Trabalho"
        super().__init__(**kwargs)

    def get_cor_badge(self) -> str:
        return "tertiary"


class Aula(Evento):
    def __init__(self, **kwargs):
        kwargs["tipo"] = "Aula"
        super().__init__(**kwargs)

    def get_cor_badge(self) -> str:
        return "primary"


class Seminario(Evento):
    def __init__(self, **kwargs):
        kwargs["tipo"] = "Seminário"
        super().__init__(**kwargs)

    def get_cor_badge(self) -> str:
        return "secondary"


class Entrega(Evento):
    def __init__(self, **kwargs):
        kwargs["tipo"] = "Entrega"
        super().__init__(**kwargs)

    def get_cor_badge(self) -> str:
        return "warning"
