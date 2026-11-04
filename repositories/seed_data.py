"""Gerador de dados iniciais (seed) para a pasta ``data/``.

Uso:
    python -m repositories.seed_data            # só cria arquivos ausentes/vazios
    python -m repositories.seed_data --force    # recria TODOS (apaga dados atuais)

As datas de eventos e tarefas são relativas a "hoje", para o dashboard sempre
mostrar compromissos próximos.

ATENÇÃO (esquema compartilhado): os campos abaixo são o contrato de dados usado
pelos templates de todos os módulos. Se alterar algum nome de campo, avise o grupo.
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Union

from repositories.json_repository import JsonRepository, get_data_dir

ARQUIVOS = ("alunos", "professores", "disciplinas", "notas", "faltas",
            "horarios", "tarefas", "eventos", "materiais")


def dados_iniciais(hoje: Optional[date] = None) -> Dict[str, Any]:
    hoje = hoje or date.today()

    def em(dias: int) -> str:
        return (hoje + timedelta(days=dias)).isoformat()

    professores = [
        {"id": "prof-ana", "nome": "Reginaldo", "email": "reginaldo@dcc.ufmg.br"},
        {"id": "prof-carlos", "nome": "Carlos Henrique Lima", "email": "carlos.lima@dcc.ufmg.br"},
        {"id": "prof-marta", "nome": "Marta Figueiredo", "email": "marta.figueiredo@mat.ufmg.br"},
    ]
    disciplinas = [
        {"id": "disc-poo", "nome": "Programação Orientada a Objetos", "codigo": "DCC025",
         "professor_id": "prof-ana", "carga_horaria": 60, "limite_faltas": 15,
         "descricao": "Classes, herança, polimorfismo e classes abstratas."},
        {"id": "disc-aed", "nome": "Algoritmos e Estruturas de Dados", "codigo": "DCC205",
         "professor_id": "prof-carlos", "carga_horaria": 60, "limite_faltas": 15,
         "descricao": "Listas, árvores, grafos e análise de complexidade."},
        {"id": "disc-calc", "nome": "Cálculo Diferencial e Integral", "codigo": "MAT001",
         "professor_id": "prof-marta", "carga_horaria": 90, "limite_faltas": 22,
         "descricao": "Limites, derivadas e integrais."},
        {"id": "disc-bd", "nome": "Banco de Dados", "codigo": "DCC011",
         "professor_id": "prof-carlos", "carga_horaria": 60, "limite_faltas": 15,
         "descricao": "Modelagem relacional e SQL."},
    ]
    return {
        "alunos": [{"id": "aluno-1", "nome": "Arthur", "curso": "Engenharia de Controle e Automação",
                    "matricula": "2026000001"}],
        "professores": professores,
        "disciplinas": disciplinas,
        "notas": [
            {"id": "nota-1", "disciplina_id": "disc-poo", "nome_avaliacao": "Prova 1", "nota": 8.5, "peso": 3},
            {"id": "nota-2", "disciplina_id": "disc-poo", "nome_avaliacao": "Trabalho Prático", "nota": 9.0, "peso": 2},
            {"id": "nota-3", "disciplina_id": "disc-aed", "nome_avaliacao": "Prova 1", "nota": 5.0, "peso": 3},
            {"id": "nota-4", "disciplina_id": "disc-calc", "nome_avaliacao": "Prova 1", "nota": 7.0, "peso": 4},
        ],
        "faltas": [
            {"id": "falta-1", "disciplina_id": "disc-poo", "quantidade": 2},
            {"id": "falta-2", "disciplina_id": "disc-aed", "quantidade": 13},
            {"id": "falta-3", "disciplina_id": "disc-calc", "quantidade": 4},
            {"id": "falta-4", "disciplina_id": "disc-bd", "quantidade": 0},
        ],
        "horarios": [
            {"id": "hor-1", "disciplina_id": "disc-poo", "dia_semana": "Segunda",
             "horario_inicio": "08:00", "horario_fim": "10:00", "sala": "Sala 4010", "bloco": "ICEx"},
            {"id": "hor-2", "disciplina_id": "disc-aed", "dia_semana": "Terça",
             "horario_inicio": "10:00", "horario_fim": "12:00", "sala": "Sala 3040", "bloco": "ICEx"},
            {"id": "hor-3", "disciplina_id": "disc-calc", "dia_semana": "Quarta",
             "horario_inicio": "08:00", "horario_fim": "10:00", "sala": "Sala 101", "bloco": "Bloco 3"},
            {"id": "hor-4", "disciplina_id": "disc-bd", "dia_semana": "Quinta",
             "horario_inicio": "14:00", "horario_fim": "16:00", "sala": "Lab 2", "bloco": "ICEx"},
        ],
        "tarefas": [
            {"id": "tar-1", "titulo": "Lista de exercícios de herança", "disciplina_id": "disc-poo",
             "prioridade": "Alta", "data_prazo": em(2), "status": "Em andamento",
             "tempo_estimado": "3 horas", "descricao": "Questões 1 a 8 sobre herança e polimorfismo."},
            {"id": "tar-2", "titulo": "Implementar árvore AVL", "disciplina_id": "disc-aed",
             "prioridade": "Urgente", "data_prazo": em(-1), "status": "Pendente",
             "tempo_estimado": "5 horas", "descricao": "Inserção, remoção e rotações."},
            {"id": "tar-3", "titulo": "Modelo entidade-relacionamento", "disciplina_id": "disc-bd",
             "prioridade": "Média", "data_prazo": em(7), "status": "Pendente",
             "tempo_estimado": "2 horas", "descricao": ""},
            {"id": "tar-4", "titulo": "Revisar anotações de Cálculo", "disciplina_id": "disc-calc",
             "prioridade": "Baixa", "data_prazo": "", "status": "Pendente",
             "tempo_estimado": "1 hora", "descricao": ""},
            {"id": "tar-5", "titulo": "Entregar relatório do projeto", "disciplina_id": "disc-poo",
             "prioridade": "Alta", "data_prazo": em(-5), "status": "Concluída",
             "tempo_estimado": "4 horas", "descricao": "Entrega 1 do UniversityOS."},
        ],
        "eventos": [
            {"id": "ev-1", "titulo": "Prova 2 de POO", "tipo": "Prova", "disciplina_id": "disc-poo",
             "data": em(5), "hora": "08:00", "local": "Sala 4010", "descricao": "Conteúdo: herança e polimorfismo."},
            {"id": "ev-2", "titulo": "Entrega do trabalho de AED", "tipo": "Trabalho", "disciplina_id": "disc-aed",
             "data": em(9), "hora": "23:59", "local": "Moodle", "descricao": ""},
            {"id": "ev-3", "titulo": "Seminário de Banco de Dados", "tipo": "Seminário", "disciplina_id": "disc-bd",
             "data": em(20), "hora": "14:00", "local": "Lab 2", "descricao": "Apresentação em grupo."},
        ],
        # materiais.json guarda só a configuração da pasta de materiais do aluno
        "materiais": {"pasta_raiz": ""},
    }


def semear(data_dir: Optional[Union[str, Path]] = None, forcar: bool = False,
           hoje: Optional[date] = None) -> Dict[str, str]:
    """Cria os arquivos JSON iniciais. Devolve {arquivo: 'criado'|'mantido'}.

    Sem ``forcar``, arquivos que já têm conteúdo NUNCA são sobrescritos.
    """
    pasta = get_data_dir(data_dir)
    pasta.mkdir(parents=True, exist_ok=True)
    iniciais = dados_iniciais(hoje)
    resultado: Dict[str, str] = {}
    for nome in ARQUIVOS:
        repo = JsonRepository(f"{nome}.json", pasta)
        vazio = (not repo.caminho.exists()) or not repo.caminho.read_text(encoding="utf-8").strip()
        if forcar or vazio:
            repo.salvar(iniciais[nome])
            resultado[f"{nome}.json"] = "criado"
        else:
            resultado[f"{nome}.json"] = "mantido"
    return resultado


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Gera os dados iniciais do UniversityOS.")
    ap.add_argument("--force", action="store_true", help="recria todos os arquivos (apaga dados atuais)")
    for arq, estado in semear(forcar=ap.parse_args().force).items():
        print(f"{arq}: {estado}")
