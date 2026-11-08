"""Testes de integração das rotas Flask (Tarefas, Materiais, Dashboard e páginas)."""
import pytest


# ------------------------------------------------------------------- tarefas
def test_listar_tarefas(client):
    r = client.get("/api/tarefas")
    assert r.status_code == 200
    tarefas = r.get_json()
    assert len(tarefas) >= 5
    assert {"id", "titulo", "prioridade", "status", "data_prazo", "disciplina_nome",
            "tempo_estimado", "descricao"} <= set(tarefas[0])


def test_criar_tarefa_como_o_front_envia(client):
    payload = {"titulo": "Exercício de POO", "disciplina_id": "", "prioridade": "Média",
               "data_prazo": "", "status": "Pendente", "tempo_estimado": "2 horas", "descricao": ""}
    r = client.post("/api/tarefas", json=payload)
    assert r.status_code == 201
    assert r.get_json()["disciplina_nome"] == "Geral"
    assert any(t["titulo"] == "Exercício de POO" for t in client.get("/api/tarefas").get_json())


@pytest.mark.parametrize("payload", [
    {"titulo": ""}, {"titulo": "x", "prioridade": "Zzz"}, {"titulo": "x", "data_prazo": "amanhã"},
    {"titulo": "x", "disciplina_id": "nao-existe"}, {"titulo": "x", "status": "Atrasada"},
])
def test_criar_tarefa_invalida(client, payload):
    r = client.post("/api/tarefas", json=payload)
    assert r.status_code == 400 and "error" in r.get_json()


def test_criar_sem_json(client):
    assert client.post("/api/tarefas", data="oi").status_code == 400


def test_put_status_e_delete(client):
    tid = client.get("/api/tarefas").get_json()[0]["id"]
    r = client.put(f"/api/tarefas/{tid}", json={"status": "Concluída"})
    assert r.status_code == 200 and r.get_json()["status"] == "Concluída"
    assert client.patch(f"/api/tarefas/{tid}", json={"status": "Pendente"}).status_code == 200
    assert client.delete(f"/api/tarefas/{tid}").status_code == 200
    assert client.delete(f"/api/tarefas/{tid}").status_code == 404
    assert client.put("/api/tarefas/inexistente", json={"status": "Pendente"}).status_code == 404


# ----------------------------------------------------------------- dashboard
def test_dashboard_contrato_com_o_front(client):
    r = client.get("/api/dashboard")
    assert r.status_code == 200
    d = r.get_json()
    assert {"total_disciplinas", "total_tarefas_pendentes", "total_avaliacoes_proximas",
            "media_geral", "alertas", "tarefas_recentes", "proximos_eventos"} <= set(d)
    assert {"id", "titulo", "disciplina_nome", "data_prazo", "prioridade"} <= set(d["tarefas_recentes"][0])
    assert {"titulo", "disciplina_nome", "data", "hora", "tipo"} <= set(d["proximos_eventos"][0])


def test_concluir_tarefa_pelo_dashboard_atualiza_contador(client):
    antes = client.get("/api/dashboard").get_json()
    tid = antes["tarefas_recentes"][0]["id"]
    client.put(f"/api/tarefas/{tid}", json={"status": "Concluída"})
    depois = client.get("/api/dashboard").get_json()
    assert depois["total_tarefas_pendentes"] == antes["total_tarefas_pendentes"] - 1


# ------------------------------------------------------------------ materiais
@pytest.fixture()
def pasta(tmp_path):
    raiz = tmp_path / "Mat"
    (raiz / "POO").mkdir(parents=True)
    (raiz / "POO" / "slides.txt").write_text("conteudo")
    (tmp_path / "fora.txt").write_text("segredo")
    return raiz


def test_scan_sem_config_devolve_erro_legivel(client):
    r = client.get("/api/materiais/scan")
    assert r.status_code == 404 and r.get_json()["error"]


def test_fluxo_materiais(client, app, pasta):
    abertos = []
    app.config["MATERIAL_ABRIDOR"] = lambda p, rev: abertos.append((p.name, rev))

    assert client.post("/api/materiais/config", json={"caminho": str(pasta / "x")}).status_code == 404
    assert client.post("/api/materiais/config", json={"caminho": str(pasta)}).status_code == 200

    scan = client.get("/api/materiais/scan").get_json()
    arq = scan["subpastas"][0]["arquivos"][0]
    assert scan["subpastas"][0]["nome_pasta"] == "POO" and arq["nome"] == "slides.txt"

    assert client.post("/api/materiais/abrir", json={"caminho": arq["caminho"]}).status_code == 200
    assert client.post("/api/materiais/revelar", json={"caminho": scan["subpastas"][0]["caminho_pasta"]}).status_code == 200
    assert abertos == [("slides.txt", False), ("POO", True)]

    dl = client.get("/api/materiais/download", query_string={"caminho": arq["caminho"], "download": "true"})
    assert dl.status_code == 200 and dl.data == b"conteudo"
    assert "attachment" in dl.headers["Content-Disposition"]


def test_materiais_bloqueia_acesso_fora_da_pasta(client, app, pasta, tmp_path):
    app.config["MATERIAL_ABRIDOR"] = lambda p, rev: pytest.fail("não deveria abrir")
    client.post("/api/materiais/config", json={"caminho": str(pasta)})
    fora = str(tmp_path / "fora.txt")
    assert client.get("/api/materiais/download", query_string={"caminho": fora}).status_code == 403
    assert client.post("/api/materiais/abrir", json={"caminho": fora}).status_code == 403
    assert client.get("/api/materiais/download",
                      query_string={"caminho": str(pasta / ".." / "fora.txt")}).status_code == 403
    assert client.post("/api/materiais/abrir", json={}).status_code == 400


# --------------------------------------------------------------------- páginas
@pytest.mark.parametrize("rota", ["/", "/tarefas", "/materiais"])
def test_paginas_renderizam_com_base(client, rota):
    r = client.get(rota)
    assert r.status_code == 200
    assert b"University OS" in r.data and b"modal-faltei-hoje" in r.data


def test_rota_inexistente_devolve_404_json(client):
    r = client.get("/api/nao-existe")
    assert r.status_code == 404 and r.get_json()["error"]
