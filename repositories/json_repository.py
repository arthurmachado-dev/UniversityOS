'''Repositório genérico para persistência em arquivos JSON.

Cada arquivo em data/ guarda uma lista de dicionários (ou, em casos de
configuração, um único objeto). A classe oferece CRUD básico, escrita atômica
e proteção contra acesso concorrente dentro do mesmo processo.
'''
from __future__ import annotations

import json
import os
import tempfile
import threading
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

DATA_DIR_PADRAO = Path(__file__).resolve().parent.parent / "data"


class RepositoryError(Exception):
    """Erro de leitura/gravação dos arquivos JSON."""


def get_data_dir(data_dir: Optional[Union[str, Path]] = None) -> Path:
    """Resolve a pasta de dados: argumento > variável de ambiente > padrão."""
    if data_dir:
        return Path(data_dir)
    env = os.environ.get("UNIVERSITYOS_DATA_DIR")
    return Path(env) if env else DATA_DIR_PADRAO


class JsonRepository:
    """CRUD genérico sobre um arquivo JSON.

    Args:
        nome_arquivo: nome do arquivo dentro da pasta de dados (ex.: ``tarefas.json``).
        data_dir: pasta de dados; se omitida usa ``UNIVERSITYOS_DATA_DIR`` ou ``data/``.
        padrao: valor devolvido quando o arquivo não existe ou está vazio.
    """

    _locks: Dict[str, threading.RLock] = {}
    _locks_guard = threading.Lock()

    def __init__(self, nome_arquivo: str, data_dir: Optional[Union[str, Path]] = None, padrao: Any = None):
        self.caminho = get_data_dir(data_dir) / nome_arquivo
        self._padrao = [] if padrao is None else padrao

    # ------------------------------------------------------------------ lock
    @property
    def _lock(self) -> threading.RLock:
        chave = str(self.caminho.resolve())
        with JsonRepository._locks_guard:
            return JsonRepository._locks.setdefault(chave, threading.RLock())

    # --------------------------------------------------------- leitura/escrita
    def carregar(self) -> Any:
        """Lê o arquivo inteiro. Arquivo ausente/vazio devolve o valor padrão."""
        with self._lock:
            if not self.caminho.exists():
                return self._copiar_padrao()
            try:
                texto = self.caminho.read_text(encoding="utf-8")
            except OSError as exc:
                raise RepositoryError(f"Não foi possível ler {self.caminho.name}: {exc}") from exc
            if not texto.strip():
                return self._copiar_padrao()
            try:
                return json.loads(texto)
            except json.JSONDecodeError as exc:
                raise RepositoryError(f"JSON inválido em {self.caminho.name}: {exc}") from exc

    def salvar(self, dados: Any) -> None:
        """Grava o arquivo de forma atômica (arquivo temporário + rename)."""
        with self._lock:
            try:
                self.caminho.parent.mkdir(parents=True, exist_ok=True)
                fd, tmp = tempfile.mkstemp(dir=self.caminho.parent, suffix=".tmp")
                try:
                    with os.fdopen(fd, "w", encoding="utf-8") as f:
                        json.dump(dados, f, ensure_ascii=False, indent=2)
                    os.replace(tmp, self.caminho)
                except BaseException:
                    if os.path.exists(tmp):
                        os.remove(tmp)
                    raise
            except OSError as exc:
                raise RepositoryError(f"Não foi possível gravar {self.caminho.name}: {exc}") from exc

    def _copiar_padrao(self) -> Any:
        return json.loads(json.dumps(self._padrao))

    # -------------------------------------------------------------------- CRUD
    def _lista(self) -> List[Dict[str, Any]]:
        dados = self.carregar()
        if not isinstance(dados, list):
            raise RepositoryError(f"{self.caminho.name} deveria conter uma lista.")
        return dados

    def listar(self) -> List[Dict[str, Any]]:
        return self._lista()

    def obter(self, id: str) -> Optional[Dict[str, Any]]:
        for item in self._lista():
            if str(item.get("id")) == str(id):
                return item
        return None

    def filtrar(self, predicado: Callable[[Dict[str, Any]], bool]) -> List[Dict[str, Any]]:
        return [i for i in self._lista() if predicado(i)]

    def adicionar(self, item: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            itens = self._lista()
            novo = dict(item)
            if not novo.get("id"):
                novo["id"] = self.gerar_id()
            itens.append(novo)
            self.salvar(itens)
            return novo

    def atualizar(self, id: str, campos: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        with self._lock:
            itens = self._lista()
            for item in itens:
                if str(item.get("id")) == str(id):
                    item.update({k: v for k, v in campos.items() if k != "id"})
                    self.salvar(itens)
                    return item
            return None

    def remover(self, id: str) -> bool:
        with self._lock:
            itens = self._lista()
            restantes = [i for i in itens if str(i.get("id")) != str(id)]
            if len(restantes) == len(itens):
                return False
            self.salvar(restantes)
            return True

    @staticmethod
    def gerar_id() -> str:
        return uuid.uuid4().hex[:8]
