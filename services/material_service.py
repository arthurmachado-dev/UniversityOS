"""Regras de negócio de Materiais de Estudo (pastas locais do aluno)."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from models.material import Material
from repositories.json_repository import JsonRepository

# Nunca abrimos arquivos executáveis/scripts a partir da interface web.
EXTENSOES_BLOQUEADAS = {
    ".exe", ".bat", ".cmd", ".com", ".msi", ".scr", ".ps1", ".vbs", ".vbe",
    ".js", ".jse", ".wsf", ".sh", ".app", ".jar", ".lnk", ".reg", ".dll",
}
LIMITE_ARQUIVOS = 5000
PASTA_GERAL = "Geral"


class MaterialErro(Exception):
    """Erro de regra de negócio; ``status`` é o código HTTP sugerido."""

    def __init__(self, mensagem: str, status: int = 400):
        super().__init__(mensagem)
        self.status = status


class MaterialService:
    def __init__(self, data_dir=None, repo: Optional[JsonRepository] = None,
                 disciplinas_repo: Optional[JsonRepository] = None,
                 abridor: Optional[Callable[[Path, bool], None]] = None):
        # materiais.json guarda um objeto de configuração: {"pasta_raiz": "..."}
        self.repo = repo or JsonRepository("materiais.json", data_dir, padrao={"pasta_raiz": ""})
        self.disciplinas_repo = disciplinas_repo or JsonRepository("disciplinas.json", data_dir)
        self._abridor = abridor or abrir_no_sistema

    # ------------------------------------------------------------------ config
    def _config(self) -> Dict[str, Any]:
        dados = self.repo.carregar()
        return dados if isinstance(dados, dict) else {"pasta_raiz": ""}

    def pasta_raiz(self) -> Optional[Path]:
        bruto = self._config().get("pasta_raiz", "")
        return Path(bruto) if bruto else None

    def configurar(self, caminho: str) -> Dict[str, Any]:
        caminho = (caminho or "").strip().strip('"')
        if not caminho:
            raise MaterialErro("Informe o caminho da pasta.")
        pasta = Path(caminho).expanduser()
        if not pasta.is_dir():
            raise MaterialErro("Pasta não encontrada neste computador.", 404)
        config = self._config()
        config["pasta_raiz"] = str(pasta.resolve())
        self.repo.salvar(config)
        return {"pasta_raiz": config["pasta_raiz"]}

    # -------------------------------------------------------------------- scan
    def escanear(self) -> Dict[str, Any]:
        raiz = self.pasta_raiz()
        if raiz is None:
            raise MaterialErro("Nenhuma pasta de materiais configurada.", 404)
        if not raiz.is_dir():
            raise MaterialErro("A pasta configurada não existe mais.", 404)

        disciplinas = {d.get("nome", "").lower(): str(d.get("id")) for d in self.disciplinas_repo.listar()}
        grupos: Dict[str, List[Material]] = {}
        total = 0
        for atual, subdirs, arquivos in os.walk(raiz):
            subdirs[:] = sorted(d for d in subdirs if not d.startswith("."))
            for nome in sorted(arquivos):
                if nome.startswith(".") or total >= LIMITE_ARQUIVOS:
                    continue
                arq = Path(atual) / nome
                rel = arq.relative_to(raiz)
                pasta = rel.parts[0] if len(rel.parts) > 1 else PASTA_GERAL
                try:
                    tamanho = arq.stat().st_size
                except OSError:
                    continue
                titulo = str(Path(*rel.parts[1:])) if len(rel.parts) > 1 else nome
                grupos.setdefault(pasta, []).append(Material(
                    titulo=titulo, caminho_arquivo=str(arq), tamanho_bytes=tamanho,
                    disciplina_id=disciplinas.get(pasta.lower(), ""), id=str(total)))
                total += 1

        # pastas vazias também aparecem
        for sub in sorted(p for p in raiz.iterdir() if p.is_dir() and not p.name.startswith(".")):
            grupos.setdefault(sub.name, [])

        subpastas = []
        for nome_pasta in sorted(grupos, key=str.lower):
            materiais = grupos[nome_pasta]
            caminho_pasta = raiz if nome_pasta == PASTA_GERAL and not (raiz / nome_pasta).is_dir() else raiz / nome_pasta
            subpastas.append({
                "nome_pasta": nome_pasta,
                "caminho_pasta": str(caminho_pasta),
                "total_arquivos": len(materiais),
                "disciplina_id": materiais[0].disciplina_id if materiais else disciplinas.get(nome_pasta.lower(), ""),
                "arquivos": [{"nome": m.titulo, "tamanho_bytes": m.tamanho_bytes,
                              "caminho": m.caminho_arquivo, "extensao": m.extensao} for m in materiais],
            })
        return {"pasta_raiz": raiz.name or str(raiz), "caminho": str(raiz), "subpastas": subpastas}

    # ------------------------------------------------------------- segurança
    def resolver_seguro(self, caminho: str, *, arquivo: Optional[bool] = None) -> Path:
        """Garante que ``caminho`` está dentro da pasta de materiais configurada."""
        raiz = self.pasta_raiz()
        if raiz is None:
            raise MaterialErro("Nenhuma pasta de materiais configurada.", 404)
        if not caminho:
            raise MaterialErro("Caminho não informado.")
        try:
            alvo = Path(caminho).resolve()
            base = raiz.resolve()
        except (OSError, RuntimeError):
            raise MaterialErro("Caminho inválido.")
        if alvo != base and base not in alvo.parents:
            raise MaterialErro("Acesso negado: o caminho está fora da pasta de materiais.", 403)
        if not alvo.exists():
            raise MaterialErro("Arquivo ou pasta não encontrado.", 404)
        if arquivo is True and not alvo.is_file():
            raise MaterialErro("O caminho não é um arquivo.")
        return alvo

    # ------------------------------------------------------------------ ações
    def abrir(self, caminho: str) -> None:
        alvo = self.resolver_seguro(caminho)
        if alvo.is_file() and alvo.suffix.lower() in EXTENSOES_BLOQUEADAS:
            raise MaterialErro("Este tipo de arquivo não pode ser aberto pelo sistema.", 403)
        self._abridor(alvo, False)

    def revelar(self, caminho: str) -> None:
        self._abridor(self.resolver_seguro(caminho), True)

    def caminho_para_download(self, caminho: str) -> Path:
        return self.resolver_seguro(caminho, arquivo=True)


def abrir_no_sistema(alvo: Path, revelar: bool = False) -> None:
    """Abre um arquivo/pasta com o programa padrão do sistema operacional."""
    try:
        if sys.platform.startswith("win"):
            if revelar and alvo.is_file():
                subprocess.Popen(["explorer", "/select,", str(alvo)])
            else:
                os.startfile(str(alvo))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-R", str(alvo)] if revelar else ["open", str(alvo)])
        else:
            destino = alvo.parent if (revelar and alvo.is_file()) else alvo
            subprocess.Popen(["xdg-open", str(destino)])
    except (OSError, FileNotFoundError) as exc:
        raise MaterialErro(f"Não foi possível abrir no computador: {exc}", 500)
