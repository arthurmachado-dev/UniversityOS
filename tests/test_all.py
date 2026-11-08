"""Testes unitários: repositório, seed, modelo Tarefa e serviços."""
import json
from datetime import date

import pytest

from models.tarefa import Tarefa
from repositories.json_repository import JsonRepository, RepositoryError
from repositories.seed_data import ARQUIVOS, semear
from services.dashboard_service import DashboardService
from services.material_service import MaterialErro, MaterialService
from services.tarefa_service import TarefaNaoEncontrada, TarefaService

HOJE = date(2026, 11, 2)


@pytest.fixture()
def dados(tmp_path):
    semear(tmp_path, hoje=HOJE)
    return tmp_path


# ------------------------------------------------------------- JsonRepository
def test_repositorio_crud(tmp_path):
    repo = JsonRepository("x.json", tmp_path)
    assert repo.listar() == []
    item = repo.adicionar({"nome": "a"})
    assert item["id"] and repo.obter(item["id"])["nome"] == "a"
    assert repo.atualizar(item["id"], {"nome": "b"})["nome"] == "b"
    assert repo.atualizar("inexistente", {}) is None
    assert repo.remover(item["id"]) is True
    assert repo.remover(item["id"]) is False


def test_repositorio_arquivo_vazio_vira_padrao(tmp_path):
    (tmp_path / "v.json").write_text("", encoding="utf-8")
    assert JsonRepository("v.json", tmp_path).listar() == []


def test_repositorio_json_corrompido_nao_sobrescreve(tmp_path):
    (tmp_path / "c.json").write_text("{quebrado", encoding="utf-8")
    repo = JsonRepository("c.json", tmp_path)
    with pytest.raises(RepositoryError):
        repo.adicionar({"a": 1})
    assert (tmp_path / "c.json").read_text(encoding="utf-8") == "{quebrado"


def test_repositorio_preserva_acentos(tmp_path):
    repo = JsonRepository("a.json", tmp_path)
    repo.adicionar({"nome": "Concluída"})
    assert "Concluída" in repo.caminho.read_text(encoding="utf-8")


# ----------------------------------------------------------------------- seed
def test_seed_cria_todos_os_arquivos(tmp_path):
    resultado = semear(tmp_path, hoje=HOJE)
    assert set(resultado) == {f"{n}.json" for n in ARQUIVOS}
    for nome in ARQUIVOS:
        json.loads((tmp_path / f"{nome}.json").read_text(encoding="utf-8"))


def test_seed_nao_sobrescreve_dados_existentes(tmp_path):
    semear(tmp_path, hoje=HOJE)
    repo = JsonRepository("tarefas.json", tmp_path)
    repo.salvar([{"id": "meu", "titulo": "Minha"}])
    assert semear(tmp_path, hoje=HOJE)["tarefas.json"] == "mantido"
    assert repo.listar()[0]["id"] == "meu"
    assert semear(tmp_path, forcar=True, hoje=HOJE)["tarefas.json"] == "criado"


# --------------------------------------------------------------------- Tarefa
def test_tarefa_validacoes():
    with pytest.raises(ValueError):
        Tarefa(titulo="  ")
    with pytest.raises(ValueError):
        Tarefa(titulo="x", prioridade="Máxima")
    with pytest.raises(ValueError):
        Tarefa(titulo="x", status="Atrasada")  # status derivado, não gravável
    with pytest.raises(ValueError):
        Tarefa(titulo="x", data_prazo="31/12/2026")


def test_tarefa_atrasada_e_concluida():
    t = Tarefa(titulo="x", data_prazo="2026-11-01")
    assert t.esta_atrasada(HOJE) and t.status_efetivo(HOJE) == "Atrasada"
    t.concluir()
    assert not t.esta_atrasada(HOJE) and t.status_efetivo(HOJE) == "Concluída"
    assert not Tarefa(titulo="y", data_prazo="2026-11-02").esta_atrasada(HOJE)
    assert not Tarefa(titulo="z").esta_atrasada(HOJE)


def test_tarefa_roundtrip():
    t = Tarefa(titulo="  x ", prioridade="Alta", data_prazo="2026-12-01", id="1")
    assert Tarefa.from_dict(t.to_dict()).to_dict() == t.to_dict()


