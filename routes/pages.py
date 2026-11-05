"""Rotas de páginas HTML (renderizam os templates)."""
from flask import Blueprint, render_template

bp = Blueprint("pages", __name__)

PAGINAS = {
    "/": "index.html",
    "/disciplinas": "disciplinas.html",
    "/notas": "notas.html",
    "/faltas": "faltas.html",
    "/horarios": "horarios.html",
    "/tarefas": "tarefas.html",
    "/calendario": "calendario.html",
    "/materiais": "materiais.html",
    "/estatisticas": "estatisticas.html",
}


def _registrar(rota: str, template: str) -> None:
    endpoint = "inicio" if rota == "/" else rota.strip("/")
    bp.add_url_rule(rota, endpoint, lambda t=template: render_template(t))


for _rota, _template in PAGINAS.items():
    _registrar(_rota, _template)
