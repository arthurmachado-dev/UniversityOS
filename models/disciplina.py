from typing import Dict, Any

DURACAO_AULA_MINUTOS = 100

class Disciplina:
    def __init__(self, nome: str, carga_horaria: int, codigo: str = "", professor_id: str = "",
                 turma: str = "", semestre: str = "", descricao: str = "", id: str = ""):
        self.id = id
        self.nome = nome
        self.codigo = codigo
        self.professor_id = professor_id
        self.turma = turma
        self.carga_horaria = int(carga_horaria) if carga_horaria else 0
        self.semestre = semestre
        self.descricao = descricao

    @property
    def total_minutos(self) -> int:
        """Carga horária total convertida em minutos."""
        return self.carga_horaria * 60

    @property
    def total_aulas(self) -> int:
        """Total de aulas de 100 minutos no semestre."""
        if self.carga_horaria <= 0:
            return 0
        return int(round((self.carga_horaria * 60) / DURACAO_AULA_MINUTOS))

    @property
    def limite_faltas_aulas(self) -> int:
        if self.total_minutos <= 0:
            return 0
        limite_minutos = self.total_minutos * 0.25
        return int(limite_minutos // DURACAO_AULA_MINUTOS)

    @property
    def limite_faltas(self) -> float:
        return float(self.limite_faltas_aulas)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nome": self.nome,
            "codigo": self.codigo,
            "professor_id": self.professor_id,
            "turma": self.turma,
            "carga_horaria": self.carga_horaria,
            "semestre": self.semestre,
            "descricao": self.descricao,
            "total_aulas": self.total_aulas,
            "duracao_aula_min": DURACAO_AULA_MINUTOS,
            "limite_faltas": self.limite_faltas_aulas,
            "limite_faltas_aulas": self.limite_faltas_aulas
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Disciplina":
        carga = data.get("carga_horaria", 0)
        try:
            carga = int(carga)
        except (ValueError, TypeError):
            carga = 0

        return cls(
            id=str(data.get("id", "")),
            nome=str(data.get("nome", "")),
            codigo=str(data.get("codigo", "")),
            professor_id=str(data.get("professor_id", "")),
            turma=str(data.get("turma", "")),
            carga_horaria=carga,
            semestre=str(data.get("semestre", "")),
            descricao=str(data.get("descricao", ""))
        )
