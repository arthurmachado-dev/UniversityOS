from pathlib import Path
from typing import Dict, Any

class Material:
    """Representa um arquivo de material de estudo."""
    def __init__(self, titulo: str, caminho_arquivo: str = "", disciplina_id: str = "", id: str = "", tamanho_bytes: int = 0):
        self.id = id
        self.titulo = titulo
        self.caminho_arquivo = caminho_arquivo
        self.disciplina_id = disciplina_id
        self.tamanho_bytes = int(tamanho_bytes) if tamanho_bytes else 0

    @property
    def path(self) -> Path:
        """Retorna o caminho como pathlib.Path."""
        return Path(self.caminho_arquivo) if self.caminho_arquivo else Path()

    @property
    def nome_arquivo(self) -> str:
        """Retorna o nome do arquivo."""
        return self.path.name if self.caminho_arquivo else self.titulo

    @property
    def extensao(self) -> str:
        """Retorna a extensão do arquivo."""
        return self.path.suffix.lower() if self.caminho_arquivo else ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "caminho_arquivo": str(self.caminho_arquivo),
            "disciplina_id": self.disciplina_id,
            "tamanho_bytes": self.tamanho_bytes
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Material":
        return cls(
            id=str(data.get("id", "")),
            titulo=str(data.get("titulo", "")),
            caminho_arquivo=str(data.get("caminho_arquivo", "")),
            disciplina_id=str(data.get("disciplina_id", "")),
            tamanho_bytes=int(data.get("tamanho_bytes", 0) or 0)
        )