# -------------------------------------------------------------- TarefaService
def test_service_lista_com_status_derivado_e_nome(dados):
    svc = TarefaService(dados, hoje=lambda: HOJE)
    por_id = {t["id"]: t for t in svc.listar()}
    assert por_id["tar-2"]["status"] == "Atrasada"
    assert por_id["tar-1"]["disciplina_nome"] == "Programação Orientada a Objetos"
    assert por_id["tar-4"]["disciplina_nome"] == "Cálculo Diferencial e Integral"
    assert por_id["tar-5"]["status"] == "Concluída"  # prazo passado, mas concluída


def test_service_tarefa_sem_disciplina_vira_geral(dados):
    svc = TarefaService(dados, hoje=lambda: HOJE)
    nova = svc.criar({"titulo": "Livre"})
    assert nova["disciplina_nome"] == "Geral"


def test_service_ordena_por_prazo_sem_prazo_no_fim(dados):
    lista = TarefaService(dados, hoje=lambda: HOJE).listar()
    assert lista[-1]["data_prazo"] == ""


def test_service_criar_atualizar_remover(dados):
    svc = TarefaService(dados, hoje=lambda: HOJE)
    nova = svc.criar({"titulo": "Estudar", "disciplina_id": "", "prioridade": "Média",
                      "data_prazo": "", "status": "Pendente"})
    assert nova["disciplina_nome"] == "Geral"
    assert svc.atualizar(nova["id"], {"status": "Concluída"})["status"] == "Concluída"
    svc.remover(nova["id"])
    with pytest.raises(TarefaNaoEncontrada):
        svc.obter(nova["id"])


def test_service_rejeita_disciplina_inexistente_e_status_invalido(dados):
    svc = TarefaService(dados, hoje=lambda: HOJE)
    with pytest.raises(ValueError):
        svc.criar({"titulo": "x", "disciplina_id": "nao-existe"})
    with pytest.raises(ValueError):
        svc.atualizar("tar-1", {"status": "Atrasada"})
    assert svc.obter("tar-1")["status"] == "Em andamento"  # não foi alterada


def test_service_update_ignora_campos_desconhecidos(dados):
    svc = TarefaService(dados, hoje=lambda: HOJE)
    svc.atualizar("tar-1", {"id": "hack", "foo": "bar", "titulo": "Novo"})
    assert svc.obter("tar-1")["titulo"] == "Novo"
    assert "foo" not in svc.repo.obter("tar-1")


# ------------------------------------------------------------ MaterialService
@pytest.fixture()
def pasta_materiais(tmp_path):
    raiz = tmp_path / "Materiais"
    (raiz / "Programação Orientada a Objetos").mkdir(parents=True)
    (raiz / "Programação Orientada a Objetos" / "aula1.pdf").write_bytes(b"x" * 10)
    (raiz / "Programação Orientada a Objetos" / "sub").mkdir()
    (raiz / "Programação Orientada a Objetos" / "sub" / "ex.txt").write_text("oi")
    (raiz / "Cálculo").mkdir()
    (raiz / "solto.md").write_text("# solto")
    (raiz / "perigo.exe").write_bytes(b"MZ")
    (tmp_path / "segredo.txt").write_text("fora")
    return raiz


def _svc(dados, abertos=None):
    return MaterialService(dados, abridor=lambda p, r: (abertos if abertos is not None else []).append((p, r)))


def test_scan_sem_pasta_configurada(dados):
    with pytest.raises(MaterialErro) as e:
        _svc(dados).escanear()
    assert e.value.status == 404


def test_config_valida_pasta(dados, pasta_materiais):
    svc = _svc(dados)
    with pytest.raises(MaterialErro):
        svc.configurar("")
    with pytest.raises(MaterialErro):
        svc.configurar(str(pasta_materiais / "nao-existe"))
    svc.configurar(str(pasta_materiais))
    assert svc.pasta_raiz() == pasta_materiais.resolve()


