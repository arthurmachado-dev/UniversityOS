from flask import Blueprint, jsonify, request
from services.disciplina_service import DisciplinaService

# Criação do Blueprint da API de Disciplinas e Professores
bp = Blueprint("api_disciplinas", __name__, url_prefix="/api")
service = DisciplinaService()

# --- Rotas de Disciplinas ---

@bp.route("/disciplinas", methods=["GET"])
def get_disciplinas():
    """Retorna a lista completa de disciplinas cadastradas com informações do professor."""
    return jsonify(service.listar_disciplinas())

@bp.route("/disciplinas/<disc_id>", methods=["GET"])
def get_disciplina(disc_id):
    """Busca uma disciplina específica pelo ID."""
    disc = service.obter_disciplina(disc_id)
    if not disc:
        return jsonify({"error": "Disciplina não encontrada"}), 404
    return jsonify(disc)

@bp.route("/disciplinas", methods=["POST"])
def create_disciplina():
    """Cadastra uma nova disciplina no curso."""
    data = request.get_json() or {}
    if not data.get("nome"):
        return jsonify({"error": "O campo 'nome' é obrigatório"}), 400
    created = service.criar_disciplina(data)
    return jsonify(created), 201

@bp.route("/disciplinas/<disc_id>", methods=["PUT"])
def update_disciplina(disc_id):
    """Atualiza as informações de uma disciplina existente."""
    data = request.get_json() or {}
    updated = service.atualizar_disciplina(disc_id, data)
    if not updated:
        return jsonify({"error": "Disciplina não encontrada"}), 404
    return jsonify(updated)

@bp.route("/disciplinas/<disc_id>", methods=["DELETE"])
def delete_disciplina(disc_id):
    """Remove uma disciplina do sistema."""
    success = service.deletar_disciplina(disc_id)
    if not success:
        return jsonify({"error": "Disciplina não encontrada"}), 404
    return jsonify({"success": True})

# --- Rotas de Professores ---

@bp.route("/professores", methods=["GET"])
def get_professores():
    """Retorna a lista de todos os professores cadastrados."""
    return jsonify(service.listar_professores())

@bp.route("/professores", methods=["POST"])
def create_professor():
    """Cadastra um novo professor no corpo docente."""
    data = request.get_json() or {}
    if not data.get("nome"):
        return jsonify({"error": "O campo 'nome' é obrigatório"}), 400
    created = service.criar_professor(data)
    return jsonify(created), 201

@bp.route("/professores/<prof_id>", methods=["DELETE"])
def delete_professor(prof_id):
    """Remove um professor do cadastro."""
    success = service.deletar_professor(prof_id)
    if not success:
        return jsonify({"error": "Professor não encontrado"}), 404
    return jsonify({"success": True})
