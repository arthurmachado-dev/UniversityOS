from typing import Dict, Any

class Horario:
    def __init__(self, dia_semana: str, horario_inicio: str, horario_fim: str,
                 disciplina_id: str, sala: str = "", bloco: str = "", id: str = ""):
        self.id = id
        self.dia_semana = dia_semana 
        self.horario_inicio = horario_inicio 
        self.horario_fim = horario_fim     
        self.disciplina_id = disciplina_id
        self.sala = sala
        self.bloco = bloco

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "dia_semana": self.dia_semana,
            "horario_inicio": self.horario_inicio,
            "horario_fim": self.horario_fim,
            "disciplina_id": self.disciplina_id,
            "sala": self.sala,
            "bloco": self.bloco
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Horario":
        return cls(
            id=str(data.get("id", "")),
            dia_semana=str(data.get("dia_semana", "")),
            horario_inicio=str(data.get("horario_inicio", "")),
            horario_fim=str(data.get("horario_fim", "")),
            disciplina_id=str(data.get("disciplina_id", "")),
            sala=str(data.get("sala", "")),
            bloco=str(data.get("bloco", ""))
        )
