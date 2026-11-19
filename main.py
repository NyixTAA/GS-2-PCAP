import os
import sys

from base_conhecimento import BaseConhecimento
from assistente import Assistente


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    pasta = os.path.dirname(os.path.abspath(__file__))
    caminho_base = os.path.join(pasta, "data", "base_conhecimento.json")
    caminho_historico = os.path.join(pasta, "data", "historico.json")
    caminho_csv = os.path.join(pasta, "data", "atendimentos.csv")

    base = BaseConhecimento(caminho_base)
    base.carregar()

    assistente = Assistente("Citizen Assist AI", base, caminho_historico, caminho_csv)
    assistente.iniciar()


if __name__ == "__main__":
    main()