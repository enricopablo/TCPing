# 🚀 TCPING — TCP Ping Tool (Python + UV)

🇺🇸 [English](README.md) | 🇧🇷 **Português**

Uma ferramenta de linha de comando (CLI) robusta para testar a conectividade de portas **TCP**. Diferente do ping tradicional (ICMP), esta ferramenta valida se serviços específicos (Web, SSH, Banco de Dados, etc.) estão aceitando conexões, fornecendo métricas de latência e estabilidade.

![Python](https://img.shields.io/badge/Python-3.13+-blue?logo=python)
![UV](https://img.shields.io/badge/Managed%20by-UV-purple?logo=python)
![OS](https://img.shields.io/badge/OS-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)

<img width="794" height="395" alt="print-windows" src="https://github.com/user-attachments/assets/c6129d03-b8c3-4003-9165-b621e619f4f3" />

## ✨ Funcionalidades

* **Handshake TCP:** Mede o tempo de resposta real da aplicação (SYN/SYN-ACK).
* **Estatísticas Avançadas:** Média, Mínimo, Máximo e **Jitter** (variação da latência).
* **Modo Contagem (`-c`):** Defina um limite de disparos ou rode infinitamente.
* **Vários alvos:** Diversos hosts e portas de uma vez, testados em paralelo.
* **Pronto para scripts:** Códigos de saída como os do `ping` e saída em JSON.
* **Instalável como comando:** Via `uv tool`, disponível em qualquer terminal como `tcping`.
* **Interface Rica:** Utiliza a biblioteca `Rich` para tabelas e cores no terminal.

---

## 🛠️ Pré-requisitos

* **`uv`** (gerenciador de pacotes Python ultra-rápido): obrigatório.
* **Git**: necessário para instalar direto do GitHub (`git+https://...`) ou via clone. Sem ele, use a [instalação sem Git](#instalação-sem-git).

### uv

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Ou, em qualquer sistema, via `pip`:

```bash
pip install uv
```

### Git

Confira se já está instalado com `git --version`. Se não estiver:

| Sistema | Comando |
|---|---|
| **Debian / Ubuntu / Linux Mint** | `sudo apt install git` |
| **Fedora** | `sudo dnf install git` |
| **macOS** | `xcode-select --install` |
| **Windows** | `winget install --id Git.Git -e` |

## 📦 Instalação

Direto do GitHub, sem precisar clonar:

```bash
uv tool install git+https://github.com/enricopablo/TCPing
```

Ou a partir de um clone local:

```bash
git clone https://github.com/enricopablo/TCPing.git
cd TCPing/
uv tool install --force .
```

### Instalação sem Git

Se o Git não estiver instalado (erro `Git executable not found`), instale a partir do `.zip` do GitHub:

```bash
uv tool install "tcping @ https://github.com/enricopablo/TCPing/archive/refs/heads/main.zip"
```

Pronto! O comando `tcping` fica disponível em qualquer terminal (macOS, Linux e Windows).

> Se o terminal não encontrar o comando, rode `uv tool update-shell` e abra um novo terminal.

### 📍 Onde o `tcping` fica instalado

O `uv tool` instala o executável (que precisa estar no `PATH`) e um ambiente isolado com o código e as dependências:

| Sistema | Executável | Ambiente isolado |
|---|---|---|
| **Windows** | `%USERPROFILE%\.local\bin\tcping.exe` | `%APPDATA%\uv\data\tools\tcping\` |
| **macOS** | `~/.local/bin/tcping` | `~/.local/share/uv/tools/tcping/` |
| **Linux** | `~/.local/bin/tcping` | `~/.local/share/uv/tools/tcping/` |

Esses caminhos podem mudar conforme variáveis de ambiente (`UV_TOOL_BIN_DIR`, `UV_TOOL_DIR`, `XDG_BIN_HOME`, `XDG_DATA_HOME`). Para conferir na sua máquina:

```bash
uv tool dir --bin   # pasta do executável
uv tool dir         # pasta dos ambientes isolados
```

Para testar sem instalar nada (requer Git):

```bash
uvx --from git+https://github.com/enricopablo/TCPing tcping google.com 443
```

### Atualizar / Remover

```bash
uv tool upgrade tcping      # instalado via GitHub (git+https)
uv tool install --force .   # instalado via clone (após git pull)
uv tool uninstall tcping
```

Instalado sem Git (`.zip`)? Para atualizar, repita o comando de instalação com `--force --reinstall`:

```bash
uv tool install --force --reinstall "tcping @ https://github.com/enricopablo/TCPing/archive/refs/heads/main.zip"
```

## 🚀 Como Usar

```bash
tcping <host...> <porta...> [opções]
```

Exemplos:

```bash
# Teste básico (roda até você apertar Ctrl+C)
tcping google.com 443

# 10 tentativas com intervalo de 0.5s
tcping 1.1.1.1 80 -c 10 -i 0.5

# Só o relatório final, sem as tentativas
tcping google.com 443 -c 5 -r
```

### 🎯 Vários Alvos

Informe quantos hosts e portas quiser: **números são portas, o resto são hosts**. O `tcping` testa todas as combinações, **em paralelo**:

```bash
tcping web1 web2 443          # 2 alvos: web1:443, web2:443
tcping google.com 80 443      # 2 alvos: google.com:80, google.com:443
tcping web1 web2 80 443       # 4 alvos: todas as combinações
```

Com mais de um alvo, a saída vira uma tabela atualizada ao vivo, com a última latência, estatísticas e o histórico das últimas 10 tentativas de cada alvo. Ao final é exibido um resumo comparativo.

- `-c` define quantas tentativas **cada alvo** recebe; `-i` é o intervalo entre o início de uma rodada e o da seguinte (como no `ping`). Se uma rodada demorar mais que `-i`, a próxima começa em seguida.
- Um host não encontrado é informado e os demais continuam sendo testados.

## 🤖 Uso em Scripts e Automação

### Código de saída

Igual ao `ping`, o `tcping` informa o resultado pelo código de saída:

| Código | Significado |
|---|---|
| `0` | Todos os alvos tiveram ao menos uma conexão bem-sucedida |
| `1` | Algum alvo não teve nenhuma conexão bem-sucedida |
| `2` | Erro de uso (inclusive valores inválidos de `-c`, `-i` e `-t`) ou host não encontrado |

Com um único alvo, isso equivale a: `0` se ele respondeu ao menos uma vez, `1` se não respondeu nenhuma.

```bash
tcping db.local 5432 -c 3 -r && ./deploy.sh              # só faz o deploy se o banco responder
tcping db.local 5432 -c 3 -r || echo "Banco fora!"        # alerta se não responder
tcping web1 web2 db 443 5432 -c 3 -r && ./deploy.sh      # só se TODOS os alvos responderem
```

### Saída JSON (`--json`)

Cada evento vira uma linha JSON ([NDJSON](https://github.com/ndjson/ndjson-spec)), identificada pelo campo `type`:

```bash
tcping google.com 443 -c 2 --json
```

```json
{"type": "attempt", "host": "google.com", "ip": "142.250.219.206", "port": 443, "seq": 1, "timestamp": "2026-11-08T21:32:39", "status": "open", "latency_ms": 17.52, "error": null}
{"type": "attempt", "host": "google.com", "ip": "142.250.219.206", "port": 443, "seq": 2, "timestamp": "2026-11-08T21:32:40", "status": "closed", "latency_ms": null, "error": "Timeout"}
{"type": "summary", "host": "google.com", "ip": "142.250.219.206", "port": 443, "family": "ipv4", "attempts": 2, "success": 1, "failed": 1, "success_rate": 50.0, "latency_ms": {"min": 17.52, "avg": 17.52, "max": 17.52, "jitter": 0.0}, "duration_s": 2.24}
```

- Com vários alvos, há uma linha `summary` **por alvo**, no fim; o campo `seq` é o número da rodada.
- Com `-r`, apenas as linhas `summary` são emitidas.
- Host não encontrado gera `{"type": "error", ..., "error": "Host not found"}` com código de saída `2`; os demais alvos continuam.
- Valores ausentes (latência de uma falha, latência sem nenhum sucesso) são `null`.

```bash
tcping google.com 443 -c 5 --json -r | jq .latency_ms.avg   # latência média
tcping google.com 443 --json >> historico.jsonl             # monitoramento contínuo
```

## 📊 Opções da CLI

```text
Opção       Atalho  Descrição                                   Padrão
--count     -c      Tentativas por alvo (0 = infinito)          0
--interval  -i      Intervalo entre rodadas (segundos, >= 0)    1.0
--timeout   -t      Tempo limite por tentativa (segundos, > 0)  2.0
            -4      Força o uso de IPv4                         -
            -6      Força o uso de IPv6                         -
--report    -r      Exibe só o relatório final                  -
--json              Saída em JSON (uma linha por evento)        -
--version   -V      Exibe a versão instalada                    -
--help      -h      Exibe a ajuda                               -
```

### 🔍 Entendendo a Saída

Ao executar o `tcping`, a ferramenta realiza o **Three-Way Handshake do TCP**. A latência exibida é o tempo decorrido entre o envio do `SYN` e o recebimento do `SYN-ACK`.

O nome do host é resolvido (DNS) **uma única vez**, antes do primeiro teste, então o tempo de DNS não entra na latência. O IP resolvido aparece no cabeçalho, ex.: `google.com (142.250.79.46):443`. IPv4 e IPv6 são suportados; use `-4` ou `-6` para forçar um deles.

A saída do programa é em inglês:

- 🟢 `OPEN`: o serviço respondeu e a conexão foi aceita.

- 🔴 `CLOSED`: a conexão falhou. O motivo aparece entre parênteses:
  - `Refused`: o host respondeu, mas nenhum serviço escuta nessa porta.
  - `Timeout`: sem resposta dentro do tempo limite (geralmente firewall descartando pacotes).
  - `Network unreachable` / `Host unreachable`: não há rota até o destino.

- `Host not found`: o nome não pôde ser resolvido (DNS).

- `Jitter`: variação na latência. Valores altos indicam instabilidade na rota ou sobrecarga no host.

## 📂 Estrutura do Projeto

```text
.
├── src/tcping/
│   ├── __init__.py   # Versão do pacote
│   ├── __main__.py   # Permite `python -m tcping`
│   ├── cli.py        # Interface de linha de comando (click) e loop de tentativas
│   ├── output.py     # Exibição: terminal (rich) ou JSON
│   ├── probe.py      # Resolução de DNS e teste de conexão TCP
│   ├── stats.py      # Estatísticas e resumo da execução
│   └── target.py     # Alvos: interpretação dos argumentos e estatísticas por alvo
├── tests/            # Testes automatizados (pytest)
├── main.py           # Atalho: `uv run main.py <host> <porta>`
├── CHANGELOG.md      # Histórico de versões (em inglês)
├── pyproject.toml    # Configurações do projeto e do comando `tcping`
├── uv.lock           # Trava de versões de dependências
├── README.md         # Documentação (inglês)
└── README.pt-BR.md   # Documentação (português)
```

## 🧑‍💻 Desenvolvimento

```bash
uv sync                               # cria o ambiente com as dependências
uv run tcping google.com 443          # roda a versão do código local
uv run pytest                         # roda os testes (não precisa de internet)
uv tool install --editable --force .  # (opcional) `tcping` global refletindo o código local
```

---
<p align="center">Obviamente feito com 🤖, engenhosidade humana 🤷🏻‍♂️ e uma quantidade suspeita de tokens 🔥.</p>
