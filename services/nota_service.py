from typing import List, Dict, Any, Optional
from repositories.json_repository import JSONRepository
from models.nota import Nota
from services.disciplina_service import DisciplinaService

class NotaService:
    """Serviço responsável pela gestão de avaliações, cálculo de médias ponderadas e simulação de notas necessárias."""
    def __init__(self, data_dir: str = "data"):
        self.nota_repo = JSONRepository(
            filename="notas.json",
            fieldnames=["id", "disciplina_id", "nome_avaliacao", "nota", "peso"],
            data_dir=data_dir
        )
        self.disciplina_service = DisciplinaService(data_dir=data_dir)

    def listar_notas(self) -> List[Dict[str, Any]]:
        """Retorna todas as notas com o nome da disciplina associada."""
        disciplinas_map = {d["id"]: d["nome"] for d in self.disciplina_service.listar_disciplinas()}
        rows = self.nota_repo.read_all()
        notas = []
        for r in rows:
            n = Nota.from_dict(r)
            n_dict = n.to_dict()
            n_dict["disciplina_nome"] = disciplinas_map.get(n.disciplina_id, "Disciplina Desconhecida")
            notas.append(n_dict)
        return notas

    def listar_notas_por_disciplina(self, disciplina_id: str) -> List[Dict[str, Any]]:
        """Retorna as notas de uma disciplina específica."""
        all_notas = self.listar_notas()
        return [n for n in all_notas if n["disciplina_id"] == disciplina_id]

    def calcular_media_disciplina(self, disciplina_id: str) -> float:
        """Calcula a média ponderada das avaliações de uma disciplina."""
        notas = self.listar_notas_por_disciplina(disciplina_id)
        if not notas:
            return 0.0
        soma_ponderada = sum(n["nota"] * n["peso"] for n in notas)
        soma_pesos = sum(n["peso"] for n in notas)
        if soma_pesos == 0:
            return 0.0
        return round(soma_ponderada / soma_pesos, 2)

    def calcular_media_geral(self) -> float:
        """Calcula a média geral do estudante ponderada pela carga horária de cada matéria."""
        disciplinas = self.disciplina_service.listar_disciplinas()
        if not disciplinas:
            return 0.0
        soma_media_peso = 0.0
        soma_pesos = 0.0
        for d in disciplinas:
            m = self.calcular_media_disciplina(d["id"])
            if m > 0.0:
                peso_disc = float(d.get("carga_horaria", 1)) or 1.0
                soma_media_peso += m * peso_disc
                soma_pesos += peso_disc
        if soma_pesos == 0:
            return 0.0
        return round(soma_media_peso / soma_pesos, 2)

    def simular_nota_necessaria(self, disciplina_id: str, media_desejada: float, peso_proxima: float) -> Dict[str, Any]:
        """Calcula a pontuação necessária na próxima avaliação para atingir a meta de média estipulada."""
        notas = self.listar_notas_por_disciplina(disciplina_id)
        soma_ponderada_atual = sum(n["nota"] * n["peso"] for n in notas)
        soma_pesos_atual = sum(n["peso"] for n in notas)

        peso_total = soma_pesos_atual + peso_proxima
        if peso_proxima <= 0:
            return {"erro": "O peso da próxima avaliação deve ser maior que 0"}

        soma_ponderada_necessaria = media_desejada * peso_total
        nota_necessaria = (soma_ponderada_necessaria - soma_ponderada_atual) / peso_proxima
        nota_necessaria_arredondada = round(max(0.0, nota_necessaria), 2)

        return {
            "disciplina_id": disciplina_id,
            "media_desejada": media_desejada,
            "peso_proxima": peso_proxima,
            "nota_atual": self.calcular_media_disciplina(disciplina_id),
            "nota_necessaria": nota_necessaria_arredondada
        }

    def criar_nota(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cadastra uma nova nota de avaliação, definindo o peso padrão com base na carga horária se não especificado."""
        disc_id = data.get("disciplina_id")
        if disc_id:
            disc = self.disciplina_service.obter_disciplina(disc_id)
            if disc and disc.get("carga_horaria"):
                if not data.get("peso") or float(data.get("peso", 0)) <= 0:
                    data["peso"] = float(disc.get("carga_horaria"))
        nota = Nota.from_dict(data)
        saved = self.nota_repo.save(nota.to_dict())
        return saved

    def atualizar_nota(self, nota_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza os dados de uma nota existente."""
        existing = self.nota_repo.find_by_id(nota_id)
        if not existing:
            return None
        data["id"] = nota_id
        nota = Nota.from_dict(data)
        saved = self.nota_repo.save(nota.to_dict())
        return saved

    def deletar_nota(self, nota_id: str) -> bool:
        """Exclui uma nota cadastrada."""
        return self.nota_repo.delete(nota_id)
