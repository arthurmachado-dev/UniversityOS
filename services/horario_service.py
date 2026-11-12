import datetime
from typing import List, Dict, Any, Optional
from repositories.json_repository import JSONRepository
from models.horario import Horario
from services.disciplina_service import DisciplinaService

DIAS_SEMANA_MAP = {
    0: "Segunda",
    1: "Terça",
    2: "Quarta",
    3: "Quinta",
    4: "Sexta",
    5: "Sábado",
    6: "Domingo"
}

class HorarioService:
    """Serviço responsável pelo gerenciamento da grade de horários de aulas semanais."""
    def __init__(self, data_dir: str = "data"):
        self.horario_repo = JSONRepository(
            filename="horarios.json",
            fieldnames=["id", "dia_semana", "horario_inicio", "horario_fim", "disciplina_id", "sala", "bloco"],
            data_dir=data_dir
        )
        self.disciplina_service = DisciplinaService(data_dir=data_dir)

    def listar_horarios(self) -> List[Dict[str, Any]]:
        """Retorna todos os horários cadastrados com os nomes das disciplinas e professores correspondentes."""
        disciplinas_map = {d["id"]: d for d in self.disciplina_service.listar_disciplinas()}
        rows = self.horario_repo.read_all()
        horarios = []
        for r in rows:
            h = Horario.from_dict(r)
            h_dict = h.to_dict()
            disc = disciplinas_map.get(h.disciplina_id, {})
            h_dict["disciplina_nome"] = disc.get("nome", "Disciplina Desconhecida")
            h_dict["professor_nome"] = disc.get("professor_nome", "Prof. Não Informado")
            horarios.append(h_dict)
        return horarios

    def listar_horarios_por_dia(self, dia: str) -> List[Dict[str, Any]]:
        """Retorna os horários filtrados por um dia específico da semana."""
        all_h = self.listar_horarios()
        return [h for h in all_h if h["dia_semana"].lower() == dia.lower()]

    def obter_horarios_hoje(self) -> List[Dict[str, Any]]:
        """Retorna os horários de aula agendados para o dia atual com base no calendário do sistema."""
        today_idx = datetime.date.today().weekday()
        dia_nome = DIAS_SEMANA_MAP.get(today_idx, "Segunda")
        return self.listar_horarios_por_dia(dia_nome)

    def obter_horario(self, h_id: str) -> Optional[Dict[str, Any]]:
        """Busca um horário pelo seu ID."""
        row = self.horario_repo.find_by_id(h_id)
        if not row:
            return None
        h = Horario.from_dict(row)
        h_dict = h.to_dict()
        disc = self.disciplina_service.obter_disciplina(h.disciplina_id)
        h_dict["disciplina_nome"] = disc["nome"] if disc else "Disciplina Desconhecida"
        h_dict["professor_nome"] = disc.get("professor_nome", "") if disc else ""
        return h_dict

    def criar_horario(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cadastra um novo horário de aula na grade semanal."""
        horario = Horario.from_dict(data)
        saved = self.horario_repo.save(horario.to_dict())
        return self.obter_horario(saved["id"]) or saved

    def atualizar_horario(self, h_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza um horário de aula existente."""
        existing = self.horario_repo.find_by_id(h_id)
        if not existing:
            return None
        data["id"] = h_id
        horario = Horario.from_dict(data)
        saved = self.horario_repo.save(horario.to_dict())
        return self.obter_horario(saved["id"])

    def deletar_horario(self, h_id: str) -> bool:
        """Exclui um horário da grade."""
        return self.horario_repo.delete(h_id)
