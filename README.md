# Citizen Assist AI — Vacinação para pessoas idosas (60+)

Assistente de terminal, feito em Python, que responde dúvidas sobre **vacinação de pessoas com 60 anos ou mais** usando apenas uma base de conhecimento verificada (arquivo JSON). Toda resposta mostra a **fonte**, a **data de verificação** e o aviso de que o assistente **não é um canal oficial**. O assistente **não coleta dados pessoais**.

> Global Solution 2 — Pensamento Computacional e Automação com Python (desafio CitizenTech)

## Integrantes

Lucas Galle Melchior - RM: 574027<br>
Davi Ramos Silva - RM: 571744

## Público e problema

- **Público:** pessoas idosas (60 anos ou mais), suas famílias e cuidadores.
- **Problema:** a informação sobre quais vacinas tomar, quando e onde existe, mas está espalhada em calendários técnicos, notícias e páginas que nem sempre são oficiais. O assistente reúne as orientações do Ministério da Saúde em linguagem simples.

## ODS relacionados

- **ODS 3 — Saúde e Bem-Estar:** estimula a vacinação e a prevenção de doenças graves na terceira idade.
- **ODS 10 — Redução das Desigualdades:** informação clara e gratuita para quem tem menos acesso a canais digitais.
- **ODS 16 — Paz, Justiça e Instituições Eficazes:** acesso público à informação, com fonte e data sempre visíveis.

## Como executar

Requisitos: Python 3.8 ou superior.

```bash
git clone <link-do-repositorio>
cd citizen-assist-ai
python main.py
```

Menu principal: `1` digitar dúvida · `2` navegar por categorias · `3` indicadores · `4` exportar CSV · `0` sair (pede a nota de facilidade de 1 a 5 e exporta o CSV).

## Estrutura

```
citizen-assist-ai/
├── README.md
├── main.py                  # ponto de entrada
├── orientacao.py            # classe Orientacao
├── base_conhecimento.py     # classe BaseConhecimento (+ normalizar e pontuação)
├── assistente.py            # classe Assistente
└── data/
    ├── base_conhecimento.json   # 14 orientações, 3 categorias
    ├── historico.json           # atendimentos registrados
    └── atendimentos.csv         # exportação (gerada pelo programa)
```

Composição: `Assistente` => `base: BaseConhecimento` => `orientacoes: [Orientacao, ...]`.

## Regra de pontuação usada

A pergunta e os textos da base são normalizados (minúsculas, sem acentos, sem pontuação) e cada orientação recebe pontos:

| Regra | Pontos |
|-------|--------|
| Palavra-chave da orientação que aparece na pergunta | +3 |
| Palavra da pergunta (4 letras ou mais) que aparece no título | +1 |

| Melhor pontuação | Resultado |
|------------------|-----------|
| 6 ou mais | Confiança **ALTA** |
| 3 a 5 | Confiança **MÉDIA** |
| menos de 3 | "Não encontrei": sugere outras palavras ou as categorias |

`buscar()` devolve uma lista de tuplas `(pontos, orientacao)` da maior para a menor pontuação. O assistente mostra a melhor orientação e até duas alternativas.

**Exemplo:** "Como faço a vacina da gripe?" => `vacina da gripe` (+3), `gripe` (+3), "vacina" no título (+1), "gripe" no título (+1) = **8 pontos, confiança ALTA**.

**Ajustes feitos em relação à regra básica:**
- A palavra-chave só vale se aparecer como palavra inteira (ex.: `sus` não casa dentro de outra palavra).
- Palavras muito comuns ("como", "para", "quais", "posso"...) não ganham ponto de título.
- Cada palavra da pergunta conta no máximo 1 ponto de título.
- Alternativas só aparecem se tiverem pelo menos 3 pontos.
- Em caso de empate, vem primeiro a orientação de menor `id`.

## Regras de atendimento

- Entradas inválidas (letras, vazio, número fora da faixa, s/n inválido) nunca encerram o programa.
- Pergunta com **8 ou mais dígitos** ou com **@** é recusada e **não é registrada**.
- JSON ausente ou corrompido não trava o programa (a base ou o histórico são tratados com aviso).
- Cada atendimento é salvo em `data/historico.json`: data, sessão, origem (pergunta ou categoria), pergunta, id da orientação, se encontrou, se ajudou, tentativas, tempo em segundos e nota de facilidade.
- Um atendimento termina quando a pessoa responde **s** ("ajudou") ou desiste (**0**). Reescrever a dúvida após um **n** conta como nova tentativa do mesmo atendimento.

