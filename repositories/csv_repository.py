"""Alias de compatibilidade: CSVRepository → JSONRepository.

O módulo de calendário foi escrito esperando um CSVRepository, mas o projeto
armazena tudo em JSON.  Esta classe simplesmente reexporta JSONRepository para
que ``from repositories.csv_repository import CSVRepository`` funcione sem
modificar o código do calendário.
"""
from repositories.json_repository import JSONRepository as CSVRepository  # noqa: F401

__all__ = ["CSVRepository"]

