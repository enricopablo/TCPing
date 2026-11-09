# Changelog

Todas as mudanças relevantes deste projeto são documentadas aqui.

O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o projeto adota o [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [0.4.0] - 2026-11-08

### Adicionado
- Vários alvos em uma execução: números são portas, o resto são hosts, e todas as combinações são testadas (`tcping web1 web2 80 443` = 4 alvos).
- Testes dos alvos em paralelo a cada rodada.
- Com mais de um alvo: tabela atualizada ao vivo (última latência, mín/méd/máx, jitter e histórico das últimas 10 tentativas) e resumo comparativo ao final.
- Validação das portas (1 a 65535) e mensagens de erro de uso para host ou porta ausentes.
- Novo módulo `target.py`.

### Alterado
- `-c` passa a ser o número de tentativas **por alvo**, e `-i` o intervalo entre rodadas.
- Código de saída `0` exige que **todos** os alvos tenham respondido ao menos uma vez. Com um alvo, nada muda.
- Host não encontrado em uma lista de alvos não interrompe os demais; a execução termina com código `2`.
- JSON: linhas `attempt` passam a incluir `host`, `ip` e `port`, e há um `summary` por alvo.

### Corrigido
- JSON: `jitter` saía como `0` (inteiro) com uma única tentativa; agora sai `0.0`.

## [0.3.0] - 2026-11-08

### Adicionado
- Código de saída igual ao `ping`: `0` se houve ao menos uma conexão bem-sucedida, `1` se nenhuma, `2` para erro de uso ou host não encontrado.
- Opção `--report` / `-r`: exibe só o cabeçalho e o relatório final, sem as tentativas.
- Opção `--json`: saída NDJSON com eventos `attempt`, `summary` e `error` (com `-r`, só `summary`).
- Testes automatizados com `pytest` (`uv run pytest`), sem dependência de internet.
- `--help`: exemplos de `-r` e `--json`.
- Atalho `-h` para `--help`.
- README: seção "Uso em Scripts e Automação" e tabela com os caminhos de instalação por sistema operacional.

### Alterado
- Exibição separada da medição (novo módulo `output.py`, com saída para terminal e JSON).
- Erro inesperado durante a execução encerra com código `2`, após exibir o resumo.

## [0.2.0] - 2026-11-08

### Adicionado
- Instalação como comando global `tcping` via `uv tool install` (direto do GitHub ou de um clone local).
- Opção `--version` / `-V`.
- Exemplos de uso no `--help`.
- Opções `-4` e `-6` para forçar IPv4 ou IPv6.
- Suporte a IPv6 (endereços exibidos como `[::1]:443`).
- IP resolvido exibido no cabeçalho, ex.: `google.com (142.250.79.46):443`.
- Execução via `python -m tcping`.

### Alterado
- Código reorganizado em pacote `src/tcping/` (`cli.py`, `probe.py`, `stats.py`). O `main.py` na raiz passa a ser apenas um atalho para `uv run main.py`.
- Projeto renomeado para `tcping`.
- O DNS é resolvido uma única vez antes dos testes: a latência agora mede apenas o handshake TCP.
- Falhas exibem o motivo real: `Recusada`, `Timeout`, `Rede inalcançável`, `Host inalcançável`.
- Host inexistente é informado uma vez ("Host não encontrado") e encerra com código 2.
- A tela do terminal não é mais limpa ao iniciar.
- README reescrito com as novas formas de instalação, atualização e remoção.

### Corrigido
- Latência exibida em tentativas que falharam (agora mostra `-`).
- Resumo mostrava `0.00 ms` de latência e jitter quando nenhuma tentativa teve sucesso (agora mostra `-`).
- Descrição da ferramenta ausente no `--help`.
- Cabeçalho exibia "1 tentativas" (agora "1 tentativa").
- README: badge de versão do Python (3.13+), comandos de instalação do `uv` com `\|` e erros de digitação.

### Removido
- Gravação de logs em arquivo (pasta `logs/`) e a opção `--output` / `-o`.
- Instruções de alias (`tping`) no README, substituídas pela instalação via `uv tool`.

## [0.1.0] - 2026-03-07

### Adicionado
- Primeira versão: script `main.py` executado com `uv run`.
- Teste de conectividade TCP com latência, mínimo, médio, máximo e jitter.
- Opções `--count`, `--interval`, `--timeout` e `--output`.
- Logs em `logs/tcp_ping_HOST_PORTA.log`, em modo append.
- Limpeza da tela ao iniciar (Windows e Unix).
- Interface com `rich` e uso via alias `tping`.

[0.4.0]: https://github.com/enricopablo/TCP-Ping/compare/781c1da...HEAD
[0.3.0]: https://github.com/enricopablo/TCP-Ping/compare/781c1da...HEAD
[0.2.0]: https://github.com/enricopablo/TCP-Ping/compare/781c1da...HEAD
[0.1.0]: https://github.com/enricopablo/TCP-Ping/tree/781c1da
