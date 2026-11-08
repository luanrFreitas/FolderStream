<h1 align="center">FolderStream</h1>

<p align="center">
  <strong>Transforme qualquer pasta de aulas em vídeo baixadas num player de curso completo, offline e bonito — sem servidor, sem upload, sem depender de ninguém.</strong>
</p>

<p align="center">
  <img alt="license" src="https://img.shields.io/badge/license-GPLv3-blue.svg">
  <img alt="python" src="https://img.shields.io/badge/python-3.10%2B-blue.svg">
  <img alt="offline" src="https://img.shields.io/badge/100%25-offline-success.svg">
  <img alt="status" src="https://img.shields.io/badge/status-early--stage-orange.svg">
</p>

---

Você baixou um curso. Agora tem uma pasta cheia de `Aula.mp4` espalhadas em subpastas com nomes tipo `001. Introducao`, `002. Modulo 2`... e pra assistir você abre cada vídeo manualmente no player padrão do sistema, sem progresso salvo, sem anotações, sem noção de quanto já andou.

**FolderStream** resolve isso: aponte para a pasta do curso, rode um comando, e ganhe um site local completo — sidebar navegável, player com retomada automática, anotações por timestamp, progresso por módulo, temporizador Pomodoro e 8 temas visuais — tudo dentro de um `index.html` que você abre com duplo clique, sem instalar servidor nenhum.

## Por que usar FolderStream em vez de só abrir os vídeos numa pasta?

| | Pasta + player padrão | FolderStream |
|---|:---:|:---:|
| Continuar de onde parou | ❌ manual | ✅ automático |
| Progresso por módulo/curso | ❌ | ✅ |
| Anotações com timestamp clicável | ❌ | ✅ |
| Busca por nome de aula | ❌ | ✅ |
| Próxima aula automática | ❌ | ✅ |
| Pomodoro integrado | ❌ | ✅ |
| Funciona 100% offline, sem conta/login | ✅ | ✅ |
| Sem instalar app, sem servidor | ✅ | ✅ |
| Visual organizado (não é só uma lista de arquivos) | ❌ | ✅ |

## Como funciona

```
Sua pasta de curso                    FolderStream gera:
├── 001. Introducao/                  <curso>/FolderStream/
│   └── 001. Boas-vindas/               ├── index.html   (abra este)
│       ├── Aula.mp4                    ├── script.js
│       └── descricao.html              ├── style.css
├── 002. Modulo Pratico/                └── files_manifest.json
│   └── 001. Parte 1/
│       ├── Aula.mp4
│       └── Aula.pt-br.srt
```

O gerador varre a pasta, monta a árvore de módulos/aulas, lê a duração dos vídeos e produz uma pasta `FolderStream/` ao lado do curso. **Os vídeos originais não são copiados nem movidos** — o player só referencia os arquivos onde já estão, então não duplica espaço em disco e funciona com bibliotecas de qualquer tamanho.

## Principais recursos

- **Zero servidor, zero instalação no navegador.** Abre por `file://`, funciona em qualquer navegador moderno.
- **Progresso e anotações persistentes**, salvos no `localStorage` do navegador, isolados por curso.
- **Retomada automática** — volta exatamente de onde parou em cada vídeo (com correção para não travar em aulas já concluídas).
- **Navegação por teclado**: `Espaço` (play/pause), `←`/`→` (±5s), `N`/`P` (próxima/anterior aula).
- **Controle de velocidade** de reprodução (0.75x–2x).
- **Timer Pomodoro** embutido, com configuração de ciclos de foco/pausa.
- **Backup exportável/importável** em JSON — leva seu progresso e notas para outro navegador ou máquina.
- **Apagar dados do curso** (progresso, anotações e/ou preferências do player, cada um opcional) direto pelo painel de Configurações, com confirmação antes de aplicar.
- **8 temas visuais prontos** (ver abaixo), trocáveis a qualquer momento dentro do player — sem precisar regenerar nada.
- **Modo lote (`--batch`)**: gera a plataforma para todos os cursos de uma pasta-mãe de uma vez, com um índice HTML listando todos.
- **Cache de duração de vídeo**: reprocessar um curso (`--force`) não roda `ffprobe` de novo em vídeos que não mudaram.
- **Leve de verdade**: o `index.html` gerado tem poucos KB — nada de imagens embutidas em base64 inflando o arquivo.

## Temas disponíveis

Todo curso gerado já sai com os 8 temas prontos — a troca é feita dentro do player, sem precisar escolher nada na hora de gerar.

| Tema | Estilo |
|---|---|
| Light — Neutral | Minimalista, fundo branco, acento azul |
| Light — Warm | Tom "papel/editorial", acento âmbar |
| Dark — Slate | Dark neutro, sem preto puro, acento azul claro |
| Dark — Carbon | Preto absoluto (bom para OLED), acento ciano |
| Blue — Corporate | Dark azulado profundo, estilo IDE |
| Blue — Light | Versão clara da família azul |
| Orange & Black — High Contrast | Preto fosco + laranja vibrante |
| Orange & Black — Soft | Tons terrosos, laranja queimado |

## Instalação

