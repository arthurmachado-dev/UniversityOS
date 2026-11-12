from flask import Blueprint, jsonify, request
from services.falta_service import FaltaService

# Criação do Blueprint da API de Controle de Faltas e Frequência
bp = Blueprint("api_faltas", __name__, url_prefix="/api")
service = FaltaService()

@bp.route("/faltas", methods=["GET"])
def get_faltas():
    """Lista todos os registros individuais de ausências ou filtra por disciplina."""
    disc_id = request.args.get("disciplina_id")
    if disc_id:
        return jsonify(service.listar_faltas_por_disciplina(disc_id))
    return jsonify(service.listar_faltas())

@bp.route("/faltas/resumo", methods=["GET"])
def get_resumo_faltas():
    """Retorna o cálculo percentual de faltas, limites de 25% e status de perigo/atenção."""
    disc_id = request.args.get("disciplina_id")
    if disc_id:
        return jsonify(service.obter_resumo_faltas_por_disciplina(disc_id))
    return jsonify(service.listar_resumo_todas_disciplinas())

@bp.route("/faltas/incrementar", methods=["POST"])
def incrementar_falta():
    """Registra uma ou mais faltas para uma disciplina específica."""
    data = request.get_json() or {}
    disc_id = data.get("disciplina_id")
    quantidade = data.get("quantidade", 1)
    data_falta = data.get("data", "")
    if not disc_id:
        return jsonify({"error": "O campo 'disciplina_id' é obrigatório"}), 400
    res = service.registrar_falta(disciplina_id=disc_id, quantidade=int(quantidade), data=data_falta)
    return jsonify(res), 201

@bp.route("/faltas/decrementar", methods=["POST"])
def decrementar_falta():
    """Remove ou decrementa uma falta de uma disciplina específica."""
    data = request.get_json() or {}
    disc_id = data.get("disciplina_id")
    quantidade = data.get("quantidade", 1)
    if not disc_id:
        return jsonify({"error": "O campo 'disciplina_id' é obrigatório"}), 400
    sucesso = service.decrementar_falta(disciplina_id=disc_id, quantidade=int(quantidade))
    return jsonify({"success": sucesso}), 200

@bp.route("/faltas/hoje", methods=["POST"])
def registrar_faltas_hoje():
    """Registra ausência em lote para todas as disciplinas selecionadas na grade de hoje."""
    data = request.get_json() or {}
    disc_ids = data.get("disciplina_ids", [])
    if not isinstance(disc_ids, list):
        return jsonify({"error": "'disciplina_ids' deve ser uma lista"}), 400
    registradas = service.registrar_faltas_hoje(disc_ids)
    return jsonify({"success": True, "registradas": registradas}), 201

@bp.route("/faltas/<falta_id>", methods=["DELETE"])
def delete_falta(falta_id):
    """Exclui um registro individual de falta."""
    success = service.deletar_falta(falta_id)
    if not success:
        return jsonify({"error": "Registro de falta não encontrado"}), 404
    return jsonify({"success": True})
