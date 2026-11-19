import csv
import json
import os
import subprocess
import time
from datetime import datetime

from base_conhecimento import LIMITE_MEDIA, nivel_confianca, normalizar

CAMPOS = ["data", "sessao", "origem", "pergunta", "orientacao_id", "encontrou",
          "ajudou", "tentativas", "tempo_segundos", "nota_facilidade"]

PADRAO = {"data": "", "sessao": "", "origem": "pergunta", "pergunta": "",
          "orientacao_id": None, "encontrou": False, "ajudou": False,
          "tentativas": 1, "tempo_segundos": 0.0, "nota_facilidade": None}

AVISO_INICIAL = ("Aviso: este assistente NÃO é um canal oficial e não coleta dados pessoais.\n"
                 "Não digite nome, CPF, telefone ou e-mail.")


def limpar_terminal():
    if os.name == 'nt':
        subprocess.run('cls', shell=True)
    else:
        subprocess.run(['clear'])


class Assistente:
    def __init__(self, nome, base, caminho_historico="data/historico.json",
                 caminho_csv="data/atendimentos.csv"):
        self.nome = nome
        self.base = base
        self.caminho_historico = caminho_historico
        self.caminho_csv = caminho_csv
        self.historico = []
        self.sessao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.entrada_encerrada = False
        self.carregar_historico()

    def ler_texto(self, mensagem):
        try:
            return input(mensagem).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            self.entrada_encerrada = True
            return "0"

    def pausar(self):
        self.ler_texto("\nPressione Enter para continuar...")

    def ler_opcao(self, mensagem, maximo):
        while True:
            texto = self.ler_texto(mensagem)
            if self.entrada_encerrada:
                return 0
            if texto == "":
                print("Atenção: você não digitou nada. Digite uma das opções.")
                continue
            try:
                numero = int(texto)
            except ValueError:
                print("Atenção: digite apenas o número da opção.")
                continue
            if numero < 0 or numero > maximo:
                print(f"Atenção: opção fora da faixa. Escolha de 0 a {maximo}.")
                continue
            return numero

    def ler_sim_nao(self, mensagem):
        while True:
            texto = normalizar(self.ler_texto(mensagem)).strip()
            if self.entrada_encerrada:
                return False
            if texto in ("s", "sim"):
                return True
            if texto in ("n", "nao"):
                return False
            print("Atenção: responda apenas com s (sim) ou n (não).")

    def tem_dado_pessoal(self, texto):
        if "@" in texto:
            return True
        digitos = 0
        for letra in texto:
            if letra.isdigit():
                digitos += 1
        return digitos >= 8

    def carregar_historico(self):
        self.historico = []
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            return
        except (ValueError, OSError):
            print("Aviso: historico.json ilegível. Começando com um histórico vazio.")
            return
        if not isinstance(dados, list):
            print("Aviso: historico.json com formato inesperado. Começando vazio.")
            return
        for item in dados:
            if isinstance(item, dict):
                atendimento = dict(PADRAO)
                atendimento.update(item)
                self.historico.append(atendimento)

    def salvar_historico(self):
        try:
            pasta = os.path.dirname(self.caminho_historico)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            with open(self.caminho_historico, "w", encoding="utf-8") as arquivo:
                json.dump(self.historico, arquivo, ensure_ascii=False, indent=2)
        except OSError:
            print("Aviso: não consegui salvar o historico.json.")

    def registrar(self, origem, pergunta, orientacao_id, encontrou, ajudou, tentativas, tempo):
        atendimento = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sessao": self.sessao,
            "origem": origem,
            "pergunta": pergunta,
            "orientacao_id": orientacao_id,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": tempo,
            "nota_facilidade": None,
        }
        self.historico.append(atendimento)
        self.salvar_historico()

    def perguntar(self):
        if len(self.base.orientacoes) == 0:
            print("\nA base de conhecimento não está disponível no momento.")
            self.pausar()
            return

        limpar_terminal()
        inicio = time.time()
        tentativas = 0
        primeira_pergunta = ""
        achou = False
        ultima_orientacao = None

        while True:
            texto = self.ler_texto("\nDigite sua dúvida (0 para voltar): ")

            if texto == "":
                print("Atenção: a pergunta está vazia. Digite sua dúvida ou 0 para voltar.")
                continue

            if texto == "0":
                if tentativas > 0:
                    tempo = round(time.time() - inicio, 1)
                    self.registrar("pergunta", primeira_pergunta, ultima_orientacao,
                                   achou, False, tentativas, tempo)
                return

            if self.tem_dado_pessoal(texto):
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                continue

            tentativas += 1
            if tentativas == 1:
                primeira_pergunta = texto

            resultados = self.base.buscar(texto)
            if len(resultados) == 0 or resultados[0][0] < LIMITE_MEDIA:
                self.mostrar_nao_encontrei()
                continue

            achou = True
            pontos, melhor = resultados[0]
            ultima_orientacao = melhor.id
            print(f"\nConfiança da resposta: {nivel_confianca(pontos)} ({pontos} pontos)\n")
            melhor.exibir()
            self.mostrar_alternativas(resultados[1:3])

            ajudou = self.ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
            if ajudou:
                tempo = round(time.time() - inicio, 1)
                self.registrar("pergunta", primeira_pergunta, melhor.id,
                               True, True, tentativas, tempo)
                inicio = time.time()
                tentativas = 0
                primeira_pergunta = ""
                achou = False
                ultima_orientacao = None
                limpar_terminal()
            else:
                limpar_terminal()
                print("Tudo bem. Tente escrever a dúvida com outras palavras (ou digite 0 para voltar).")

    def mostrar_nao_encontrei(self):
        print("\nNão encontrei uma orientação para essa dúvida.")
        print("Tente outras palavras, por exemplo: gripe, covid, tétano, hepatite, pneumonia.")
        print("Ou volte ao menu e use a opção 2 para ver as categorias.")

    def mostrar_alternativas(self, alternativas):
        uteis = []
        for pontos, orientacao in alternativas:
            if pontos >= LIMITE_MEDIA:
                uteis.append(orientacao)
        if len(uteis) > 0:
            print("\nOutras orientações que podem ajudar:")
            for orientacao in uteis:
                print(f"  - {orientacao.titulo} [{orientacao.categoria}]")

    def navegar(self):
        if len(self.base.orientacoes) == 0:
            print("\nA base de conhecimento não está disponível no momento.")
            self.pausar()
            return
        categorias = self.base.categorias()
        while True:
            limpar_terminal()
            print("=== Categorias ===")
            for numero, categoria in enumerate(categorias, start=1):
                print(f"{numero} - {categoria}")
            print("0 - Voltar")
            opcao = self.ler_opcao("Escolha uma categoria: ", len(categorias))
            if opcao == 0:
                return
            self.navegar_categoria(categorias[opcao - 1])

    def navegar_categoria(self, categoria):
        orientacoes = self.base.por_categoria(categoria)
        while True:
            limpar_terminal()
            inicio = time.time()
            print(f"=== {categoria} ===")
            for numero, orientacao in enumerate(orientacoes, start=1):
                print(f"{numero} - {orientacao.titulo}")
            print("0 - Voltar")
            opcao = self.ler_opcao("Escolha uma orientação: ", len(orientacoes))
            if opcao == 0:
                return
            escolhida = orientacoes[opcao - 1]
            print()
            escolhida.exibir()
            ajudou = self.ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
            tempo = round(time.time() - inicio, 1)
            self.registrar("categoria", f"{categoria} > {escolhida.titulo}",
                           escolhida.id, True, ajudou, 1, tempo)

    def indicadores(self):
        total = len(self.historico)
        if total == 0:
            return None

        encontrados = 0
        ajudaram = 0
        soma_tentativas = 0
        soma_tempo = 0.0
        notas_por_sessao = {}
        sem_solucao = []

        for atendimento in self.historico:
            soma_tentativas += atendimento["tentativas"]
            if atendimento["encontrou"]:
                encontrados += 1
                soma_tempo += atendimento["tempo_segundos"]
            if atendimento["ajudou"]:
                ajudaram += 1
            else:
                if atendimento["pergunta"] not in sem_solucao:
                    sem_solucao.append(atendimento["pergunta"])
            if atendimento["nota_facilidade"] is not None:
                notas_por_sessao[atendimento["sessao"]] = atendimento["nota_facilidade"]

        resultado = {
            "total": total,
            "encontrada_pct": round(encontrados / total * 100, 1),
            "ajudou_pct": round(ajudaram / total * 100, 1),
            "tempo_medio": None,
            "tentativas_media": round(soma_tentativas / total, 1),
            "facilidade": None,
            "avaliacoes": len(notas_por_sessao),
            "sem_solucao": sem_solucao,
        }
        if encontrados > 0:
            resultado["tempo_medio"] = round(soma_tempo / encontrados, 1)
        if len(notas_por_sessao) > 0:
            resultado["facilidade"] = round(sum(notas_por_sessao.values()) / len(notas_por_sessao), 1)
        return resultado

    def exibir_indicadores(self):
        dados = self.indicadores()
        print("\n=== Indicadores ===")
        if dados is None:
            print("Ainda não há atendimentos registrados.")
            return
        print(f"Total de atendimentos: {dados['total']}")
        print(f"Resposta encontrada (%): {dados['encontrada_pct']}")
        print(f"Taxa de acerto: ajudou (%): {dados['ajudou_pct']}")
        if dados["tempo_medio"] is None:
            print("Tempo médio para encontrar: sem dados")
        else:
            print(f"Tempo médio para encontrar: {dados['tempo_medio']} s")
        print(f"Tentativas por atendimento: {dados['tentativas_media']}")
        if dados["facilidade"] is None:
            print("Facilidade de uso (1 a 5): sem avaliações")
        else:
            print(f"Facilidade de uso (1 a 5): {dados['facilidade']} ({dados['avaliacoes']} avaliação(ões))")
        print("Dúvidas sem solução:")
        if len(dados["sem_solucao"]) == 0:
            print("  (nenhuma)")
        for pergunta in dados["sem_solucao"]:
            print(f"  - {pergunta}")

    def exportar_csv(self):
        if len(self.historico) == 0:
            print("\nNão há atendimentos para exportar.")
            return
        try:
            pasta = os.path.dirname(self.caminho_csv)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            with open(self.caminho_csv, "w", newline="", encoding="utf-8-sig") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS)
                escritor.writeheader()
                for atendimento in self.historico:
                    escritor.writerow({campo: atendimento.get(campo) for campo in CAMPOS})
            print(f"\n{len(self.historico)} atendimento(s) exportado(s) para {self.caminho_csv}")
        except OSError:
            print("\nNão consegui gravar o CSV. Se ele estiver aberto em outro programa, feche-o e tente de novo.")

    def pedir_nota(self):
        atendimentos_da_sessao = []
        for atendimento in self.historico:
            if atendimento["sessao"] == self.sessao:
                atendimentos_da_sessao.append(atendimento)
        if len(atendimentos_da_sessao) == 0 or self.entrada_encerrada:
            return

        limpar_terminal()
        print("Antes de sair: de 1 a 5, quão fácil foi usar o assistente? (0 para pular)")
        nota = self.ler_opcao("Sua nota: ", 5)
        if nota == 0:
            return
        for atendimento in atendimentos_da_sessao:
            atendimento["nota_facilidade"] = nota
        self.salvar_historico()

    def mostrar_menu(self):
        limpar_terminal()
        print(f"=== {self.nome} ===")
        print("Orientações sobre vacinação para pessoas com 60 anos ou mais.")
        print(AVISO_INICIAL)
        if len(self.base.orientacoes) == 0:
            print("\nAviso: a base de conhecimento não foi carregada.")
        print("\n=== Menu principal ===")
        print("1 - Digitar minha dúvida")
        print("2 - Navegar por categorias")
        print("3 - Ver indicadores")
        print("4 - Exportar atendimentos para CSV")
        print("0 - Sair")

    def iniciar(self):
        while True:
            self.mostrar_menu()
            opcao = self.ler_opcao("Escolha uma opção: ", 4)

            if opcao == 1:
                self.perguntar()
            elif opcao == 2:
                self.navegar()
            elif opcao == 3:
                self.exibir_indicadores()
                self.pausar()
            elif opcao == 4:
                self.exportar_csv()
                self.pausar()
            else:
                break

        self.pedir_nota()
        self.exportar_csv()
        print("\nObrigado por usar o assistente. Cuide da sua saúde!")