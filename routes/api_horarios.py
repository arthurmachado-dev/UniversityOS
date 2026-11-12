from flask import Blueprint, jsonify, request
from services.horario_service import HorarioService

# Criação do Blueprint da API do Quadro de Horários Semanais
bp = Blueprint("api_horarios", __name__, url_prefix="/api")
service = HorarioService()

@bp.route("/horarios", methods=["GET"])
def get_horarios():
    """Retorna os horários de aula cadastrados, com opção de filtro por dia da semana."""
    dia = request.args.get("dia")
    if dia:
        return jsonify(service.listar_horarios_por_dia(dia))
    return jsonify(service.listar_horarios())

@bp.route("/horarios/hoje", methods=["GET"])
def get_horarios_hoje():
    """Retorna as aulas agendadas especificamente para o dia de hoje."""
    return jsonify(service.obter_horarios_hoje())

@bp.route("/horarios", methods=["POST"])
def create_horario():
    """Cadastra um novo horário de aula na grade semanal."""
    data = request.get_json() or {}
    if not data.get("disciplina_id") or not data.get("dia_semana"):
        return jsonify({"error": "Os campos 'disciplina_id' e 'dia_semana' são obrigatórios"}), 400
    created = service.criar_horario(data)
    return jsonify(created), 201

@bp.route("/horarios/<h_id>", methods=["PUT"])
def update_horario(h_id):
    """Atualiza as informações de um horário de aula."""
    data = request.get_json() or {}
    updated = service.atualizar_horario(h_id, data)
    if not updated:
        return jsonify({"error": "Horário não encontrado"}), 404
    return jsonify(updated)

@bp.route("/horarios/<h_id>", methods=["DELETE"])
def delete_horario(h_id):
    """Remove um horário de aula da grade semanal."""
    success = service.deletar_horario(h_id)
    if not success:
        return jsonify({"error": "Horário não encontrado"}), 404
    return jsonify({"success": True})
