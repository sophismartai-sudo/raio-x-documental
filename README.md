# 🛡️ raio-x-documental

**Detector offline de texto oculto e _prompt injection_ em documentos.**
Uma contribuição pública e gratuita ao Poder Judiciário brasileiro.

`100% offline` · `sem rede` · `não altera o original` · `determinístico e auditável` · `Python 3.9+`

**Três jeitos de usar:** 🖥️ **pelo Terminal**, 100% offline — o jeito certo para documentos sigilosos ·
🟠 **no Claude Code** · 🟢 **no Codex** (OpenAI / ChatGPT).

---

## 💛 Uma palavra de gratidão

Esta ferramenta nasceu de um propósito simples: **proteger quem decide.**

Quando um documento carrega instruções escondidas — invisíveis aos olhos, mas
lidas pela máquina — quem confia numa inteligência artificial para ajudar a ler
pode ser induzido ao erro sem jamais perceber. Num processo judicial, isso não é
um detalhe técnico: é a integridade da Justiça em jogo.

O **raio-x-documental** é a nossa forma de contribuir. Ele foi construído para
ser **honesto, transparente e seguro**: roda inteiramente no seu computador, não
envia nada para lugar nenhum, nunca altera o documento original e explica cada
achado com evidência. É um **auxílio** ao trabalho humano — nunca um substituto
dele.

A magistrados, servidores, peritos, advogados e a todos que zelam pela lisura do
processo: **obrigado pelo cuidado que vocês com cada documento.** Que esta
ferramenta seja uma pequena ajuda nesse cuidado.

