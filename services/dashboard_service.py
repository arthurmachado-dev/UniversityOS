"""Consolida os dados da página inicial (dashboard)."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Callable, Dict, List, Optional

from repositories.json_repository import JsonRepository
from services.tarefa_service import TarefaService

JANELA_AVALIACOES_DIAS = 14
LIMITE_LISTAS = 5
MEDIA_MINIMA = 6.0          # abaixo disso a disciplina entra em alerta
ALERTA_FREQUENCIA = 0.8     # alerta quando 80% do limite de faltas foi usado


# Uma "fonte" é qualquer função sem argumentos que devolve uma lista de dicionários.
Fonte = Callable[[], List[Dict[str, Any]]]


class DashboardService:
    """Monta o resumo da página inicial a partir de fontes de dados injetáveis.

    Por padrão cada fonte lê o JSON correspondente. ** Trocar a fonte quando Marcio e Pedro subirem services:

        DashboardService(fonte_notas=NotaService().listar,
                         fonte_faltas=FaltaService().listar, ...)

    Formato mínimo esperado de cada fonte (campos que o dashboard lê):
        alunos       -> nome
        disciplinas  -> id, nome, limite_faltas
        notas        -> disciplina_id, nota, peso
        faltas       -> disciplina_id, quantidade
        eventos      -> titulo, tipo, data (AAAA-MM-DD), hora, disciplina_id
    """

    def __init__(self, data_dir=None, hoje: Callable[[], date] = date.today,
                 tarefa_service: Optional[TarefaService] = None,
                 fonte_alunos: Optional[Fonte] = None,
                 fonte_disciplinas: Optional[Fonte] = None,
                 fonte_notas: Optional[Fonte] = None,
                 fonte_faltas: Optional[Fonte] = None,
                 fonte_eventos: Optional[Fonte] = None):
        self._hoje = hoje
        self.tarefas = tarefa_service or TarefaService(data_dir, hoje=hoje)
        self._alunos = fonte_alunos or JsonRepository("alunos.json", data_dir).listar
        self._disciplinas = fonte_disciplinas or JsonRepository("disciplinas.json", data_dir).listar
        self._notas = fonte_notas or JsonRepository("notas.json", data_dir).listar
        self._faltas = fonte_faltas or JsonRepository("faltas.json", data_dir).listar
        self._eventos = fonte_eventos or JsonRepository("eventos.json", data_dir).listar

    # ---------------------------------------------------------------- métricas
    def _medias_por_disciplina(self) -> Dict[str, float]:
        """Média ponderada (nota × peso) de cada disciplina com notas lançadas."""
        acumulado: Dict[str, List[float]] = {}
        for n in self._notas():
            try:
                nota, peso = float(n["nota"]), float(n.get("peso", 1))
            except (KeyError, TypeError, ValueError):
                continue
            soma = acumulado.setdefault(str(n.get("disciplina_id")), [0.0, 0.0])
            soma[0] += nota * peso
            soma[1] += peso
        return {d: s[0] / s[1] for d, s in acumulado.items() if s[1] > 0}

    def _proximos_eventos(self, nomes: Dict[str, str]) -> List[Dict[str, Any]]:
        hoje = self._hoje().isoformat()
        futuros = [e for e in self._eventos() if str(e.get("data", "")) >= hoje]
        futuros.sort(key=lambda e: (e.get("data", ""), e.get("hora") or "99:99"))
        return [{**e, "disciplina_nome": nomes.get(str(e.get("disciplina_id"))) or "Geral"}
                for e in futuros]

    def _alertas(self, nomes: Dict[str, str], medias: Dict[str, float]) -> List[Dict[str, str]]:
        alertas: List[Dict[str, str]] = []

        atrasadas = [t for t in self.tarefas.listar() if t["status"] == "Atrasada"]
        if atrasadas:
            alertas.append({
                "nivel": "error", "titulo": f"{len(atrasadas)} tarefa(s) atrasada(s)",
                "mensagem": "Ex.: " + atrasadas[0]["titulo"] + " (prazo " + atrasadas[0]["data_prazo"] + ")."})

        limites = {str(d["id"]): d.get("limite_faltas") for d in self._disciplinas()}
        for f in self._faltas():
            did = str(f.get("disciplina_id"))
            limite, qtd = limites.get(did), int(f.get("quantidade", 0) or 0)
            if not limite:
                continue
            nome = nomes.get(did, "Disciplina")
            if qtd >= limite:
                alertas.append({"nivel": "error", "titulo": f"Limite de faltas: {nome}",
                                "mensagem": f"{qtd} de {limite} faltas permitidas. Risco de reprovação por falta."})
            elif qtd >= limite * ALERTA_FREQUENCIA:
                alertas.append({"nivel": "warning", "titulo": f"Faltas em {nome}",
                                "mensagem": f"Você usou {qtd} de {limite} faltas permitidas."})

        for did, media in sorted(medias.items(), key=lambda kv: kv[1]):
            if media < MEDIA_MINIMA and did in nomes:
                alertas.append({"nivel": "warning", "titulo": f"Média baixa: {nomes[did]}",
                                "mensagem": f"Média atual {media:.1f} (mínimo {MEDIA_MINIMA:.1f})."})

        proximo = next(iter(self._proximos_eventos(nomes)), None)
        if proximo and proximo.get("data") == self._hoje().isoformat():
            alertas.append({"nivel": "info", "titulo": f"Hoje: {proximo['titulo']}",
                            "mensagem": f"{proximo['tipo']} de {proximo['disciplina_nome']}."})
        return alertas

    # ------------------------------------------------------------------ resumo
    def resumo(self) -> Dict[str, Any]:
        disciplinas = self._disciplinas()
        nomes = {str(d["id"]): d.get("nome", "") for d in disciplinas}
        medias = self._medias_por_disciplina()
        medias_validas = [m for d, m in medias.items() if d in nomes]
        media_geral = round(sum(medias_validas) / len(medias_validas), 2) if medias_validas else 0.0

        eventos = self._proximos_eventos(nomes)
        limite = (self._hoje() + timedelta(days=JANELA_AVALIACOES_DIAS)).isoformat()
        avaliacoes = [e for e in eventos if e.get("data", "") <= limite]
        pendentes = self.tarefas.pendentes()
        alunos = self._alunos()

        return {
            "aluno_nome": (alunos[0].get("nome", "") if alunos else ""),
            "data_hoje": self._hoje().isoformat(),
            "total_disciplinas": len(disciplinas),
            "total_tarefas_pendentes": len(pendentes),
            "total_avaliacoes_proximas": len(avaliacoes),
            "media_geral": media_geral,
            "alertas": self._alertas(nomes, medias),
            "tarefas_recentes": pendentes[:LIMITE_LISTAS],
            "proximos_eventos": eventos[:LIMITE_LISTAS],
        }