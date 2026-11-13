"""Ponto de entrada do UniversityOS (Flask)."""
from __future__ import annotations

import importlib
import logging
import os
from pathlib import Path
from typing import Optional, Union

from flask import Flask, jsonify

from repositories.json_repository import RepositoryError, get_data_dir
from repositories.seed_data import semear

log = logging.getLogger("universityos")

# Cada módulo de rotas deve expor um objeto `bp` (flask.Blueprint).
MODULOS_ROTAS = (
    "routes.pages",
    "routes.api_dashboard",
    "routes.api_tarefas",
    "routes.api_materiais",
    "routes.api_disciplinas",
    "routes.api_notas",
    "routes.api_faltas",
    "routes.api_horarios",
    "routes.api_calendario",
    "routes.api_estatisticas",
)


def create_app(data_dir: Optional[Union[str, Path]] = None, testing: bool = False) -> Flask:
    app = Flask(__name__)
    app.config["DATA_DIR"] = str(get_data_dir(data_dir))
    app.config["TESTING"] = testing
    app.config["JSON_AS_ASCII"] = False

    semear(app.config["DATA_DIR"])  # cria apenas o que estiver ausente/vazio

    for nome in MODULOS_ROTAS:
        try:
            modulo = importlib.import_module(nome)
            app.register_blueprint(modulo.bp)
        except (ImportError, AttributeError) as exc:
            # Permite rodar o projeto enquanto os outros módulos ainda não existem.
            log.warning("Módulo de rotas %s não carregado: %s", nome, exc)

    @app.errorhandler(RepositoryError)
    def erro_repositorio(exc):
        return jsonify({"error": str(exc)}), 500

    @app.errorhandler(404)
    def nao_encontrado(exc):
        return jsonify({"error": "Recurso não encontrado."}), 404

    return app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # 127.0.0.1: o app abre arquivos do PC, então não deve ficar exposto na rede.
    create_app().run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)),
                     debug=os.environ.get("FLASK_DEBUG") == "1")
