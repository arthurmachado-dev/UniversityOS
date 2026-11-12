from flask import Blueprint, jsonify, request
from services.nota_service import NotaService

# Criação do Blueprint da API de Notas e Calculadora/Simulador de Médias
bp = Blueprint("api_notas", __name__, url_prefix="/api")
service = NotaService()

@bp.route("/notas", methods=["GET"])
def get_notas():
    """Retorna todas as notas cadastradas ou filtra por disciplina."""
    disc_id = request.args.get("disciplina_id")
    if disc_id:
        return jsonify(service.listar_notas_por_disciplina(disc_id))
    return jsonify(service.listar_notas())

@bp.route("/notas", methods=["POST"])
def create_nota():
    """Cadastra uma nova nota de avaliação."""
    data = request.get_json() or {}
    if not data.get("disciplina_id") or not data.get("nome_avaliacao"):
        return jsonify({"error": "Os campos 'disciplina_id' e 'nome_avaliacao' são obrigatórios"}), 400
    created = service.criar_nota(data)
    return jsonify(created), 201

@bp.route("/notas/<nota_id>", methods=["PUT"])
def update_nota(nota_id):
    """Atualiza uma nota existente."""
    data = request.get_json() or {}
    updated = service.atualizar_nota(nota_id, data)
    if not updated:
        return jsonify({"error": "Nota não encontrada"}), 404
    return jsonify(updated)

@bp.route("/notas/<nota_id>", methods=["DELETE"])
def delete_nota(nota_id):
    """Exclui uma nota cadastrada."""
    success = service.deletar_nota(nota_id)
    if not success:
        return jsonify({"error": "Nota não encontrada"}), 404
    return jsonify({"success": True})

@bp.route("/notas/simular", methods=["POST"])
def simular_nota():
    """Calcula a nota necessária na próxima avaliação para atingir a média desejada."""
    data = request.get_json() or {}
    disc_id = data.get("disciplina_id")
    media_desejada = float(data.get("media_desejada", 7.0))
    peso_proxima = float(data.get("peso_proxima", 1.0))
    if not disc_id:
        return jsonify({"error": "O campo 'disciplina_id' é obrigatório"}), 400
    resultado = service.simular_nota_necessaria(disc_id, media_desejada, peso_proxima)
    return jsonify(resultado)