def test_scan_agrupa_por_subpasta(dados, pasta_materiais):
    svc = _svc(dados)
    svc.configurar(str(pasta_materiais))
    res = svc.escanear()
    por_nome = {s["nome_pasta"]: s for s in res["subpastas"]}
    assert set(por_nome) == {"Programação Orientada a Objetos", "Cálculo", "Geral"}
    poo = por_nome["Programação Orientada a Objetos"]
    assert poo["total_arquivos"] == 2 and poo["disciplina_id"] == "disc-poo"
    assert por_nome["Cálculo"]["arquivos"] == []
    assert {a["nome"] for a in por_nome["Geral"]["arquivos"]} == {"solto.md", "perigo.exe"}
    assert all({"nome", "tamanho_bytes", "caminho"} <= set(a) for a in poo["arquivos"])


def test_abrir_bloqueia_fora_da_raiz_e_executaveis(dados, pasta_materiais, tmp_path):
    abertos = []
    svc = _svc(dados, abertos)
    svc.configurar(str(pasta_materiais))
    with pytest.raises(MaterialErro) as e:
        svc.abrir(str(tmp_path / "segredo.txt"))
    assert e.value.status == 403
    with pytest.raises(MaterialErro) as e:
        svc.abrir(str(pasta_materiais / ".." / "segredo.txt"))  # path traversal
    assert e.value.status == 403
    with pytest.raises(MaterialErro) as e:
        svc.abrir(str(pasta_materiais / "perigo.exe"))
    assert e.value.status == 403
    assert abertos == []
    svc.abrir(str(pasta_materiais / "solto.md"))
    svc.revelar(str(pasta_materiais / "Cálculo"))
    assert len(abertos) == 2 and abertos[1][1] is True


# ------------------------------------------------------------------ Dashboard
def test_dashboard_resumo(dados):
    r = DashboardService(dados, hoje=lambda: HOJE).resumo()
    assert r["total_disciplinas"] == 4
    assert r["total_tarefas_pendentes"] == 4  # tar-1..4 (tar-5 concluída)
    assert r["total_avaliacoes_proximas"] == 2  # eventos em 5 e 9 dias; o de 20 fica fora
    assert 0 < r["media_geral"] <= 10
    assert r["aluno_nome"] == "Arthur"
    assert [t["id"] for t in r["tarefas_recentes"]][0] == "tar-2"  # atrasada primeiro
    assert r["proximos_eventos"][0]["disciplina_nome"] == "Programação Orientada a Objetos"
    titulos = " | ".join(a["titulo"] for a in r["alertas"])
    assert "atrasada" in titulos and "Algoritmos" in titulos  # faltas 13/15 e tarefa atrasada
    assert {a["nivel"] for a in r["alertas"]} <= {"error", "warning", "info"}


def test_dashboard_sem_dados(tmp_path):
    r = DashboardService(tmp_path, hoje=lambda: HOJE).resumo()
    assert r["total_disciplinas"] == 0 and r["media_geral"] == 0.0 and r["alertas"] == []

def test_dashboard_usa_fontes_injetadas_sem_ler_json(tmp_path):
    """tmp_path está vazio: se o service lesse os JSON, o resultado seria zerado."""
    svc = DashboardService(
        tmp_path, hoje=lambda: HOJE,
        fonte_alunos=lambda: [{"nome": "Rafael Estevão"}],
        fonte_disciplinas=lambda: [{"id": "d1", "nome": "POO", "limite_faltas": 10}],
        fonte_notas=lambda: [{"disciplina_id": "d1", "nota": 4.0, "peso": 1}],
        fonte_faltas=lambda: [{"disciplina_id": "d1", "quantidade": 9}],
        fonte_eventos=lambda: [{"titulo": "Prova", "tipo": "Prova", "data": "2026-11-04",
                                "hora": "08:00", "disciplina_id": "d1"}],
    )
    r = svc.resumo()
    assert r["aluno_nome"] == "Rafael Estevão" and r["total_disciplinas"] == 1
    assert r["media_geral"] == 4.0 and r["total_avaliacoes_proximas"] == 1
    assert r["proximos_eventos"][0]["disciplina_nome"] == "POO"
    titulos = " | ".join(a["titulo"] for a in r["alertas"])
    assert "Faltas em POO" in titulos and "Média baixa: POO" in titulos