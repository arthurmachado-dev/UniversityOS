# UniversityOS

Organizador acadêmico web (Flask + JSON) — UFMG / DCC — Programação Orientada a Objetos.
Reúne disciplinas, horários, faltas, notas, tarefas, calendário e materiais de estudo.

## Como executar

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py                    # abre em http://127.0.0.1:5000
```

Na primeira execução, os arquivos de `data/` que estiverem ausentes ou vazios são
criados com dados de exemplo (para facilitar a avaliação do programa). **Dados já existentes nunca são sobrescritos.**
Para recriar tudo do zero (apaga seus dados): `python -m repositories.seed_data --force`.

Variáveis opcionais: `PORT` (padrão 5000), `FLASK_DEBUG=1`, `UNIVERSITYOS_DATA_DIR` (pasta dos JSON).

> O servidor escuta apenas em `127.0.0.1` de propósito: a aba **Materiais** abre
> arquivos do seu computador, então não deve ficar acessível pela rede.

## Testes

```bash
python -m pytest -q
```

Os testes usam uma pasta temporária; não tocam nos seus dados em `data/`.

## Estrutura

```
app.py              fábrica create_app() e ponto de entrada
models/             classes de domínio (Tarefa, Material, ...)
repositories/       json_repository.py (CRUD genérico) e seed_data.py (dados iniciais)
services/           regras de negócio (um service por módulo + dashboard)
routes/             Blueprints: pages.py (HTML) e api_*.py (JSON)
templates/ static/  interface (HTML + Tailwind via CDN, JS)
data/               banco em arquivos JSON
tests/              pytest (unitários + rotas)
```

Fluxo de uma requisição: `routes` → `services` (regras) → `repositories` (JSON).

### Contrato para os módulos dos outros integrantes

* Cada arquivo `routes/api_*.py` deve expor um `Blueprint` chamado **`bp`**; o `app.py`
  o registra automaticamente (módulos ainda inexistentes são ignorados com um aviso no log).
* Pegue a pasta de dados com `current_app.config["DATA_DIR"]` e use
  `JsonRepository("arquivo.json", data_dir)` — assim os testes conseguem isolar os dados.
* Erros devem voltar como `{"error": "mensagem"}` com status HTTP adequado (400/404).
* O esquema dos JSON está em `repositories/seed_data.py` (é o contrato usado pelos templates).

## API implementada neste módulo

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/dashboard` | Resumo da página inicial (métricas, alertas, tarefas e eventos próximos) |
| GET / POST | `/api/tarefas` | Lista (ordenada por prazo) / cria |
| GET / PUT / PATCH / DELETE | `/api/tarefas/<id>` | Obtém / atualiza parcialmente / remove |
| GET | `/api/materiais/scan` | Lê a pasta de materiais configurada, agrupando por subpasta |
| POST | `/api/materiais/config` | `{"caminho": "..."}` define a pasta raiz |
| POST | `/api/materiais/abrir` · `/revelar` | Abre arquivo / mostra pasta no computador |
| GET | `/api/materiais/download?caminho=...` | Baixa um arquivo da pasta de materiais |

**Tarefas:** prioridades `Baixa, Média, Alta, Urgente`; status gravados `Pendente, Em andamento, Concluída`.
`Atrasada` é calculado na leitura (prazo vencido e não concluída) e não pode ser gravado.

**Materiais — segurança:** só arquivos dentro da pasta configurada podem ser abertos/baixados
(proteção contra `..`), e executáveis/scripts (`.exe`, `.bat`, `.sh`, `.ps1`...) nunca são abertos.

## Regras de negócio (relatório, seção 5.1)

Nota final = soma das notas; frequência < 75% → Reprovado por Falta; ≥ 60 → Aprovado;
40–59 → Recuperação; abaixo disso → Reprovado por Nota.
