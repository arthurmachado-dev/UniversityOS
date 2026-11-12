from flask import Blueprint, jsonify
from services.estatistica_service import EstatisticaService

# Criação do Blueprint da API de Estatísticas, Alertas e Dashboard
bp = Blueprint("api_estatisticas", __name__, url_prefix="/api")
service = EstatisticaService()

@bp.route("/dashboard", methods=["GET"])
def get_dashboard():
    """Retorna os dados consolidados para a página inicial (dashboard): métricas, alertas, tarefas recentes e eventos."""
    return jsonify(service.obter_dashboard())

@bp.route("/estatisticas", methods=["GET"])
def get_estatisticas():
    """Retorna estatísticas detalhadas com desempenho por disciplina, frequência acumulada e métricas de produtividade."""
    return jsonify(service.obter_estatisticas_completas())
