---
name: raio-x-documental
description: >
  Detecta texto oculto e comandos de prompt injection dentro de documentos (branco-no-branco,
  fonte invisível, caracteres Unicode escondidos, metadados) — defensivo, 100% offline, sem enviar
  o arquivo a lugar nenhum. Use ao conferir laudos, petições, contratos ou qualquer documento antes
  de usar IA: "verifica esse documento", "tem prompt injection nesse PDF?", "esse laudo tem texto
  escondido?". Emite laudo formal nos padrões do Judiciário. NÃO altera o arquivo original.
---

# raio-x-documental

Verifica documentos em busca de conteúdo oculto e prompt injection. Determinístico e offline.

## Fluxo

1. Checar dependências: `python3 ~/.claude/skills/raio-x-documental/scripts/verificar.py --doctor`
2. Verificar um arquivo (e gerar laudo):
   `python3 ~/.claude/skills/raio-x-documental/scripts/verificar.py <arquivo> --laudo <dir_saida>`
3. Ler o veredito no terminal e o laudo HTML gerado. Exit code 1 = CRÍTICO/ALTO.
4. NÃO alterar o original.
5. Se o documento não vier LIMPO, a pessoa pode, **se quiser**, gerar uma cópia higienizada (sempre em
   arquivo `.txt` separado — o original nunca é tocado):
   `python3 ~/.claude/skills/raio-x-documental/scripts/verificar.py <arquivo> --higienizar <dir_saida> --modo ambos`
   - `--modo neutralizar`: cópia com só o texto visível, sem o conteúdo oculto — segura para colar numa IA.
   - `--modo revelar`: o conteúdo oculto decodificado, exatamente o que estava escrito no trecho malicioso.
   - `--modo ambos` (padrão): gera as duas cópias.

## Formatos: PDF, TXT/MD, DOCX/DOC, ODT, RTF, HTML/e-mail, imagens (PNG/JPG/TIFF) e PDF escaneado.

## Modo pasta

O caminho passado também pode ser uma PASTA. Nesse caso só os documentos que estão DIRETAMENTE
dentro dela são analisados: subpastas nunca são abertas automaticamente, e atalhos/links que apontem
para fora da pasta selecionada nunca são seguidos. Os resultados (inclusive os maliciosos/suspeitos)
são resumidos no terminal e, com `--laudo <dir_saida>`, em `resumo_da_pasta.html`/`.json` dentro do
diretório de saída, com um laudo individual por documento suspeito.

## Integridade e autoria
`python3 ~/.claude/skills/raio-x-documental/scripts/verificar.py --verificar-integridade` confere os arquivos da skill contra `INTEGRIDADE.sha256`.
Autoria e licença (uso público, não comercial, sem derivações): ver `README.md`, `LICENSE` e `AUTORIA.md` na raiz da skill.