## Indicadores

Resposta encontrada (%) · Taxa de acerto: ajudou (%) · Tempo médio para encontrar · Tentativas por atendimento · Facilidade de uso (1 a 5) · Lista de dúvidas sem solução.

## Fontes consultadas

Todas as orientações foram conferidas em fontes do Ministério da Saúde (gov.br) em **18/11/2026**:

- Calendário Técnico Nacional de Vacinação do Idoso — https://www.gov.br/saude/pt-br/composicao/svsa/pni/calendario-tecnico/calendario-tecnico-nacional-de-vacinacao-idoso
- Calendário de Vacinação — https://www.gov.br/saude/pt-br/vacinacao
- Campanha Nacional de Vacinação contra a Influenza 2026 — https://www.gov.br/saude/pt-br/assuntos/noticias/2026/marco/dia-d-campanha-nacional-de-vacinacao-contra-a-influenza-comeca-neste-sabado-28
- Pneumo 20 para pessoas com 85 anos ou mais — https://www.gov.br/saude/pt-br/assuntos/noticias-ms/2026/setembro/nova-vacina-para-idosos-ministerio-da-saude-vai-ofertar-pneumo20-para-quem-tem-mais-de-85-anos
- Carteira de vacinação pelo Meu SUS Digital — https://www.gov.br/saude/pt-br/assuntos/noticias-ms/2026/outubro/quer-consultar-suas-vacinas-saiba-como-acessar-a-carteira-de-vacinacao-pelo-meu-sus-digital

## Limitações

- A base cobre só vacinação para 60+ e reflete o calendário nacional conferido em 18/11/2026. Calendários, campanhas e regras mudam; cada UBS ou município pode ter regras próprias.
- A busca é por regras (palavras-chave): não entende sinônimos, erros de digitação ou frases muito diferentes das palavras-chave cadastradas.
- O bloqueio de dados pessoais só detecta 8 ou mais dígitos e "@". Um nome digitado sem números passaria.
- O assistente não substitui orientação médica nem a avaliação da equipe da UBS.
- Vacinas que não fazem parte da rotina do SUS para idosos em geral (por exemplo, as oferecidas só em clínicas particulares) não estão na base.

# Teste com usuários

## Procedimento
- Público do Citizen Assist AI: pessoas idosas (60+), familiares e cuidadores.
- Foram 3 participantes anônimos (P1, P2 e P3), com 4 atendimentos cada: 12 atendimentos iniciais.
- Após a análise, foi executada uma melhoria na orientação de ID 13 e um reteste adicional.
- Nenhum nome, CPF, telefone ou e-mail foi incluído.

## Indicadores dos 12 atendimentos iniciais

| Indicador | Resultado |
|---|---|
| Atendimentos | 12 |
| Participantes | 3 |
| Resposta encontrada | 75.0% |
| Taxa de acerto — ajudou | 58.3% |
| Tempo médio para encontrar (apenas encontrados) | 26.6 s |
| Tentativas por atendimento | 1.0 |
| Facilidade média (1 a 5) | 4.3 |

## Dúvidas sem solução no teste inicial
- Como completar as doses da hepatite B?<br>- Existe vacinação em casa para quem não consegue sair?<br>- Como vejo o comprovante das vacinas?<br>- Idoso pode tomar vacina contra herpes zoster pelo SUS?<br>- Tem vacina contra dengue para pessoas idosas?<br>

## Melhoria aplicada
Na orientação de ID 13 — **Ver minha carteira de vacinação no celular** — foi acrescentada a palavra-chave `comprovante das vacinas`. A dúvida “Como vejo o comprovante das vacinas?” não foi encontrada na rodada inicial. Após a inclusão da palavra-chave, o reteste retornou a orientação de ID 13 e foi marcado como útil.

## Resultado após o reteste
- Atendimentos iniciais: 12.
- Reteste adicional: 1.
- Total simulado com reteste: 13.
- Resposta encontrada: 76.9%.
- Taxa de acerto — ajudou: 61.5%.
- Tempo médio para encontrar: 25.8 s.
- Facilidade média: 4.3/5.

## Arquivos
- `data/historico.json`: 12 atendimentos simulados + 1 reteste.
- `data/atendimentos.csv`: exportação dos mesmos registros.
- `alteracoes/palavras_chave_id13.json`: fragmento da melhoria proposta.
- `evidencias/relatorio_indicadores.json`: indicadores calculados.
- `evidencias/casos_de_teste.csv`: resumo dos casos simulados.
