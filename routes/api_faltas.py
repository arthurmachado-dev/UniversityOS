import datetime
from typing import List, Dict, Any, Optional
from repositories.json_repository import JSONRepository
from models.falta import Falta
from services.disciplina_service import DisciplinaService
from services.horario_service import HorarioService

class FaltaService:
    """
    Serviço responsável pelo controle de faltas e frequência acadêmica.
    Regra de Negócio:
    - Cada aula dura 100 minutos (1h 40min).
    - Carga horária total da disciplina em minutos = carga_horaria * 60.
    - Total de aulas no semestre = (carga_horaria * 60) / 100.
    - Limite máximo de faltas de 25% = (carga_horaria * 60 * 0.25) // 100 aulas.
    """
    def __init__(self, data_dir: str = "data"):
        self.falta_repo = JSONRepository(
            filename="faltas.json",
            fieldnames=["id", "disciplina_id", "data", "quantidade"],
            data_dir=data_dir
        )
        self.disciplina_service = DisciplinaService(data_dir=data_dir)
        self.horario_service = HorarioService(data_dir=data_dir)

    def listar_faltas(self) -> List[Dict[str, Any]]:
        """Retorna todos os registros individuais de falta."""
        rows = self.falta_repo.read_all()
        return [Falta.from_dict(r).to_dict() for r in rows]

    def listar_faltas_por_disciplina(self, disciplina_id: str) -> List[Dict[str, Any]]:
        """Retorna os registros de faltas de uma disciplina específica."""
        rows = self.falta_repo.filter_by("disciplina_id", disciplina_id)
        return [Falta.from_dict(r).to_dict() for r in rows]

    def obter_resumo_faltas_por_disciplina(self, disciplina_id: str) -> Dict[str, Any]:
        """Calcula o percentual de faltas utilizado com base em aulas de 100 minutos e o limite máximo de 25%."""
        disc = self.disciplina_service.obter_disciplina(disciplina_id)
        if not disc:
            return {
                "disciplina_id": disciplina_id,
                "disciplina_nome": "Desconhecida",
                "carga_horaria": 0,
                "total_aulas": 0,
                "duracao_aula_min": 100,
                "limite_faltas": 0,
                "faltas_atuais": 0,
                "faltas_restantes": 0,
                "minutos_faltas": 0,
                "minutos_limite": 0,
                "percentual_usado": 0.0,
                "percentual_limite_usado": 0.0,
                "status": "Seguro"
            }

        carga_horaria = int(disc.get("carga_horaria", 0) or 0)
        total_minutos = carga_horaria * 60
        total_aulas = int(round(total_minutos / 100)) if total_minutos > 0 else 0
        
        # Limite máximo de faltas em aulas de 100 min (25% dos minutos da carga horária)
        limite_aulas = int((total_minutos * 0.25) // 100) if total_minutos > 0 else 0

        faltas_records = self.listar_faltas_por_disciplina(disciplina_id)
        faltas_atuais = sum(int(f.get("quantidade", 1) or 1) for f in faltas_records)

        faltas_restantes = max(0, limite_aulas - faltas_atuais)
        minutos_faltas = faltas_atuais * 100
        minutos_limite = int(total_minutos * 0.25)

        # Percentual de faltas sobre a carga horária total da disciplina
        percentual_ch_usado = (minutos_faltas / total_minutos * 100.0) if total_minutos > 0 else 0.0
        # Percentual do limite de 25% consumido
        percentual_limite_consumido = (faltas_atuais / limite_aulas * 100.0) if limite_aulas > 0 else 0.0

        if faltas_atuais >= limite_aulas or percentual_ch_usado >= 25.0:
            status = "Perigo"
        elif percentual_limite_consumido >= 50.0 or faltas_restantes <= max(1, int(limite_aulas * 0.4)):
            status = "Atenção"
        else:
            status = "Seguro"

        return {
            "disciplina_id": disciplina_id,
            "disciplina_nome": disc.get("nome", ""),
            "carga_horaria": carga_horaria,
            "total_aulas": total_aulas,
            "duracao_aula_min": 100,
            "limite_faltas": limite_aulas,
            "faltas_atuais": faltas_atuais,
            "faltas_restantes": faltas_restantes,
            "minutos_faltas": minutos_faltas,
            "minutos_limite": minutos_limite,
            "percentual_usado": round(percentual_ch_usado, 1),
            "percentual_limite_usado": round(percentual_limite_consumido, 1),
            "status": status
        }

    def listar_resumo_todas_disciplinas(self) -> List[Dict[str, Any]]:
        """Gera o resumo de faltas e limites para todas as disciplinas cadastradas."""
        disciplinas = self.disciplina_service.listar_disciplinas()
        resumos = []
        for disc in disciplinas:
            res = self.obter_resumo_faltas_por_disciplina(disc["id"])
            resumos.append(res)
        return resumos

    def registrar_falta(self, disciplina_id: str, quantidade: int = 1, data: str = "") -> Dict[str, Any]:
        """Registra a ausência em uma disciplina (cada unidade = 1 aula de 100 minutos) e grava no JSON."""
        if not data:
            data = datetime.date.today().isoformat()
        falta = Falta(disciplina_id=disciplina_id, quantidade=quantidade, data=data)
        saved = self.falta_repo.save(falta.to_dict())
        return saved

    def decrementar_falta(self, disciplina_id: str, quantidade: int = 1) -> bool:
        """
        Remove/diminui faltas da disciplina indicada.
        Remove o registro de falta mais recente ou subtrai da quantidade.
        """
        records = self.listar_faltas_por_disciplina(disciplina_id)
        if not records:
            return False

        # Pega o registro mais recente
        ultimo = records[-1]
        qtd_atual = int(ultimo.get("quantidade", 1) or 1)

        if qtd_atual > quantidade:
            ultimo["quantidade"] = qtd_atual - quantidade
            self.falta_repo.update(ultimo["id"], ultimo)
            return True
        else:
            # Deleta o registro completo
            self.falta_repo.delete(ultimo["id"])
            qtd_restante = quantidade - qtd_atual
            if qtd_restante > 0 and len(records) > 1:
                return self.decrementar_falta(disciplina_id, quantidade=qtd_restante)
            return True

    def registrar_faltas_hoje(self, disciplina_ids: List[str]) -> List[Dict[str, Any]]:
        """Registra ausências em lote para múltiplas disciplinas no dia atual."""
        today_str = datetime.date.today().isoformat()
        registradas = []
        for d_id in disciplina_ids:
            if d_id:
                res = self.registrar_falta(disciplina_id=d_id, quantidade=1, data=today_str)
                registradas.append(res)
        return registradas

    def deletar_falta(self, falta_id: str) -> bool:
        """Exclui um registro de falta existente."""
        return self.falta_repo.delete(falta_id)
