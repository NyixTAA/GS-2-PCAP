import json

from orientacao import Orientacao

PONTOS_PALAVRA_CHAVE = 3
PONTOS_TITULO = 1
LIMITE_ALTA = 6
LIMITE_MEDIA = 3

PALAVRAS_COMUNS = ["como", "para", "qual", "quais", "onde", "quando", "posso",
                   "pode", "quero", "preciso", "tenho", "fazer", "faco", "isso",
                   "esse", "essa", "deve", "tomar"]

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ü": "u", "ç": "c"}


def normalizar(texto):
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()-/\"'":
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


def nivel_confianca(pontos):
    if pontos >= LIMITE_ALTA:
        return "ALTA"
    if pontos >= LIMITE_MEDIA:
        return "MÉDIA"
    return None


class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []

    def carregar(self):
        self.orientacoes = []
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            print(f"Aviso: arquivo '{self.caminho}' não encontrado.")
            return False
        except (ValueError, OSError):
            print(f"Aviso: não foi possível ler '{self.caminho}' (arquivo corrompido?).")
            return False

        if not isinstance(dados, list):
            print("Aviso: o JSON da base deve ser uma lista de orientações.")
            return False

        ignorados = 0
        for registro in dados:
            valido, motivo = Orientacao.registro_valido(registro)
            if valido:
                self.orientacoes.append(Orientacao.de_dicionario(registro))
            else:
                ignorados += 1
                print(f"Aviso: registro ignorado ({motivo}).")

        if ignorados > 0:
            print(f"Aviso: {ignorados} registro(s) inválido(s) ignorado(s).")
        if len(self.orientacoes) == 0:
            print("Aviso: a base de conhecimento está vazia.")
            return False
        return True

    def categorias(self):
        lista = []
        for orientacao in self.orientacoes:
            if orientacao.categoria not in lista:
                lista.append(orientacao.categoria)
        return lista

    def por_categoria(self, categoria):
        resultado = []
        for orientacao in self.orientacoes:
            if orientacao.categoria == categoria:
                resultado.append(orientacao)
        return resultado

    def pontuar(self, pergunta_normalizada, orientacao):
        pontos = 0

        for palavra_chave in orientacao.palavras_chave:
            if normalizar(palavra_chave) in pergunta_normalizada:
                pontos += PONTOS_PALAVRA_CHAVE

        titulo = normalizar(orientacao.titulo)
        palavras_vistas = []
        for palavra in pergunta_normalizada.split():
            if len(palavra) >= 4 and palavra not in PALAVRAS_COMUNS and palavra not in palavras_vistas:
                palavras_vistas.append(palavra)
                if " " + palavra + " " in titulo:
                    pontos += PONTOS_TITULO
        return pontos

    def buscar(self, pergunta):
        pergunta_normalizada = normalizar(pergunta)
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta_normalizada, orientacao)
            if pontos > 0:
                resultados.append((pontos, orientacao))
        resultados.sort(key=lambda tupla: (-tupla[0], tupla[1].id))
        return resultados