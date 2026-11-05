"""Modelo de Tarefa (trabalhos, exercícios e prazos)."""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, Optional

PRIORIDADES = ("Baixa", "Média", "Alta", "Urgente")
STATUS_VALIDOS = ("Pendente", "Em andamento", "Concluída")
STATUS_ATRASADA = "Atrasada"  # status derivado: nunca é gravado em disco
CAMPOS_EDITAVEIS = ("titulo", "disciplina_id", "prioridade", "data_prazo", "status",
                    "tempo_estimado", "descricao")


class Tarefa:
    """Uma tarefa acadêmica com prioridade, prazo e status.

    Os atributos são validados nos *setters*, então um objeto ``Tarefa`` nunca
    fica em estado inválido. ``Atrasada`` não é um status armazenado: é
    calculado por :meth:`status_efetivo` a partir do prazo.
    """

    def __init__(self, titulo: str, disciplina_id: str = "", prioridade: str = "Média",
                 data_prazo: str = "", status: str = "Pendente", tempo_estimado: str = "",
                 descricao: str = "", id: str = ""):
        self.id = str(id or "")
        self.titulo = titulo
        self.disciplina_id = disciplina_id
        self.prioridade = prioridade
        self.data_prazo = data_prazo
        self.status = status
        self.tempo_estimado = tempo_estimado
        self.descricao = descricao

    # ------------------------------------------------------------- validações
    @property
    def titulo(self) -> str:
        return self._titulo

    @titulo.setter
    def titulo(self, valor: str) -> None:
        valor = (valor or "").strip()
        if not valor:
            raise ValueError("O título da tarefa é obrigatório.")
        self._titulo = valor

    @property
    def disciplina_id(self) -> str:
        return self._disciplina_id

    @disciplina_id.setter
    def disciplina_id(self, valor: Optional[str]) -> None:
        self._disciplina_id = str(valor).strip() if valor else ""

    @property
    def prioridade(self) -> str:
        return self._prioridade

    @prioridade.setter
    def prioridade(self, valor: str) -> None:
        if valor not in PRIORIDADES:
            raise ValueError(f"Prioridade inválida: {valor!r}. Use: {', '.join(PRIORIDADES)}.")
        self._prioridade = valor

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, valor: str) -> None:
        if valor not in STATUS_VALIDOS:
            raise ValueError(f"Status inválido: {valor!r}. Use: {', '.join(STATUS_VALIDOS)}.")
        self._status = valor

    @property
    def data_prazo(self) -> str:
        return self._data_prazo.isoformat() if self._data_prazo else ""

    @data_prazo.setter
    def data_prazo(self, valor: Optional[str]) -> None:
        if not valor:
            self._data_prazo = None
            return
        try:
            self._data_prazo = date.fromisoformat(str(valor).strip())
        except ValueError as exc:
            raise ValueError("Prazo inválido. Use o formato AAAA-MM-DD.") from exc

    @property
    def prazo(self) -> Optional[date]:
        return self._data_prazo

    @property
    def tempo_estimado(self) -> str:
        return self._tempo_estimado

    @tempo_estimado.setter
    def tempo_estimado(self, valor: Optional[str]) -> None:
        self._tempo_estimado = (valor or "").strip()

    @property
    def descricao(self) -> str:
        return self._descricao

    @descricao.setter
    def descricao(self, valor: Optional[str]) -> None:
        self._descricao = (valor or "").strip()

    # --------------------------------------------------------------- comportamento
    @property
    def concluida(self) -> bool:
        return self._status == "Concluída"

    def concluir(self) -> None:
        self._status = "Concluída"

    def reabrir(self) -> None:
        self._status = "Pendente"

    def esta_atrasada(self, hoje: Optional[date] = None) -> bool:
        hoje = hoje or date.today()
        return (not self.concluida) and self._data_prazo is not None and self._data_prazo < hoje

    def status_efetivo(self, hoje: Optional[date] = None) -> str:
        return STATUS_ATRASADA if self.esta_atrasada(hoje) else self._status

    # ------------------------------------------------------------ serialização
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "disciplina_id": self.disciplina_id,
            "prioridade": self.prioridade,
            "data_prazo": self.data_prazo,
            "status": self.status,
            "tempo_estimado": self.tempo_estimado,
            "descricao": self.descricao,
        }

    @classmethod
    def from_dict(cls, dados: Dict[str, Any]) -> "Tarefa":
        return cls(
            id=str(dados.get("id", "")),
            titulo=dados.get("titulo", ""),
            disciplina_id=dados.get("disciplina_id", ""),
            prioridade=dados.get("prioridade") or "Média",
            data_prazo=dados.get("data_prazo", ""),
            status=dados.get("status") or "Pendente",
            tempo_estimado=dados.get("tempo_estimado", ""),
            descricao=dados.get("descricao", ""),
        )

    def __repr__(self) -> str:
        return f"Tarefa(id={self.id!r}, titulo={self.titulo!r}, status={self.status!r})"
