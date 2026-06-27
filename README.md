# ⚔️ Bot Discord — Albion Online

Bot de gerenciamento de grupos para guildas de Albion Online. Permite criar pings de conteúdo (DGs, eventos) com seleção de funções, sistema de fila automática e gerenciamento de membros.

---

## 📋 Funcionalidades

- Ping de conteúdo com título, tier, data/hora e classes personalizadas
- Botões dinâmicos para seleção de função
- **1 membro por função** — quem chegar depois entra na fila automaticamente
- Fila visível no embed em tempo real
- Promoção automática da fila quando alguém sai
- Gerenciamento manual pelo criador do ping (add/rem/fechar)

---

## 🚀 Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/matheussantos-web/bot-discord-albion.git
cd bot-discord-albion
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Crie o arquivo `.env`
```env
TOKEN=SEU_TOKEN_AQUI
```

### 4. Configure o `config.py`
```python
CANAL_DG = 'content-ping'  # nome do canal onde o bot vai mandar os pings
GUILD_NOME = 'NOME DA SUA GUILDA'
```

### 5. Rode o bot
```bash
py main.py
```

---

## 🤖 Comandos

| Comando | Descrição |
|---|---|
| `!content titulo / tier / data / hora / CLASSE1 CLASSE2 ...` | Cria ping com data e hora |
| `!content titulo / tier / CLASSE1 CLASSE2 ...` | Cria ping para agora |
| `!add @membro CLASSE` | Adiciona membro a uma função |
| `!rem @membro` | Remove membro do conteúdo ou da fila |
| `!fechar` | Encerra o conteúdo ativo |

### Exemplos
```
!content DG AVA / 8.4 / 25/06 / 14:00 / TANK HEAL SILENCE REPETIDOR ELEVADO
!content DG RANDOM / 7.3 / TANK HEAL DPS
!add @João TANK
!rem @João
!fechar
```

---

## 📁 Estrutura do projeto

```
bot-discord-albion/
├── main.py          # Inicialização do bot
├── config.py        # Configurações (canal, nome da guilda)
├── .env             # Token do bot (não versionar!)
├── requirements.txt
└── cogs/
    ├── content.py   # Comando !content, embed e botões
    └── gerenciar.py # Comandos !add, !rem, !fechar
```

---

## ⚙️ Requisitos

- Python 3.10+
- discord.py
- python-dotenv

---

## ⚠️ Observações

- O canal `content-ping` precisa existir no servidor
- O cargo do bot precisa estar acima dos membros no servidor
- Nunca suba o arquivo `.env` para o GitHub
- Ao resetar o token, atualiza o `.env` imediatamente

---

## 👤 Autor

Desenvolvido por **Teaga**
