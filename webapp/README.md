# MarkItDown Web

Interface web local para o [MarkItDown](../README.md) deste repositório. Roda
inteiramente na sua máquina — nenhum arquivo enviado sai dela, e nenhuma
chamada de rede acontece durante a conversão.

## Baixar o repositório

Se ainda não tem o repo localmente:

```bash
git clone https://github.com/paulo-pvbn/markitdown_web.git
cd markitdown_web
```

A pasta `webapp/` (este pacote) precisa estar na raiz do repo, ao lado de
`packages/`.

## Três formas de rodar

| | Só neste PC | Rede local / Tailscale | VPS público |
|---|---|---|---|
| Acesso pelo celular | não | sim, mesma Wi-Fi ou com Tailscale instalado no celular | sim, de qualquer lugar |
| Arquivo sai da sua rede? | não | não (Tailscale é criptografado ponto-a-ponto entre seus próprios dispositivos) | sim, vai para o servidor de terceiro |
| Custo | zero | zero (Tailscale free tier cobre uso pessoal) | ~R$20–40/mês (VPS) |
| Precisa a máquina ligada | sim | sim | não — servidor fica sempre no ar |
| Precisa de HTTPS/senha própria | não | não (tráfego já é privado) | sim, essencial |

Recomendo começar pela opção do meio: resolve o acesso mobile sem abrir mão
do "offline" que motivou o projeto. A opção de VPS público só compensa se
você quiser acessar de fora sem instalar o Tailscale em cada aparelho, ou
compartilhar com outra pessoa.

### 1. Só neste PC

```bash
cd webapp
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abra **http://127.0.0.1:5000**. Só acessível nesta máquina.

### 2. Rede local ou Tailscale (acesso mobile privado)

Com Docker (mais simples de manter ligado):

```bash
cd webapp
docker compose up -d --build
```

Isso já sobe com `HOST=0.0.0.0`, então:
- **Mesma Wi-Fi:** no celular, acesse `http://IP-DO-PC:5000` (IP local do PC,
  ex. `192.168.1.23`).
- **Tailscale** (recomendado se quiser acessar de fora de casa também):
  instale o Tailscale no PC e no celular, entre com a mesma conta, e acesse
  pelo IP/nome Tailscale do PC — o tráfego nunca passa pela internet
  pública, só pela VPN privada entre seus próprios dispositivos.

Sem Docker, o mesmo efeito: `HOST=0.0.0.0 python app.py`.

### 3. VPS público (serviço pessoal online)

Mesma imagem Docker, rodando em um VPS (dá pra usar o Hostinger que você já
tem, ou qualquer VPS ~R$20–40/mês). Diferenças em relação às opções acima:

- Coloque atrás de um proxy com HTTPS (o [Caddy](https://caddyserver.com/)
  resolve isso em ~5 linhas de config, com certificado automático).
- **Adicione autenticação** — sem isso, qualquer um que descobrir a URL
  consegue converter arquivos pelo seu servidor. Mais simples: HTTP Basic
  Auth no próprio Caddy, na frente do app.
- Troque `python app.py` por um servidor WSGI de produção
  (`gunicorn`, já deixado comentado no `Dockerfile`).
- Isso deixa de ser "offline": os arquivos passam pela internet até seu
  servidor. Continuam sob seu controle (é seu VPS), mas não é mais
  equivalente à opção 1/2 em termos de privacidade.

## O que faz

- Arrasta um ou vários arquivos → converte para Markdown.
- Cada resultado aparece com opção de **copiar** ou **baixar o `.md`**.
- Com vários arquivos, dá pra baixar tudo de uma vez em um `.zip`
  (botão "Baixar tudo").

## Pipeline automatizado — pasta de saída pronta pra qualquer app/agente de IA

`watch.py` monitora uma pasta `raw/` e converte tudo que cair nela
automaticamente para Markdown em `converted/`, sem precisar abrir o
navegador nem clicar em nada. O resultado é uma pasta de Markdown
organizada e documentada que qualquer app ou agente de IA pode consumir
— Claude Projects é um exemplo de destino, não o único; serve igual
pra alimentar outro agente, um vector DB próprio, ou só pra ter o
material em texto pronto pra qualquer uso.

```bash
docker compose up -d --build
```

(o `docker-compose.yml` já sobe o `markitdown-web` e o `markitdown-watch`
juntos)

**Convenção recomendada** — uma subpasta em `raw/` por projeto/tema/destino:

```
raw/
├── investigacao-cripto/    →  converted/investigacao-cripto/
│   ├── laudo1.pdf                ├── laudo1.md
│   └── planilha.xlsx              ├── planilha.md
│                                   └── _manifest.json
└── artigo-rbdpp/            →  converted/artigo-rbdpp/
    └── rascunho.docx              ├── rascunho.md
                                    └── _manifest.json
```

Cada `.md` gerado sai com um front matter simples (nome do arquivo
original, caminho e data da conversão), útil pra rastrear a origem
depois:

```markdown
---
source: laudo1.pdf
source_path: raw/investigacao-cripto/laudo1.pdf
converted_at: 2026-09-03T14:32:36
---
```

Cada subpasta de `converted/` também ganha um `_manifest.json`,
atualizado a cada arquivo processado ali — útil pra qualquer app de
destino descobrir de uma vez só o que tem na pasta, sem precisar listar
o diretório:

```json
{
  "gerado_em": "2026-09-03T21:00:00",
  "arquivos": [
    {"arquivo": "laudo1.md", "fonte": "laudo1.pdf", "convertido_em": "2026-09-03T20:58:11", "caracteres": 4213}
  ]
}
```

**Sobre chunking:** o pipeline não faz chunking manual — cada app de
destino resolve isso do seu jeito. No caso específico dos Claude
Projects, o RAG [ativa automaticamente](https://support.claude.com/en/articles/11473015)
quando o conteúdo do projeto se aproxima do limite da janela de
contexto, e ele mesmo cuida da indexação/busca; chunking manual só
faria sentido se o destino fosse um vector DB próprio (Chroma, Qdrant
etc.).

**A entrega final no destino é manual ou por conta de cada app** — o
pipeline entrega até `converted/`, com `.md` + manifesto; não há
integração automatizada com nenhum destino específico. No caso de um
Claude Project, por exemplo: a Anthropic não tem uma API pública pra
subir arquivos num Project — só dá pra fazer isso arrastando os `.md`
pra aba Knowledge do Project, pelo navegador. (Existem pacotes não
oficiais que automatizam isso reaproveitando a sessão do seu navegador,
mas não recomendo — dependem de guardar sua chave de sessão, o que é um
risco de segurança desnecessário pra esse ganho.) Limite bom de saber
nesse caso: arquivos de Project ficam em até 30MB cada, sem limite de
quantidade — os `.md` do MarkItDown ficam bem abaixo disso na grande
maioria dos casos.

## Formatos suportados no modo offline

PDF, Word (`.docx`), PowerPoint (`.pptx`), Excel novo e antigo
(`.xlsx`/`.xls`), mensagens do Outlook (`.msg`), HTML, CSV/JSON/XML, ZIP
(itera pelo conteúdo), EPUB e imagens (metadados EXIF).

## Por que alguns recursos do MarkItDown ficam de fora

O `requirements.txt` instala só os extras que **não** dependem de rede:

| Recurso | Por que fica de fora |
|---|---|
| Transcrição de áudio | por padrão usa a API de voz do Google (precisa de internet) |
| Transcrição de YouTube | busca a legenda direto no YouTube |
| Azure Document Intelligence / Content Understanding | serviços pagos na nuvem da Microsoft |
| Descrição de imagens via LLM (`llm_client`) | precisa de uma API de modelo (OpenAI, Claude, etc.) |

Se um dia você quiser religar algum desses — por exemplo, transcrição de
áudio com um motor local como o `pocketsphinx`, ou descrição de imagem via
um LLM local (Ollama) — dá pra adicionar sem tocar no resto da arquitetura:
o `MarkItDown()` em `app.py` é o único ponto de configuração.

## Arquitetura

```
webapp/
├── app.py              # Flask: serve o front-end e expõe /convert e /convert-zip (uso manual)
├── watch.py             # monitora raw/ e converte sozinho pra converted/ (uso automatizado)
├── requirements.txt    # Flask + watchdog + markitdown (extras offline) instalado direto deste repo
├── Dockerfile           # imagem única usada pelos dois serviços do docker-compose.yml
├── docker-compose.yml   # sobe markitdown-web + markitdown-watch juntos
├── static/
│   └── index.html      # front-end de arquivo único (HTML+CSS+JS, sem CDN)
└── README.md
```

Tanto `app.py` quanto `watch.py` importam o `markitdown` diretamente de
`../packages/markitdown/src` deste repositório (não do PyPI), então
qualquer modificação que você fizer no core do conversor já reflete nos
dois sem precisar reinstalar nada.

## Próximos passos possíveis (fora do MVP)

- Limite de tamanho de upload da interface web já está em 50 MB
  (`MAX_CONTENT_LENGTH` em `app.py`) — ajuste se precisar de arquivos
  maiores.
- Autenticação simples, se for expor além de `127.0.0.1`.
