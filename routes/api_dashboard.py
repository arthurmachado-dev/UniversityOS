"""Rota do dashboard: /api/dashboard"""
from flask import Blueprint, current_app, jsonify

from services.dashboard_service import DashboardService

bp = Blueprint("api_dashboard", __name__, url_prefix="/api/dashboard")


@bp.get("")
def resumo():
    return jsonify(DashboardService(current_app.config["DATA_DIR"]).resumo())
