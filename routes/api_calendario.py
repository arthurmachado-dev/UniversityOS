from flask import Blueprint, jsonify, request
from services.calendario_service import CalendarioService

# Criação do Blueprint da API de Calendário e Eventos Acadêmicos
bp = Blueprint("api_calendario", __name__, url_prefix="/api")
service = CalendarioService()

@bp.route("/eventos", methods=["GET"])
def get_eventos():
    """Retorna a lista de eventos ou apenas os próximos compromissos."""
    proximos = request.args.get("proximos")
    if proximos and proximos.lower() in ["true", "1"]:
        limite = int(request.args.get("limite", 5))
        return jsonify(service.listar_proximos_eventos(limite=limite))
    return jsonify(service.listar_eventos())

@bp.route("/eventos/<e_id>", methods=["GET"])
def get_evento(e_id):
    """Busca os detalhes de um evento específico pelo ID."""
    ev = service.obter_evento(e_id)
    if not ev:
        return jsonify({"error": "Evento não encontrado"}), 404
    return jsonify(ev)

@bp.route("/eventos", methods=["POST"])
def create_evento():
    """Cadastra um novo evento acadêmico (prova, trabalho, aula, seminário)."""
    data = request.get_json() or {}
    if not data.get("titulo") or not data.get("data"):
        return jsonify({"error": "Os campos 'titulo' e 'data' são obrigatórios"}), 400
    created = service.criar_evento(data)
    return jsonify(created), 201

@bp.route("/eventos/<e_id>", methods=["PUT"])
def update_evento(e_id):
    """Atualiza as informações de um evento existente."""
    data = request.get_json() or {}
    updated = service.atualizar_evento(e_id, data)
    if not updated:
        return jsonify({"error": "Evento não encontrado"}), 404
    return jsonify(updated)

@bp.route("/eventos/<e_id>", methods=["DELETE"])
def delete_evento(e_id):
    """Exclui um evento acadêmico da agenda."""
    success = service.deletar_evento(e_id)
    if not success:
        return jsonify({"error": "Evento não encontrado"}), 404
    return jsonify({"success": True})
