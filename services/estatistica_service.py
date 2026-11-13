from typing import Dict, Any, List
from services.disciplina_service import DisciplinaService
from services.falta_service import FaltaService
from services.nota_service import NotaService
from services.tarefa_service import TarefaService
from services.calendario_service import CalendarioService

class EstatisticaService:
    """Serviço analítico responsável por agregar métricas globais, calcular médias e gerar alertas inteligentes."""
    def __init__(self, data_dir: str = "data"):
        self.disciplina_service = DisciplinaService(data_dir=data_dir)
        self.falta_service = FaltaService(data_dir=data_dir)
        self.nota_service = NotaService(data_dir=data_dir)
        self.tarefa_service = TarefaService(data_dir)
        self.calendario_service = CalendarioService(data_dir=data_dir)

    def obter_dashboard(self) -> Dict[str, Any]:
        """Gera a visão consolidada para o Dashboard principal com métricas, tarefas recentes, próximos eventos e alertas de atenção."""
        disciplinas = self.disciplina_service.listar_disciplinas()
        resumo_faltas = self.falta_service.listar_resumo_todas_disciplinas()
        tarefas = self.tarefa_service.listar()
        proximos_eventos = self.calendario_service.listar_proximos_eventos(limite=5)
        media_geral = self.nota_service.calcular_media_geral()

        tarefas_pendentes = [t for t in tarefas if t.get("status") in ["Pendente", "Em andamento", "Atrasada"]]
        avaliacoes_proximas = [e for e in proximos_eventos if e.get("tipo") in ["Prova", "Trabalho", "Entrega"]]

        # Constrói os alertas de itens que exigem atenção imediata do estudante
        alertas = []

        # Tarefas urgentes ou em atraso
        for t in tarefas_pendentes:
            if t.get("status") == "Atrasada":
                alertas.append({
                    "tipo": "tarefa_atrasada",
                    "titulo": t.get("titulo"),
                    "mensagem": "Tarefa atrasada!",
                    "nivel": "error"
                })
            elif t.get("prioridade") in ["Alta", "Urgente"]:
                alertas.append({
                    "tipo": "tarefa_urgente",
                    "titulo": t.get("titulo"),
                    "mensagem": f"Prazo: {t.get('data_prazo', 'Sem data')}",
                    "nivel": "error" if t.get("prioridade") == "Urgente" else "warning"
                })

        # Disciplinas próximas do limite máximo de 25% de faltas
        for f in resumo_faltas:
            if f.get("status") in ["Atenção", "Perigo"]:
                alertas.append({
                    "tipo": "falta_limite",
                    "titulo": f.get("disciplina_nome"),
                    "mensagem": f"Restam {f.get('faltas_restantes')} faltas até o limite",
                    "nivel": "error" if f.get("status") == "Perigo" else "warning"
                })

        # Próximas provas e avaliações agendadas
        for ev in avaliacoes_proximas:
            alertas.append({
                "tipo": "avaliacao_proxima",
                "titulo": f"{ev.get('tipo')}: {ev.get('titulo')}",
                "mensagem": f"Data: {ev.get('data')} às {ev.get('hora', 'Horário N/I')}",
                "nivel": "info"
            })

        return {
            "total_disciplinas": len(disciplinas),
            "total_tarefas_pendentes": len(tarefas_pendentes),
            "total_avaliacoes_proximas": len(avaliacoes_proximas),
            "media_geral": media_geral,
            "alertas": alertas[:6],
            "tarefas_recentes": tarefas_pendentes[:5],
            "proximos_eventos": proximos_eventos
        }

    def obter_estatisticas_completas(self) -> Dict[str, Any]:
        """Gera o relatório analítico completo com desempenho individual por matéria, frequência e taxa de conclusão de tarefas."""
        disciplinas = self.disciplina_service.listar_disciplinas()
        resumo_faltas = self.falta_service.listar_resumo_todas_disciplinas()
        tarefas = self.tarefa_service.listar()
        media_geral = self.nota_service.calcular_media_geral()

        desempenho_disciplinas = []
        for d in disciplinas:
            m = self.nota_service.calcular_media_disciplina(d["id"])
            desempenho_disciplinas.append({
                "disciplina_id": d["id"],
                "disciplina_nome": d["nome"],
                "media": m
            })

        concluidas = len([t for t in tarefas if t.get("status") == "Concluída"])
        pendentes = len([t for t in tarefas if t.get("status") in ["Pendente", "Em andamento"]])
        atrasadas = len([t for t in tarefas if t.get("status") == "Atrasada"])

        return {
            "media_geral": media_geral,
            "desempenho_disciplinas": desempenho_disciplinas,
            "frequencia_disciplinas": resumo_faltas,
            "tarefas_metricas": {
                "concluidas": concluidas,
                "pendentes": pendentes,
                "atrasadas": atrasadas,
                "total": len(tarefas)
            }
        }
