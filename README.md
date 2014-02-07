# ScriptBattle

Projeto de Sistemas Distribuídos. Implementação de um jogo *multiplayer* de
batalha por scripts.

# Instruções

## Dependências

* Git: `sudo apt-get install git`
* Python 3: `sudo apt-get install python3`
* Sqlite 3 (Banco de Dados): `sudo apt-get install sqlite3`
* PyQt4 (Interface Gráfica): `sudo apt-get install python3-pyqt4`

## Clonar

`git clone https://github.com/edupinhata/naval_gunbound_war`

## Atualizar

`cd naval_gunbound_war`

`git pull`

## Executar

### Servidor

* Executar: `./server.py`
* Ver opções: `./server.py -h`

### Cliente

* Executar: `./client.py`
* Ver opções: `./client.py -h`

# API HTTP

## GET /game

Obtém todos os URNs dos objetos presentes no jogo.

* Entrada: Nenhum
* Código de retorno: `200 OK`
* Saída: Vetor JSON: `string`

Exemplo:

```json
[
    "player1",
    "player2",
    "projectile1",
    "rock1",
    "rock2",
    "rock3"
]
```

## POST /game

Recebe um nome único, uma senha para modificações, e o script do jogador, e
cria um recurso de URI `/game/[nome]` no servidor. A URN é retornada no campo
`Location` do cabeçalho HTTP de retorno.

* Entrada: Objeto JSON
 * `name`: `string`
 * `password`: `string`
 * `script`: `string`
* Código de retorno: `201 Created`
* Saída: Nenhum

Exemplo:

```json
{
    "name": "player1",
    "password": "123456",
    "script": "import random
               attributes['movx'] = random.randrange(-1, 2)"
}
```

## GET /game/[nome]

Obtém os atributos correspondentes a um objeto.

* Entrada: Nenhum
* Código de retorno: `200 OK`
* Saída: Objeto JSON
 * `hp`: `int`
 * `type`: `string`
 * `posx`: `int`
 * `posy`: `int`
 * `movx`: `int`
 * `movy`: `int`
 * `lookx`: `int`
 * `looky`: `int`
 * `shots`: `int`
 * `shooting`: `boolean`
 * `kills`: `int`

Exemplo:

```json
{
    "hp": 5,
    "type": "rock",
    "posx": 5,
    "posy": 10,
    "movx": 0,
    "movy": 0,
    "lookx": -1,
    "looky": 1,
    "shots": 0,
    "shooting": false,
    "kills": 0
}
```

## PUT /game/[nome]

Recebe a senha para modificações e um script para substituir o antigo.

* Entrada: Objeto JSON
 * `password`: `string`
 * `script`: `string`
* Código de retorno: `202 Accepted`
* Saída: Nenhum

Exemplo:

```json
{
    "password": "123456",
    "script": "import random
               attributes['movy'] = random.randrange(-1, 2)"
}
```

## DELETE /game/[nome]

Recebe a senha para modificações e remove o jogador.

* Entrada: Objeto JSON
 * `password`: `string`
* Código de retorno: `204 No Content`
* Saída: Nenhum

Exemplo:

```json
{
    "password": "123456",
}
```

