"""Rotas da API de Tarefas: /api/tarefas"""
from flask import Blueprint, current_app, jsonify, request

from services.tarefa_service import TarefaNaoEncontrada, TarefaService

bp = Blueprint("api_tarefas", __name__, url_prefix="/api/tarefas")


def _service() -> TarefaService:
    return TarefaService(current_app.config["DATA_DIR"])


def _json_ou_400():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return None
    return dados


@bp.get("")
def listar():
    return jsonify(_service().listar())


@bp.get("/<id>")
def obter(id):
    try:
        return jsonify(_service().obter(id))
    except TarefaNaoEncontrada as exc:
        return jsonify({"error": str(exc)}), 404


@bp.post("")
def criar():
    dados = _json_ou_400()
    if dados is None:
        return jsonify({"error": "Corpo da requisição deve ser um JSON."}), 400
    try:
        return jsonify(_service().criar(dados)), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@bp.route("/<id>", methods=["PUT", "PATCH"])
def atualizar(id):
    dados = _json_ou_400()
    if dados is None:
        return jsonify({"error": "Corpo da requisição deve ser um JSON."}), 400
    try:
        return jsonify(_service().atualizar(id, dados))
    except TarefaNaoEncontrada as exc:
        return jsonify({"error": str(exc)}), 404
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@bp.delete("/<id>")
def remover(id):
    try:
        _service().remover(id)
        return jsonify({"ok": True})
    except TarefaNaoEncontrada as exc:
        return jsonify({"error": str(exc)}), 404
