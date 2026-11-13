import datetime
from typing import List, Dict, Any, Optional
from repositories.csv_repository import CSVRepository
from models.evento import Evento
from services.disciplina_service import DisciplinaService

class CalendarioService:
    """Serviço responsável pelas operações da agenda acadêmica e eventos do calendário."""
    def __init__(self, data_dir: str = "data"):
        self.evento_repo = CSVRepository(
            filename="eventos.json",
            fieldnames=["id", "titulo", "data", "hora", "local", "disciplina_id", "descricao", "tipo"],
            data_dir=data_dir
        )
        self.disciplina_service = DisciplinaService(data_dir=data_dir)

    def listar_eventos(self) -> List[Dict[str, Any]]:
        """Retorna todos os eventos acadêmicos ordenados cronologicamente por data e hora."""
        disciplinas_map = {d["id"]: d["nome"] for d in self.disciplina_service.listar_disciplinas()}
        rows = self.evento_repo.read_all()
        eventos = []
        for r in rows:
            ev = Evento.from_dict(r)
            ev_dict = ev.to_dict()
            ev_dict["disciplina_nome"] = disciplinas_map.get(ev.disciplina_id, "Geral")
            ev_dict["cor_badge"] = ev.get_cor_badge()
            eventos.append(ev_dict)

        # Ordena os eventos por data e hora em ordem crescente
        eventos.sort(key=lambda x: (x["data"], x["hora"]))
        return eventos

    def listar_proximos_eventos(self, limite: int = 5) -> List[Dict[str, Any]]:
        """Retorna os próximos compromissos a partir da data de hoje, limitados pela quantidade informada."""
        today_str = datetime.date.today().isoformat()
        all_e = self.listar_eventos()
        proximos = [e for e in all_e if e["data"] >= today_str]
        return proximos[:limite]

    def obter_evento(self, e_id: str) -> Optional[Dict[str, Any]]:
        """Busca um evento pelo identificador único com o nome da matéria associada."""
        row = self.evento_repo.find_by_id(e_id)
        if not row:
            return None
        ev = Evento.from_dict(row)
        ev_dict = ev.to_dict()
        disc = self.disciplina_service.obter_disciplina(ev.disciplina_id)
        ev_dict["disciplina_nome"] = disc["nome"] if disc else "Geral"
        ev_dict["cor_badge"] = ev.get_cor_badge()
        return ev_dict

    def criar_evento(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria e persiste um novo evento no calendário acadêmico."""
        evento = Evento.from_dict(data)
        saved = self.evento_repo.save(evento.to_dict())
        return self.obter_evento(saved["id"]) or saved

    def atualizar_evento(self, e_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza as informações de um evento acadêmico existente."""
        existing = self.evento_repo.find_by_id(e_id)
        if not existing:
            return None
        data["id"] = e_id
        evento = Evento.from_dict(data)
        saved = self.evento_repo.save(evento.to_dict())
        return self.obter_evento(saved["id"])

    def deletar_evento(self, e_id: str) -> bool:
        """Exclui um evento acadêmico."""
        return self.evento_repo.delete(e_id)
