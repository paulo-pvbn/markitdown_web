## Ordem 05: Comparar Tesseract vs. rapidocr-onnxruntime em qualidade de OCR

- **Depende de**: nenhuma (independente da Ordem 04, pode rodar em qualquer ordem)
- **Bloqueia**: a decisão sobre suportar PDF escaneado (pendência registrada na Ordem 03 / Notion)
- **Decisão de produto já confirmada?**: sim — decidido em chat (2026-09-03): comparar os dois motores antes de decidir o caminho.

## Objetivo

Determinar, com evidência concreta e reproduzível, se o Tesseract produz qualidade sensivelmente melhor que o `rapidocr-onnxruntime` (testado na Ordem 03) nos problemas já identificados: acentos perdidos, espaço entre palavras perdido, e ordem de coluna embaralhada em tabela. Isso é investigação, não implementação — nenhuma mudança em `app.py`/`watch.py` nesta ordem.

## Contrato de dados

Sem alteração de schema. Sem alteração do `requirements.txt` do projeto — dependências de teste (`pytesseract`, binário Tesseract, `rapidocr-onnxruntime` de novo) instaladas só no venv/scratchpad de teste, desinstaladas e documentadas ao final, mesmo padrão já usado na Ordem 03.

Saída esperada: dois arquivos de texto por página testada (ex.: `pagina-11-tesseract.txt`, `pagina-11-rapidocr.txt`), guardados fora do repositório, pra comparação lado a lado.

## Casos de borda que o executor deve tratar

- **Tesseract não é um pacote pip** — precisa do binário instalado no Windows (normalmente via instalador do UB-Mannheim). Se não estiver presente na máquina, **parar e perguntar ao usuário antes de instalar** — mesma régua já aplicada ao Docker Desktop nesta metodologia; não presumir que instalar software de sistema está sempre liberado.
- Usar os idiomas `por+eng` no Tesseract — testar só com `eng` sub-representaria a qualidade em português.
- Usar exatamente as mesmas 3 páginas já testadas na Ordem 03 (11, 51 e 121 do `733086206-Mercado-Financeiro-13ed.pdf`, ainda em `webapp/raw/InvestBot/` conforme relatório anterior) e a mesma resolução de renderização (300 DPI) — qualquer diferença de configuração de renderização compromete a comparação.
- Testar pelo menos um `--psm` (modo de segmentação de página) alternativo do Tesseract na página 121 (tabela) — o modo padrão costuma ser ruim pra tabela/coluna dupla; vale tentar um modo orientado a bloco/coluna antes de declarar o resultado final pra essa página.
- Medir tempo por página nos dois motores, na mesma máquina, na mesma sessão — não comparar contra o tempo já registrado na Ordem 03 (pode ter variado por carga da máquina).

## Fora de escopo (explicitamente)

- Não decidir o caminho final (suportar/não suportar OCR) — essa decisão continua com o arquiteto/usuário depois de ver o resultado desta ordem.
- Não integrar OCR ao `app.py`/`watch.py` nesta ordem, nem como protótipo.
- Não testar o livro inteiro (418 páginas) — só as 3 páginas de amostra já usadas na Ordem 03.
- Não criar `ORDEM-06` nesta sessão.

## Referência visual/técnica

- `audit/2026-09-03-ORDEM-03-piloto-real-claude-project.md` — resultados originais do `rapidocr-onnxruntime` pra essas mesmas 3 páginas (qualidade, tempo).
- Configuração de Tesseract usada por um projeto de terceiro revisado em chat: idiomas `por`+`eng`, instalação padrão em `C:\Program Files\Tesseract-OCR` no Windows — referência de configuração, não está neste repo.

## Critério de pronto

1. Tesseract rodou nas mesmas 3 páginas (11, 51, 121), com `por+eng`, 300 DPI, e pelo menos uma tentativa de `--psm` ajustado pra página 121.
2. `rapidocr-onnxruntime` rodou de novo nas mesmas 3 páginas, na mesma sessão (pra ter tempo comparável ao Tesseract).
3. Textos extraídos dos dois motores salvos em arquivos separados (scratchpad, fora do repo) pra cada página.
4. Relatório de auditoria compara objetivamente, por página: acentos preservados (sim/não/parcial), espaçamento entre palavras preservado (sim/não/parcial), ordem de coluna da tabela (página 121) correta ou embaralhada, e tempo de processamento.
5. Recomendação explícita do executor no relatório (qual motor tem melhor qualidade, com base no que foi observado) — a decisão final de implementar ou não continua pendente pro arquiteto/usuário.
