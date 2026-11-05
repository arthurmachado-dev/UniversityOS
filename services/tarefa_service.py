"""Regras de negócio de Tarefas."""
from __future__ import annotations

from datetime import date
from typing import Any, Callable, Dict, List, Optional

from models.tarefa import CAMPOS_EDITAVEIS, Tarefa, STATUS_ATRASADA
from repositories.json_repository import JsonRepository


class TarefaNaoEncontrada(LookupError):
    pass


class TarefaService:
    def __init__(self, data_dir=None, repo: Optional[JsonRepository] = None,
                 disciplinas_repo: Optional[JsonRepository] = None,
                 hoje: Callable[[], date] = date.today):
        self.repo = repo or JsonRepository("tarefas.json", data_dir)
        self.disciplinas_repo = disciplinas_repo or JsonRepository("disciplinas.json", data_dir)
        self._hoje = hoje

    # ------------------------------------------------------------------ helpers
    def _nomes_disciplinas(self) -> Dict[str, str]:
        return {str(d.get("id")): d.get("nome", "") for d in self.disciplinas_repo.listar()}

    def _apresentar(self, dados: Dict[str, Any], nomes: Dict[str, str]) -> Dict[str, Any]:
        tarefa = Tarefa.from_dict(dados)
        saida = tarefa.to_dict()
        saida["status"] = tarefa.status_efetivo(self._hoje())
        saida["disciplina_nome"] = nomes.get(tarefa.disciplina_id) or "Geral"
        return saida

    @staticmethod
    def _chave_ordenacao(t: Dict[str, Any]):
        # Sem prazo vai para o fim; depois, mais urgente primeiro.
        ordem_prio = {"Urgente": 0, "Alta": 1, "Média": 2, "Baixa": 3}
        return (t["data_prazo"] == "", t["data_prazo"], ordem_prio.get(t["prioridade"], 9))

    # --------------------------------------------------------------------- CRUD
    def listar(self) -> List[Dict[str, Any]]:
        nomes = self._nomes_disciplinas()
        itens = [self._apresentar(d, nomes) for d in self.repo.listar()]
        return sorted(itens, key=self._chave_ordenacao)

    def obter(self, id: str) -> Dict[str, Any]:
        dados = self.repo.obter(id)
        if dados is None:
            raise TarefaNaoEncontrada(f"Tarefa {id} não encontrada.")
        return self._apresentar(dados, self._nomes_disciplinas())

    def criar(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._validar_disciplina(payload.get("disciplina_id"))
        tarefa = Tarefa.from_dict(payload)  # levanta ValueError se inválida
        tarefa.id = JsonRepository.gerar_id()
        self.repo.adicionar(tarefa.to_dict())
        return self.obter(tarefa.id)

    def atualizar(self, id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        atual = self.repo.obter(id)
        if atual is None:
            raise TarefaNaoEncontrada(f"Tarefa {id} não encontrada.")
        campos = {k: v for k, v in payload.items() if k in CAMPOS_EDITAVEIS}
        if "disciplina_id" in campos:
            self._validar_disciplina(campos["disciplina_id"])
        mesclado = {**atual, **campos}
        tarefa = Tarefa.from_dict(mesclado)  # valida o resultado final
        self.repo.atualizar(id, {k: v for k, v in tarefa.to_dict().items() if k != "id"})
        return self.obter(id)

    def remover(self, id: str) -> None:
        if not self.repo.remover(id):
            raise TarefaNaoEncontrada(f"Tarefa {id} não encontrada.")

    def concluir(self, id: str) -> Dict[str, Any]:
        return self.atualizar(id, {"status": "Concluída"})

    # ------------------------------------------------------------ consultas extras
    def pendentes(self, limite: Optional[int] = None) -> List[Dict[str, Any]]:
        """Tarefas não concluídas (inclui as atrasadas), em ordem de prazo."""
        itens = [t for t in self.listar() if t["status"] != "Concluída"]
        return itens[:limite] if limite else itens

    def contar_atrasadas(self) -> int:
        return sum(1 for t in self.listar() if t["status"] == STATUS_ATRASADA)

    def _validar_disciplina(self, disciplina_id: Optional[str]) -> None:
        if disciplina_id and str(disciplina_id) not in self._nomes_disciplinas():
            raise ValueError("Disciplina informada não existe.")
