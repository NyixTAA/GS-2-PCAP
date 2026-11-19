AVISO = "este assistente NÃO é um canal oficial. Para o seu caso, confirme na UBS."

CAMPOS_OBRIGATORIOS = {
    "id": int,
    "categoria": str,
    "titulo": str,
    "palavras_chave": list,
    "resposta": str,
    "documentos": list,
    "onde": str,
    "fonte": str,
    "verificado_em": str,
}


class Orientacao:
    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave
        self.resposta = resposta
        self.documentos = documentos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    @staticmethod
    def registro_valido(registro):
        if not isinstance(registro, dict):
            return False, "o registro não é um dicionário"
        for campo, tipo in CAMPOS_OBRIGATORIOS.items():
            if campo not in registro:
                return False, f"falta o campo '{campo}'"
            if not isinstance(registro[campo], tipo):
                return False, f"o campo '{campo}' tem o tipo errado"
        if len(registro["palavras_chave"]) == 0:
            return False, "o campo 'palavras_chave' está vazio"
        return True, ""

    @classmethod
    def de_dicionario(cls, registro):
        return cls(
            registro["id"],
            registro["categoria"],
            registro["titulo"],
            registro["palavras_chave"],
            registro["resposta"],
            registro["documentos"],
            registro["onde"],
            registro["fonte"],
            registro["verificado_em"],
        )

    def exibir(self):
        print(f">> {self.titulo}  [{self.categoria}]")
        print(self.resposta)
        print("Documentos necessários:")
        for documento in self.documentos:
            print(f"  - {documento}")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print(f"Aviso: {AVISO}")