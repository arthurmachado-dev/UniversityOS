from flask import Blueprint, jsonify, request, send_file
from services.material_service import MaterialService

# Criação do Blueprint da API de Materiais
bp = Blueprint("api_materiais", __name__, url_prefix="/api")
service = MaterialService()

@bp.route("/materiais", methods=["GET"])
@bp.route("/materiais/scan", methods=["GET", "POST"])
def scan_materiais():
    """Escaneia o diretório e lista arquivos agrupados por pastas."""
    if request.method == "POST":
        data = request.get_json() or {}
        caminho = data.get("caminho", "")
    else:
        caminho = request.args.get("caminho", "")

    res = service.escanear_pasta_local(caminho if caminho else None)
    if "error" in res:
        return jsonify(res), 400
    return jsonify(res)

@bp.route("/materiais/config", methods=["GET", "POST"])
def config_materiais():
    """Obtém ou define o diretório raiz de materiais."""
    if request.method == "POST":
        data = request.get_json() or {}
        caminho = data.get("caminho", "")
        if not caminho:
            return jsonify({"error": "Informe o caminho da pasta"}), 400
        res = service.set_root_dir(caminho)
        if "error" in res:
            return jsonify(res), 400
        return jsonify(res)
    return jsonify(service.get_config())

@bp.route("/materiais/abrir", methods=["POST"])
def abrir_arquivo():
    """Abre o arquivo no programa padrão do computador."""
    data = request.get_json() or {}
    caminho = data.get("caminho", "")
    if not caminho:
        return jsonify({"error": "Caminho do arquivo não fornecido"}), 400
    res = service.abrir_arquivo_local(caminho)
    if "error" in res:
        return jsonify(res), 400
    return jsonify(res)

@bp.route("/materiais/revelar", methods=["POST"])
def revelar_arquivo():
    """Abre o gerenciador de arquivos no item."""
    data = request.get_json() or {}
    caminho = data.get("caminho", "")
    if not caminho:
        return jsonify({"error": "Caminho não fornecido"}), 400
    res = service.revelar_no_gerenciador(caminho)
    if "error" in res:
        return jsonify(res), 400
    return jsonify(res)

@bp.route("/materiais/download", methods=["GET"])
def download_arquivo():
    """Envia o arquivo para download/visualização."""
    caminho = request.args.get("caminho", "")
    as_attachment = request.args.get("download", "false").lower() == "true"
    path_obj, error = service.obter_path_para_download(caminho)
    if error:
        return jsonify({"error": error}), 404
    return send_file(path_obj, as_attachment=as_attachment, download_name=path_obj.name)