Requisitos: **Python 3.10+**. Nenhuma dependência de sistema é obrigatória — a duração dos vídeos é lida direto do arquivo (`.mp4`/`.mov`/`.m4v`, `.mkv`/`.webm`, `.avi`), sem precisar de FFmpeg. Se você tiver **FFmpeg** (`ffprobe`) no PATH, ele é usado primeiro (cobre também `.flv`/`.wmv` e arquivos malformados).

```bash
# recomendado: isola as dependências e coloca o comando no PATH
pipx install folderstream

# ou, com pip
pip install folderstream
```

Se o comando `folderstream` não for encontrado (comum no Windows quando a pasta `Scripts` do Python não está no PATH), use `python -m folderstream` no lugar.

### Atualização

```bash
# se instalou com pipx
pipx upgrade folderstream

# se instalou com pip
pip install -U folderstream
```

As melhorias valem para cursos gerados **depois** da atualização. Para aplicar a versão nova num curso que você já gerou, rode de novo com `--force` — o progresso e as notas salvos são mantidos:

```bash
folderstream "caminho/do/curso" --force
```

<details>
<summary>Instalar a partir do código-fonte</summary>

```bash
git clone https://github.com/luanrFreitas/FolderStream.git
cd FolderStream
pip install -e ".[dev]"
```

</details>

## Uso

```bash
# Gerar a plataforma para um curso
folderstream "D:\Cursos\Meu Curso Incrivel"

# Regenerar (mantém progresso e notas já salvos, reaproveita cache de duração)
folderstream "D:\Cursos\Meu Curso Incrivel" --force

# Com logo/capa personalizada e nome de exibição
folderstream "D:\Cursos\Meu Curso Incrivel" --logo capa.png --nome "Meu Curso Incrível"

# Gerar para todos os cursos de uma pasta de uma vez (+ gera um índice)
folderstream "D:\Cursos" --batch

# Ajuda
folderstream --help
```

Depois é só abrir `<pasta do curso>\FolderStream\index.html` no navegador.


### Estrutura de pasta esperada

```
Meu Curso/
├── 001. Modulo 1/
│   ├── 001. Aula 1/
│   │   ├── Aula.mp4
│   │   ├── Aula.pt-br.srt      (legenda, opcional — associada automaticamente)
│   │   └── descricao.html      (material de apoio, opcional)
│   └── 002. Aula 2/
│       └── Aula.mp4
└── 002. Modulo 2/
    └── ...
```

A ordenação respeita números no nome da pasta (`"2."` vem antes de `"10."`, mesmo sem zero à esquerda). Aulas podem ter sub-aulas aninhadas; módulos com arquivos soltos (sem subpasta) também funcionam. Uma pasta com **vários vídeos soltos direto nela** (em vez de 1 vídeo por subpasta) também é suportada — cada vídeo vira sua própria aula automaticamente. Pastas com **só materiais e nenhum vídeo/HTML** (ex.: uma pasta de PDFs) funcionam também — a aula mostra só a lista de materiais, sem tentar embutir nada.

## Rodando os testes

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## Arquitetura (resumo)

```
scanner  →  manifest  →  builder  →  FolderStream/
(varre a pasta)  (monta o JSON)  (monta HTML/CSS/JS final)
```

- **`folderstream/scanner.py`** varre a pasta do curso, detecta tipo de arquivo, extrai duração (via `ffprobe` se disponível, senão com parsers próprios em Python puro para MP4/MOV/M4V, MKV/WebM e AVI, com cache) e associa legendas automaticamente.
- **`folderstream/manifest.py`** monta o manifest e gerencia o `.course_id` (persistente entre regenerações, para não perder progresso salvo no navegador).
- **`folderstream/builder.py`** junta os 8 temas CSS (`folderstream/themes/`), injeta os dados do curso no motor JS (`folderstream/template/player.js`) e renderiza o HTML final via Jinja2.
- **`folderstream/template/player.js`** é o app inteiro do lado do cliente — JS puro, sem framework, sem build step.

## Roadmap

- [x] Scanner + manifest + generator com os 8 temas embutidos
- [x] Notas por timestamp, progresso, Pomodoro, atalhos de teclado, controle de velocidade
- [x] Backup exportável/importável, cache de duração, modo `--batch`
- [x] Testes automatizados cobrindo `scanner.py` e `builder.py`
- [ ] Suporte a mais formatos de legenda/anexo
- [x] Empacotamento como pacote instalável (`pip install folderstream`)

## Limitações conhecidas

- Progresso e notas ficam no `localStorage` do navegador — trocar de navegador ou limpar dados de navegação reseta tudo, a menos que você use o backup exportável.
- Sem `ffprobe`/FFmpeg instalado, a duração é lida por parsers próprios para `.mp4`/`.mov`/`.m4v`, `.mkv`/`.webm` e `.avi` (cobre praticamente todo curso baixado). Só `.flv` e `.wmv` sem FFmpeg ficam sem duração (o resto funciona normalmente).
- Renomear pastas de aula depois de já ter estudado desconecta o progresso daquele item (o id é baseado no caminho do arquivo).

## Licença

[GPLv3](./LICENSE) — pode usar, estudar, modificar e redistribuir livremente. Se você distribuir uma versão modificada, ela também precisa ser open source sob a GPLv3 (copyleft).
