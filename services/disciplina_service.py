from typing import List, Dict, Any, Optional
from repositories.json_repository import JSONRepository
from models.disciplina import Disciplina
from models.professor import Professor

class DisciplinaService:
    """Serviço responsável pelo gerenciamento de disciplinas, professores e alocações acadêmicas."""
    def __init__(self, data_dir: str = "data"):
        self.disciplina_repo = JSONRepository(
            filename="disciplinas.json",
            fieldnames=["id", "nome", "codigo", "professor_id", "turma", "carga_horaria", "semestre", "descricao"],
            data_dir=data_dir
        )
        self.professor_repo = JSONRepository(
            filename="professores.json",
            fieldnames=["id", "nome", "email", "departamento"],
            data_dir=data_dir
        )

    def listar_professores(self) -> List[Dict[str, Any]]:
        """Retorna todos os professores cadastrados no sistema."""
        rows = self.professor_repo.read_all()
        return [Professor.from_dict(r).to_dict() for r in rows]

    def obter_professor(self, prof_id: str) -> Optional[Dict[str, Any]]:
        """Busca um professor pelo seu identificador único."""
        row = self.professor_repo.find_by_id(prof_id)
        return Professor.from_dict(row).to_dict() if row else None

    def criar_professor(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cadastra um novo professor no corpo docente."""
        prof = Professor.from_dict(data)
        saved = self.professor_repo.save(prof.to_dict())
        return saved

    def deletar_professor(self, prof_id: str) -> bool:
        """Remove um professor do cadastro."""
        return self.professor_repo.delete(prof_id)

    def listar_disciplinas(self) -> List[Dict[str, Any]]:
        """Retorna todas as disciplinas cadastradas com os nomes dos respectivos professores."""
        professores_map = {p["id"]: p["nome"] for p in self.listar_professores()}
        rows = self.disciplina_repo.read_all()
        disciplinas = []
        for r in rows:
            disc = Disciplina.from_dict(r)
            d_dict = disc.to_dict()
            d_dict["professor_nome"] = professores_map.get(disc.professor_id, "Não informado")
            disciplinas.append(d_dict)
        return disciplinas

    def obter_disciplina(self, disc_id: str) -> Optional[Dict[str, Any]]:
        """Busca uma disciplina pelo ID com as informações detalhadas do professor associado."""
        row = self.disciplina_repo.find_by_id(disc_id)
        if not row:
            return None
        disc = Disciplina.from_dict(row)
        d_dict = disc.to_dict()
        prof = self.obter_professor(disc.professor_id)
        d_dict["professor_nome"] = prof["nome"] if prof else "Não informado"
        return d_dict

    def criar_disciplina(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria e persiste uma nova disciplina acadêmica."""
        disc = Disciplina.from_dict(data)
        saved = self.disciplina_repo.save(disc.to_dict())
        return self.obter_disciplina(saved["id"]) or saved

    def atualizar_disciplina(self, disc_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza os dados de uma disciplina existente."""
        existing = self.disciplina_repo.find_by_id(disc_id)
        if not existing:
            return None
        data["id"] = disc_id
        disc = Disciplina.from_dict(data)
        saved = self.disciplina_repo.save(disc.to_dict())
        return self.obter_disciplina(saved["id"])

    def deletar_disciplina(self, disc_id: str) -> bool:
        """Remove uma disciplina do catálogo acadêmico."""
        return self.disciplina_repo.delete(disc_id)
