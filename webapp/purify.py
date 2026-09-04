"""
MarkItDown Web — purificação de conteúdo convertido, pra RAG.

Remove boilerplate editorial formulaico (ISBN, direitos autorais, ficha
catalográfica, depósito legal) e lixo de OCR (blocos de linhas curtas e
isoladas sem sentido, tipicamente de capas estilizadas) do markdown
gerado pelos três pontos de conversão do projeto (`app.py`, `watch.py`,
`ocr_batch.py`) — todos importam `purify_markdown` daqui, sem duplicar
lógica.

Uso:
    from purify import purify_markdown
    texto_limpo, stats = purify_markdown(texto)
"""

import re

try:
    from spellchecker import SpellChecker

    # Dicionarios pt/en vem empacotados localmente no proprio pacote
    # (spellchecker/resources/*.json.gz) - nao baixa nada da rede.
    # Combina pt+en (nao so' pt): livros tecnicos/financeiros em portugues
    # usam muito termo em ingles sem traducao (swap, hedge, bond, yield,
    # duration...) - so' pt sozinho classificava esses termos legitimos
    # como lixo de OCR (validado com o material real do InvestBot, ver
    # relatorio da Ordem 10).
    _SPELL_PT = SpellChecker(language="pt")
    _SPELL_EN = SpellChecker(language="en")
except Exception:  # noqa: BLE001 - sem dicionario, so pula a camada de lixo de OCR
    _SPELL_PT = None
    _SPELL_EN = None

# --- Constantes ajustaveis (nao hardcoded no meio da logica) ---
GARBAGE_MAX_LINE_LENGTH = 40
GARBAGE_MIN_RECOGNIZED_RATIO = 0.5  # < 50% de palavras reconhecidas = remove a linha

_WORD_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]+")

# --- Camada 2: boilerplate por padrao de texto (so padroes universais,
# nao tenta cobrir endereco/telefone de editora - formato varia demais) ---
_BOILERPLATE_PATTERNS = [
    re.compile(r"(?im)^ISBN[\s:\-]*[\d\-Xx]+\s*$"),
    re.compile(r"(?ims)^TODOS OS DIREITOS RESERVADOS.*?(?=\n[ \t]*\n|\Z)"),
    re.compile(r"(?im)^Dados Internacionais de Cataloga[cç][aã]o na Publica[cç][aã]o.*$"),
    re.compile(r"(?im)^CDD[\s\-]*[\d.]+\s*$"),
    re.compile(r"(?im)^CDU[\s\-]*[\d.]+\s*$"),
    re.compile(r"(?ims)^Dep[oó]sito legal na Biblioteca Nacional.*?(?=\n[ \t]*\n|\Z)"),
    re.compile(r"(?im)^[©\u00a9]\s*\d{4}\s+by\s+.*$"),
]


def _normalize_whitespace(text: str) -> str:
    text = text.replace("\f", "")
    text = re.sub(r"[ \t]+(?=\n)", "", text)  # espaco a direita antes de quebra de linha
    text = re.sub(r"\n{3,}", "\n\n", text)  # colapsa 3+ quebras de linha em 2
    return text


def _remove_boilerplate(text: str) -> tuple[str, int]:
    removed = 0

    def _strip(match: re.Match) -> str:
        nonlocal removed
        removed += match.group(0).count("\n") + 1
        return ""

    for pattern in _BOILERPLATE_PATTERNS:
        text = pattern.sub(_strip, text)
    return text, removed


def _is_garbage_line(line: str) -> bool:
    """Linha e' descartada se menos de GARBAGE_MIN_RECOGNIZED_RATIO das
    palavras forem reconhecidas no dicionario (pt ou en). Linha sem
    nenhuma palavra alfabetica (so numero/pontuacao), ou com qualquer
    digito, nunca e' considerada lixo aqui - digito e' forte indicio de
    entrada de sumario/indice/nota de rodape (numero de pagina), nao de
    lixo de capa estilizada."""
    if any(ch.isdigit() for ch in line):
        return False
    words = _WORD_RE.findall(line)
    if not words:
        return False
    lower_words = [w.lower() for w in words]
    recognized = len(_SPELL_PT.known(lower_words) | _SPELL_EN.known(lower_words))
    return (recognized / len(words)) < GARBAGE_MIN_RECOGNIZED_RATIO


def _remove_ocr_garbage(text: str) -> tuple[str, int]:
    """Candidatas: blocos de linhas nao-vazias consecutivas, cercados por
    linha em branco (ou borda do texto) antes e depois, com toda linha do
    bloco abaixo de GARBAGE_MAX_LINE_LENGTH caracteres. Dentro de um bloco
    candidato, cada linha e' avaliada individualmente pelo dicionario."""
    if _SPELL_PT is None:
        return text, 0

    lines = text.split("\n")
    n = len(lines)
    removed = 0
    out: list[str] = []
    i = 0
    while i < n:
        if lines[i].strip() == "":
            out.append(lines[i])
            i += 1
            continue

        prev_is_boundary = i == 0 or lines[i - 1].strip() == ""
        if not prev_is_boundary:
            out.append(lines[i])
            i += 1
            continue

        block_start = i
        while i < n and lines[i].strip() != "":
            i += 1
        block = lines[block_start:i]
        next_is_boundary = i >= n or lines[i].strip() == ""

        if next_is_boundary and all(len(l) < GARBAGE_MAX_LINE_LENGTH for l in block):
            for l in block:
                if _is_garbage_line(l):
                    removed += 1
                else:
                    out.append(l)
        else:
            out.extend(block)

    return "\n".join(out), removed


def purify_markdown(text: str) -> tuple[str, dict]:
    """Aplica as 3 camadas (whitespace, boilerplate, lixo de OCR) e
    retorna o texto purificado + um resumo do que foi removido."""
    text = _normalize_whitespace(text)
    text, boilerplate_removidas = _remove_boilerplate(text)
    text, lixo_removidas = _remove_ocr_garbage(text)
    text = _normalize_whitespace(text)  # remocoes acima podem deixar linhas em branco extras

    stats = {
        "boilerplate_linhas_removidas": boilerplate_removidas,
        "lixo_ocr_linhas_removidas": lixo_removidas,
    }
    return text, stats
