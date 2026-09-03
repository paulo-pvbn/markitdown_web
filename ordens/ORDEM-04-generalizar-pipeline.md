## Ordem 04: Generalizar o pipeline — pasta de saída pronta pra qualquer app

- **Depende de**: Ordem 02 (pipeline validado)
- **Bloqueia**: nenhuma conhecida
- **Decisão de produto já confirmada?**: sim — decidido em chat (2026-09-03): reposicionar o projeto como conversor genérico ("pra agentes de IA" em geral), não específico a Claude Projects.

## Objetivo

Generalizar a documentação e a saída do pipeline pra deixar claro — e, na saída, tecnicamente pronto — que o material convertido serve pra qualquer app/agente de IA consumir, não só upload manual num Claude Project. Majoritariamente reposicionamento de documentação, mais uma peça pequena de código nova: um manifesto por pasta de saída.

## Contrato de dados

Novo arquivo gerado por `watch.py`: `converted/<pasta>/_manifest.json`, um por subpasta, atualizado (não recriado do zero) a cada conversão nessa subpasta.

```json
{
  "gerado_em": "2026-09-03T21:00:00",
  "arquivos": [
    {"arquivo": "laudo1.md", "fonte": "laudo1.pdf", "convertido_em": "2026-09-03T20:58:11", "caracteres": 4213}
  ]
}
```

Sem alteração de schema em outros pontos — front matter dos `.md` individuais continua igual (`source`, `source_path`, `converted_at`).

## Casos de borda que o executor deve tratar

- Manifesto precisa ser **atualizado**, não sobrescrito do zero, a cada novo arquivo convertido naquela subpasta — senão perde entradas anteriores.
- Manifesto não deve listar a si mesmo (`_manifest.json` não aparece como entrada dentro do próprio manifesto).
- Se `converted/<pasta>/` já tiver `.md` de sessões anteriores (Ordens 02/03) sem manifesto, o primeiro `convert_existing()` depois desta ordem deve gerar o manifesto retroativamente pra esses arquivos também, não só pros novos.
- Execução concorrente (dois arquivos chegando quase ao mesmo tempo na mesma subpasta) não deve corromper o JSON — usar escrita atômica (escrever em arquivo temporário + rename) se necessário.

## Fora de escopo (explicitamente)

- Não implementar OCR nem qualquer decisão de PDF escaneado nesta ordem — decisão em aberto tratada separadamente.
- Não renomear as pastas `raw/`/`converted/` em si — já são genéricas o suficiente (entrada/saída). Só a documentação e a convenção de subpastas mudam de framing.
- Não mexer em Docker/Tailscale nesta ordem.
- Não criar `ORDEM-05` nesta sessão.

## Referência visual/técnica

- `docs/instrucoes-projeto-markitdown-web.md` — seção "Pipeline automatizado" (reescrever o framing "pra RAG"/Claude Projects pra algo genérico, Claude Projects como exemplo entre outros).
- `webapp/README.md` — mesma generalização de framing.

## Critério de pronto

1. `watch.py` gera/atualiza `_manifest.json` em cada subpasta de `converted/` toda vez que processa um arquivo daquela subpasta.
2. Rodar novamente sobre o material já convertido nas Ordens 02/03 confirma que o manifesto retroage corretamente pros arquivos já existentes, sem duplicar entradas.
3. `docs/instrucoes-projeto-markitdown-web.md` e `webapp/README.md` atualizados com o framing genérico.
4. Relatório de auditoria escrito em `audit/`.
