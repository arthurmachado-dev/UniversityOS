"""Rotas da API de Materiais: /api/materiais"""
from flask import Blueprint, current_app, jsonify, request, send_file

from services.material_service import MaterialErro, MaterialService

bp = Blueprint("api_materiais", __name__, url_prefix="/api/materiais")


def _service() -> MaterialService:
    # `abridor` pode ser trocado nos testes via app.config["MATERIAL_ABRIDOR"].
    return MaterialService(current_app.config["DATA_DIR"],
                           abridor=current_app.config.get("MATERIAL_ABRIDOR"))


def _erro(exc: MaterialErro):
    return jsonify({"error": str(exc)}), exc.status


def _caminho_do_corpo() -> str:
    dados = request.get_json(silent=True) or {}
    return str(dados.get("caminho", "")) if isinstance(dados, dict) else ""


@bp.get("/scan")
def scan():
    try:
        return jsonify(_service().escanear())
    except MaterialErro as exc:
        return _erro(exc)


@bp.post("/config")
def config():
    try:
        return jsonify(_service().configurar(_caminho_do_corpo()))
    except MaterialErro as exc:
        return _erro(exc)


@bp.post("/abrir")
def abrir():
    try:
        _service().abrir(_caminho_do_corpo())
        return jsonify({"ok": True})
    except MaterialErro as exc:
        return _erro(exc)


@bp.post("/revelar")
def revelar():
    try:
        _service().revelar(_caminho_do_corpo())
        return jsonify({"ok": True})
    except MaterialErro as exc:
        return _erro(exc)


@bp.get("/download")
def download():
    try:
        arquivo = _service().caminho_para_download(request.args.get("caminho", ""))
    except MaterialErro as exc:
        return _erro(exc)
    baixar = request.args.get("download", "").lower() == "true"
    return send_file(arquivo, as_attachment=baixar, download_name=arquivo.name)