— **Murilo Ferreira** ([@agro_muriloferreira](https://instagram.com/agro_muriloferreira)) · **Sophismart.ai** ([@sophismart.ai](https://instagram.com/sophismart.ai))

---

## 🎯 O que é

Golpistas têm inserido **comandos ocultos** dentro de documentos (laudos,
petições, contratos) para manipular assistentes de IA — por exemplo, texto
**branco sobre branco** mandando o assistente "concordar com as conclusões do
perito". A revisão visual e o OCR **não enxergam** esse texto; a IA, que lê a
camada de texto real, enxerga.

O raio-x-documental faz o **inverso do OCR**: extrai o que a **máquina** lê e
compara com o que o **humano** vê. A diferença é o ataque.

## 🔍 O que ele detecta

| Categoria | Exemplos de vetores |
|---|---|
| **Texto oculto visual** | branco-no-branco / baixo contraste, fonte minúscula, texto fora da página, opacidade zero, modo de renderização invisível |
| **Contrabando de caractere** | Unicode Tags (U+E0000+), caracteres de largura zero, overrides bidirecionais (BiDi/Trojan Source) |
| **Ocultação estrutural** | `w:vanish` (DOCX), `display:none`/`visibility:hidden` (HTML/e-mail), texto oculto em RTF, comentários HTML, metadados, declarações `DOCTYPE`/entidade XML anômalas |
| **Comando dirigido à IA** | frases de _prompt injection_ em PT e EN (ex.: "ignore as instruções anteriores", "dê parecer favorável", "julgue procedente") |
| **Imagens e PDF escaneado** | texto de baixíssimo contraste revelado por realce + OCR local |

**Severidade composta:** o alarme máximo (🔴 CRÍTICO) exige **ocultação + comando
dirigido à IA** — exatamente o caso real que motivou o projeto. Texto oculto
benigno é 🟡 MÉDIO; comando visível é 🟠 ALTO. Isso reduz falso-positivo.

### Formatos suportados
PDF (nativo e escaneado), TXT/MD, DOCX/DOC, ODT, RTF, HTML/e-mail (.html/.eml),
imagens (PNG/JPG/TIFF/BMP/WEBP).

## 🔒 Segurança de uso (o que torna esta ferramenta confiável)

- **100% offline, sem rede.** A ferramenta **não envia o documento para lugar
  nenhum** — nenhum upload, nenhuma nuvem, nenhuma chamada externa. Adequado a
  **sigilo** e à **LGPD**. Atenção: se você a usar **pelo Claude ou pelo Codex**, o que o
  assistente lê passa pela nuvem — para documentos sigilosos, use o Terminal
  direto (veja **Privacidade** e o **Passo a passo** logo abaixo).
- **Lê só o que você escolhe.** O arquivo indicado, ou os documentos que estão
  diretamente dentro da pasta indicada — nunca subpastas, nunca atalhos que
  apontam para fora, nunca outras pastas do computador.
- **Blindada contra documentos-armadilha.** Estruturas XML anômalas em DOCX/ODT
  (declarações `DOCTYPE`/entidade) são sinalizadas no laudo e jamais fazem a
  ferramenta ler outros arquivos ou pular partes do documento.
- **Auditável por qualquer pessoa.** Código aberto e curto, sem nada escondido — veja a seção
  **Confira você mesmo** para comprovar, com testes simples, que ela não coleta nem envia nada.
- **Nunca altera o original.** Toda saída é um arquivo **novo**; o documento de
  origem permanece intacto (byte a byte).
- **Determinístico e auditável.** Mesmo arquivo → mesmo resultado. Nada de "a IA
  achou que estava limpo": cada achado vem com técnica, localização e trecho.
- **Cadeia de custódia.** O laudo e as cópias registram o **hash SHA-256** do
  original, a metodologia e a versão da ferramenta (espelhando CPC art. 473 e
  CPP art. 158-A).
- **Honestidade sobre limites.** "LIMPO" significa **"nenhum vetor conhecido
  encontrado"**, não uma garantia absoluta. Se o OCR não estiver disponível, a
  imagem é marcada como **não verificada** — nunca como "limpa" por omissão.
- **Não pune sozinho.** É um auxílio: recomenda-se **intimação prévia** da parte
  antes de qualquer sanção (evita punir erro de editoração/conversão).

## 🔐 Privacidade: o que é offline — e o que não é

Há duas coisas diferentes aqui, e vale entender a diferença:

- **A ferramenta** são programas que rodam **no seu computador**. Eles leem o documento do seu disco, analisam e gravam o resultado no seu disco. **Não existe nenhuma linha de código que acesse a internet** — você pode desligar o Wi-Fi e ela funciona igual.
- **Os assistentes de IA** — o Claude e o Codex (ChatGPT) — funcionam **na nuvem**, nos servidores da Anthropic e da OpenAI.

Por isso, existem dois jeitos de usar:

| | **Jeito A — pelo Terminal, direto** | **Jeito B — pedindo ao Claude ou ao Codex** |
|---|---|---|
| Quem analisa o documento | os programas locais | os mesmos programas locais |
| O documento sai do computador? | **Não. Nada sai.** | A ferramenta não envia o arquivo, **mas** tudo o que o assistente lê — o resultado, os trechos encontrados, o laudo ou o próprio documento, se você pedir — **passa pelos servidores da Anthropic (Claude) ou da OpenAI (Codex)** |
| Indicado para | **documentos sigilosos**, segredo de justiça, dados pessoais (LGPD) | documentos sem sigilo, triagem rápida |

> **Regra de ouro:** documento sigiloso → **Jeito A** (passo a passo logo abaixo). Nunca cole trechos de documento sigiloso numa conversa com qualquer IA.

**O que a ferramenta grava no seu computador** — e só se você pedir: o laudo, o resumo da pasta e as cópias higienizadas, **na pasta de resultados que você escolher**. Durante a análise de imagens e PDFs escaneados, cópias temporárias das páginas são criadas na pasta temporária do sistema, acessíveis só pelo seu usuário, e **apagadas ao final**. A ferramenta não guarda histórico, não envia estatísticas e não fala com nenhum servidor.

**Ela lê somente o que você escolhe:** o arquivo indicado, ou os documentos que estão **diretamente dentro** da pasta indicada. Não abre subpastas, não segue atalhos que apontam para fora da pasta e não consulta nenhum outro lugar do computador — nem mesmo quando um documento malicioso tenta induzi-la a isso.

Os arquivos gerados contêm **trechos do documento analisado**: guarde-os com o mesmo sigilo do documento original.

## 🧭 Passo a passo: verificar documentos sigilosos 100% offline

> Feito para quem **nunca usou o Terminal**. A **Parte 1** é feita **uma única vez**. Depois, para cada verificação, basta a **Parte 2**.
>
> Em computadores do tribunal em que não é permitido instalar programas, peça ao **suporte de TI** para fazer a Parte 1 — basta mostrar esta página.

### Parte 1 — Preparar o computador (uma vez só, com internet)

A internet só é necessária **agora**, para baixar os programas. Depois disso, a verificação funciona sem internet.

**1. Instale o Python** — o "motor" que executa a ferramenta.
- Acesse **https://www.python.org/downloads/** e clique no botão amarelo **"Download Python"**.
- **Windows:** abra o arquivo baixado. **Antes de clicar em "Install Now", marque a caixinha "Add python.exe to PATH"**, que fica na parte de baixo da primeira tela. Depois clique em **Install Now**.
- **Mac:** abra o arquivo baixado e siga o instalador (Continuar → Concordar → Instalar).

**2. Baixe a ferramenta.**
- Acesse **https://github.com/sophismartai-sudo/raio-x-documental**.
- Clique no botão verde **"<> Code"** e depois em **"Download ZIP"**.
- Abra a pasta **Downloads** e:
  - **Windows:** clique com o botão direito no arquivo ZIP → **"Extrair tudo..."** → **Extrair**;
  - **Mac:** dê dois cliques no arquivo ZIP.
- Aparecerá uma pasta chamada **raio-x-documental-main**. Mova-a para um lugar fácil, como **Documentos**.

**3. Abra o Terminal** — a janela onde se digitam comandos.
- **Windows:** clique em **Iniciar**, digite **cmd** e abra o **Prompt de Comando**.
- **Mac:** aperte **Cmd + Espaço**, digite **Terminal** e aperte **Enter**.

**4. Instale as bibliotecas da ferramenta.** Copie o comando do seu sistema, cole no Terminal e aperte **Enter**:
- **Windows:**
  ```
  py -m pip install pymupdf python-docx lxml pillow
  ```
- **Mac:**
  ```
  python3 -m pip install pymupdf python-docx lxml pillow
  ```
Aguarde até aparecer **"Successfully installed"**.

**5. (Recomendado) Instale o leitor de imagens (OCR).** Ele é necessário para **PDFs escaneados** e **fotos de documentos** — muito comuns em processos. Sem ele a ferramenta funciona, mas avisa que esses arquivos **não foram verificados** (nunca os declara "limpos").
- **Windows:** baixe o instalador em **https://github.com/UB-Mannheim/tesseract/wiki**. Ao instalar, na tela de componentes, abra **"Additional language data"** e marque **Portuguese**. Mantenha a pasta de instalação sugerida — a ferramenta a encontra sozinha.
- **Mac:** instale o Homebrew seguindo **https://brew.sh** e depois rode no Terminal: `brew install tesseract tesseract-lang`

**6. Confira se deu tudo certo.** No Terminal, digite `py` (Windows) ou `python3` (Mac) e **um espaço**. Em seguida, **arraste o arquivo `verificar.py`** — ele fica em `raio-x-documental-main` → `scripts` — para dentro da janela do Terminal. O caminho do arquivo aparece escrito sozinho. Por fim, digite um espaço, `--doctor`, e aperte **Enter**. Você deve ver **"Dependências OK."**

### Parte 2 — Verificar documentos (sempre que precisar, sem internet)

**1. Separe os documentos numa pasta.** Crie uma pasta — por exemplo **"Conferir"**, na Área de Trabalho (no Mac, **"Mesa"**) — e coloque nela os documentos a verificar. **A ferramenta analisa somente os documentos que estão dentro dessa pasta.** Subpastas não são abertas.

**2. Crie uma pasta para os resultados** — por exemplo **"Resultados"**, também na Área de Trabalho. Ela precisa ser **diferente** da pasta dos documentos.

**3. (Opcional, para ter certeza absoluta) Desligue a internet.** Desative o Wi-Fi ou retire o cabo de rede. A ferramenta funciona do mesmo jeito — é a prova de que nada sai do seu computador.

**4. Monte o comando arrastando as pastas.** No Terminal:
1. digite `py` (Windows) ou `python3` (Mac) e **um espaço**;
2. **arraste o arquivo `verificar.py`** para a janela e digite **um espaço**;
3. **arraste a pasta "Conferir"** para a janela e digite **um espaço**;
4. digite `--laudo` e **um espaço**;
5. **arraste a pasta "Resultados"** para a janela;
6. aperte **Enter**.

O comando ficará parecido com um destes — com os caminhos do seu computador:
```
py C:\Users\ana\Documents\raio-x-documental-main\scripts\verificar.py C:\Users\ana\Desktop\Conferir --laudo C:\Users\ana\Desktop\Resultados
```
```
python3 /Users/ana/Documents/raio-x-documental-main/scripts/verificar.py /Users/ana/Desktop/Conferir --laudo /Users/ana/Desktop/Resultados
```

**5. Leia o resultado.** O Terminal mostra quantos documentos foram analisados e, em destaque, a lista **"DOCUMENTOS COM CONTEÚDO MALICIOSO OU SUSPEITO"**, com o que foi encontrado em cada um. Na pasta **Resultados**, dê dois cliques em **`resumo_da_pasta.html`** — ele abre no navegador, sem internet, e lista todos os documentos. Cada documento suspeito ganha uma subpasta com o seu **laudo formal**.

| Resultado | O que significa | O que fazer |
|---|---|---|
| 🔴 **CRÍTICO** | Texto escondido **com um comando dirigido à IA** — o padrão do golpe | **Não use IA nesse documento.** Leia o laudo e siga o rito (intimação prévia da parte) |
| 🟠 **ALTO** | Comando dirigido à IA em texto visível, ou conteúdo codificado | Revise com atenção antes de usar IA |
| 🟡 **MÉDIO** | Conteúdo escondido sem comando evidente, ou arquivo que **não pôde ser verificado** | Confira manualmente |
| ✅ **LIMPO** | Nenhuma técnica conhecida de ocultação foi encontrada | Pode seguir — "limpo" não é garantia absoluta |

**6. (Opcional) Gere uma cópia segura ou revele o que estava escondido.** Acrescente ao final do comando `--higienizar`, um espaço, arraste de novo a pasta "Resultados" e escolha o modo:
- `--modo neutralizar` → cópia `.txt` só com o texto **visível**, sem o conteúdo oculto — própria para usar numa IA;
- `--modo revelar` → mostra **exatamente o que estava escondido**, decodificado;
- `--modo ambos` → as duas coisas.

**7. Encerre com cuidado.** Religue a internet, se tiver desligado, e **guarde a pasta "Resultados" com o mesmo sigilo do documento original** — ela contém trechos dele.

> **O original nunca é alterado.** A ferramenta só lê os documentos da pasta escolhida e grava os resultados na pasta de resultados.

### Se algo der errado

| Mensagem | Solução |
|---|---|
| **Windows:** "py não é reconhecido" | Reinstale o Python (Parte 1, passo 1) mantendo as opções padrão do instalador — elas instalam o comando `py` — e marque **"Add python.exe to PATH"** |
| **Mac:** "command not found: python3" | Instale o Python pelo site python.org (Parte 1, passo 1) |
| "No module named fitz" (ou docx, lxml, PIL) | Repita a Parte 1, passo 4 |
| "OCR: tesseract AUSENTE" | Repita a Parte 1, passo 5 — ou peça ao suporte de TI |
| "a pasta de resultados não pode ser a mesma pasta analisada" | Crie uma pasta separada para os resultados (Parte 2, passo 2) |

## 📦 Instalação no Claude Code

O raio-x-documental é uma **skill do Claude Code**. Instalar = colocá-la na sua
pasta de skills.

> **Link de instalação (repositório oficial):**
> **https://github.com/sophismartai-sudo/raio-x-documental**

**1. Baixe a skill para a pasta de skills do Claude:**
```bash
git clone https://github.com/sophismartai-sudo/raio-x-documental ~/.claude/skills/raio-x-documental
```

**2. Instale as dependências Python** (núcleo):
```bash
python3 -m pip install pymupdf python-docx lxml pillow
```

**3. (Opcional) OCR para imagens e PDF escaneado** — instale o `tesseract`:
```bash
# macOS
brew install tesseract tesseract-lang
# Debian/Ubuntu
sudo apt-get install tesseract-ocr tesseract-ocr-por
```

**4. Verifique a instalação:**
```bash
python3 ~/.claude/skills/raio-x-documental/scripts/verificar.py --doctor
```

Pronto. Dentro do Claude Code, a skill é reconhecida automaticamente e responde a
pedidos como **"verifica esse documento"**, **"tem prompt injection nesse PDF?"**
ou **"esse laudo tem texto escondido?"**.

## 🤖 Instalação e uso no Codex (OpenAI / ChatGPT)

A mesma skill funciona no **Codex**, o agente da OpenAI que vem no aplicativo do ChatGPT e também
na linha de comando e na IDE. **Testada no Codex do aplicativo do ChatGPT (Mac):** chamada pelo nome ou
por um pedido comum, ele encontra a skill, roda a verificação no seu computador e aponta o golpe
(veredito CRÍTICO) — sem obedecer ao comando escondido.

O Codex procura skills na pasta pessoal **`~/.agents/skills`** (no Windows, `%USERPROFILE%\.agents\skills`).

### Instalar — opção A: com um comando
```bash
git clone https://github.com/sophismartai-sudo/raio-x-documental ~/.agents/skills/raio-x-documental
```

### Instalar — opção B: sem comandos, baixando o ZIP
1. Nesta página do GitHub, clique em **"<> Code"** → **"Download ZIP"** e extraia o arquivo.
2. Renomeie a pasta extraída de **raio-x-documental-main** para **raio-x-documental**.
3. Abra a pasta de skills do Codex:
   - **Mac:** no Finder, aperte **Cmd + Shift + G**, digite `~/.agents/skills` e aperte **Enter**;
   - **Windows:** na barra de endereço do Explorador de Arquivos, digite `%USERPROFILE%\.agents\skills` e aperte **Enter**.

   Se a pasta ainda não existir, crie-a com um comando — Mac (Terminal): `mkdir -p ~/.agents/skills` ·
   Windows (Prompt de Comando): `mkdir %USERPROFILE%\.agents\skills`.
4. Mova a pasta **raio-x-documental** para dentro dela.

### Depois de instalar
- **Dependências** (se ainda não instalou; o OCR é opcional, como no passo a passo):
  `python3 -m pip install pymupdf python-docx lxml pillow` — no Windows, use `py` no lugar de `python3`.
- **Conferir:** `python3 ~/.agents/skills/raio-x-documental/scripts/verificar.py --doctor`
- O Codex detecta skills novas sozinho; se ela não aparecer, reinicie o Codex.

### Como usar no Codex
Chame pelo nome — `$raio-x-documental` — ou simplesmente peça em português. Exemplos de pedidos:
- `verifica esse documento: ~/Desktop/laudo.pdf`
- `$raio-x-documental verifica todos os documentos da pasta ~/Desktop/Conferir e gera os laudos em ~/Desktop/Resultados`
- `me mostra exatamente o que estava escondido nesse documento`
- `gera uma cópia neutralizada desse documento, só com o texto visível`

### Atualizar
- Opção A: `git -C ~/.agents/skills/raio-x-documental pull`
- Opção B: baixe o ZIP de novo e substitua a pasta **raio-x-documental**.

Depois de atualizar, confira se a sua cópia é a original: `python3 ~/.agents/skills/raio-x-documental/scripts/verificar.py --verificar-integridade`

> **Privacidade:** como no Claude, a ferramenta roda no seu computador, mas o modelo da OpenAI vê o que
> o Codex lê — o resultado, os trechos encontrados, o laudo. Para documentos sigilosos, use o Terminal
> direto (veja **Privacidade**).
>
> **Permissões:** o Codex pode pedir sua aprovação para executar o comando ou para gravar o laudo. No
> modo **somente leitura**, ele verifica o documento e mostra o veredito normalmente, mas não grava o
> laudo — para gerar o arquivo, use um modo com permissão de gravação ou aprove quando ele pedir. A
> ferramenta só lê o documento indicado e só grava na pasta de resultados que você escolher.

## 🚀 Como usar

**Verificar um documento** (veredito no terminal; _exit code_ 1 = CRÍTICO/ALTO):
```bash
python3 scripts/verificar.py caminho/do/documento.pdf
```

**Verificar uma pasta inteira** — só os documentos que estão diretamente dentro dela (subpastas e atalhos que apontam para fora **não** são lidos):
```bash
python3 scripts/verificar.py caminho/da/pasta --laudo ./resultados
```
Gera `resultados/resumo_da_pasta.html` (abre no navegador, sem internet) e, para cada documento suspeito, uma subpasta com o laudo formal. A pasta de resultados precisa ser diferente da pasta analisada.

**Gerar o laudo formal** (HTML + JSON, padrão CPC 473 com hash SHA-256):
```bash
python3 scripts/verificar.py documento.pdf --laudo ./saida
```

**Higienização opcional — você escolhe na hora** (sempre em cópia; nunca altera o original):
```bash
# cópia .txt só com o texto visível (segura para colar numa IA)
python3 scripts/verificar.py documento.pdf --higienizar ./saida --modo neutralizar

# revelar exatamente o que estava escondido, decodificado
python3 scripts/verificar.py documento.pdf --higienizar ./saida --modo revelar

# as duas coisas
python3 scripts/verificar.py documento.pdf --higienizar ./saida --modo ambos
```

**Checar dependências / OCR:**
```bash
python3 scripts/verificar.py --doctor
```

## 🧾 Integridade e autenticidade (travas contra adulteração)

Esta é uma ferramenta de confiança — então ela **se deixa auditar**. Como é
distribuída em texto aberto, a proteção contra cópia maliciosa é feita por
**detecção**, não por bloqueio: você consegue **provar** que a sua cópia é a
original, não uma versão adulterada por um terceiro mal-intencionado.

```bash
python3 scripts/verificar.py --verificar-integridade
```
O comando confere cada arquivo contra o manifesto `INTEGRIDADE.sha256` e avisa se
algo foi alterado, adicionado ou removido.

> **As travas ficam só na ferramenta, nunca nos seus documentos.** Os avisos de
> autoria, a licença e a verificação de integridade vivem **apenas no código-fonte
> e no manifesto** — elas **não aparecem** nos documentos que você analisa nem nos
> arquivos que a skill gera (laudo, cópias). As saídas permanecem documentos
> limpos, próprios para os autos: trazem apenas o **nome e a versão da ferramenta**,
> como exige a cadeia de custódia, e nada de marca ou aviso de licença.

**Recomendações:**
- Baixe e distribua **apenas** cópias do **repositório oficial da Sophismart.ai**.
- Desconfie de qualquer versão "melhorada", "modificada" ou vendida — a licença
  proíbe alteração e venda (veja abaixo).
- Cada arquivo de código traz o aviso de autoria e licença no cabeçalho.

## 🔎 Confira você mesmo: a ferramenta não coleta nem envia nada

> **Nosso compromisso:** o raio-x-documental **não tem — e nunca terá —** agente oculto, rastreador,
> telemetria ou qualquer código que colete, copie ou envie informações suas ou dos seus documentos.
> Você não precisa acreditar na nossa palavra: **confira**. Tudo o que a ferramenta faz está no código
> aberto desta página — cerca de 1.500 linhas de Python, sem nenhum programa compilado ou escondido
> (os únicos arquivos que não são texto são os documentos de exemplo, em `exemplos/`).

Os comandos abaixo são rodados **dentro da pasta da ferramenta**. Para entrar nela pelo Terminal, digite
`cd`, um espaço, arraste a pasta da ferramenta para a janela e aperte **Enter**. No Windows, use `py` no
lugar de `python3`.

### Para qualquer pessoa

**1. Confirme que a sua cópia é a original** — que ninguém a adulterou pelo caminho:
```bash
python3 scripts/verificar.py --verificar-integridade
```
Deve responder **"Integridade OK"**.

**2. O teste mais simples: sem internet.** Desligue o Wi-Fi (ou tire o cabo de rede) e use a ferramenta
normalmente. Ela funciona igual, porque não precisa de internet para nada — e, sem internet, não teria
como enviar coisa alguma.

**3. Procure no código qualquer comunicação com a internet:**
- **Mac / Linux:**
  ```bash
  grep -rnE "socket|urllib|http\.client|requests|urlopen|ftplib|smtplib|webbrowser" scripts/
  ```
- **Windows (PowerShell):**
  ```powershell
  Get-ChildItem scripts -Recurse -Filter *.py | Select-String -Pattern "socket|urllib|http\.client|requests|urlopen|ftplib|smtplib|webbrowser"
  ```

**Resultado esperado: nenhuma linha.** Esses são os recursos que um programa em Python usaria para acessar
a internet, enviar e-mails ou abrir sites — e nenhum deles aparece no código.

### Para equipes de TI e segurança

- **Único programa externo chamado:** o `tesseract`, leitor de imagens (OCR) que roda no próprio
  computador. Confira com `grep -rn "subprocess.run" scripts/` — são 3 linhas, todas executando o caminho
  do tesseract (definido na função `_tesseract()` de `scripts/detectores/imagem.py`), sem `shell=True`.
- **Nada de código dinâmico ou ofuscado:** `grep -rnE "eval\(|exec\(" scripts/` e
  `grep -rniE "base64|marshal|pickle" scripts/` não retornam nenhuma linha.
- **Dependências:** só bibliotecas públicas e amplamente usadas — PyMuPDF (`fitz`), lxml e Pillow (`PIL`),
  além da python-docx, usada nos testes. O restante é a biblioteca padrão do Python.
- **Prova com a rede bloqueada pelo próprio sistema (Mac):**
  ```bash
  sandbox-exec -p '(version 1)(allow default)(deny network*)' python3 scripts/verificar.py exemplos/injecao_branco.pdf
  ```
  A análise roda normalmente (veredito CRÍTICO) com o acesso à rede proibido pelo macOS. Para ver que o
  bloqueio funciona de verdade, tente acessar a internet com o mesmo prefixo — dá erro:
  ```bash
  sandbox-exec -p '(version 1)(allow default)(deny network*)' python3 -c "import urllib.request; urllib.request.urlopen('https://example.com')"
  ```
- **No Windows:** crie no Firewall do Windows uma regra de saída que bloqueie o `python.exe` e use a
  ferramenta normalmente.
- **O que ela grava:** só o que você pedir (laudo, resumo da pasta, cópias higienizadas), na pasta que
  você escolher. Durante o OCR, cria arquivos temporários acessíveis só pelo seu usuário e os apaga ao final.

**Encontrou algo suspeito?** Avise pela aba **Issues** deste repositório ou por
[@sophismart.ai](https://instagram.com/sophismart.ai). Transparência total faz parte da ferramenta.

## ⚖️ Licença e proibições

Distribuído sob **Licença de Uso Público, Não Comercial e Sem Derivações** — em
espírito, equivalente à **CC BY-NC-ND 4.0**. Leia o arquivo [LICENSE](LICENSE).

**✅ Você PODE:** usar, executar e **redistribuir/compartilhar a cópia íntegra,
de graça** — inclusive dentro de tribunais e entre colegas. É incentivado.

**⛔ É EXPRESSAMENTE PROIBIDO:**
- **VENDER** ou comercializar a ferramenta, no todo ou em parte;
- **MODIFICAR / ALTERAR** ou criar versões derivadas, e distribuí-las;
- **REMOVER** os créditos de autoria ou esta licença;
- Apresentar a obra como de terceiro.

**Embasamento jurídico (Brasil):** Constituição Federal art. 5º, XXVII;
Lei nº 9.610/1998 (Direitos Autorais — arts. 22, 24, 29, 49); Lei nº 9.609/1998
(Programa de Computador — art. 2º e §1º, e art. 12, que tipifica como **crime** a
violação de direitos de autor de software, com pena agravada para fins de
comércio). O direito de opor-se a alterações não autorizadas e o de ter a autoria
reconhecida sustentam, respectivamente, a proibição de modificar e a exigência de
crédito. Detalhes e citações em [LICENSE](LICENSE).

Uso comercial ou qualquer exceção depende de **autorização prévia e expressa** do
titular — contato em [AUTORIA.md](AUTORIA.md).

## 👤 Autoria

Criado e mantido por **Murilo Ferreira** ([@agro_muriloferreira](https://instagram.com/agro_muriloferreira))
e **Sophismart.ai** ([@sophismart.ai](https://instagram.com/sophismart.ai)).
© 2026. Todos os direitos reservados nos termos da [LICENSE](LICENSE).

## ⚠️ Aviso importante

Ferramenta de **auxílio técnico**. **Não substitui** o exame nem o juízo humano,
nem a intimação da parte prevista em lei. Um veredito "LIMPO" indica ausência de
**vetores conhecidos**, não garantia absoluta.

---

<p align="center"><em>Feito com respeito ao trabalho de quem cuida da Justiça brasileira. 🇧🇷</em></p>
