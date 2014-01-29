# naval_gunbound_war

Projeto de Sistemas Distribuídos. Implementação de um batalha naval distribuído.

# Dependências

* Python 3

# API RESTful

## Entradas e Saídas

Uma entrada é o corpo do pacote de requisição e uma saída é o corpo do pacote
de resposta. Todas entradas e saídas são em formato JSON, podendo ser objetos
(`{}`) ou vetores (`[]`) com variados atributos dependendo do recurso e do
método.

## Long Polling

Recursos acessados pelo método GET bloqueiam a requisição se o cabeçalho tiver
o campo `If-Modified-Since`, especificando uma data igual ou superior ao
`timestamp` de modificação do recurso. Isto permite que clientes façam
requisições continuamente sem sobrecarregar a rede.

## Recursos e Métodos

### POST /game

Cria um recurso `[token]` no servidor correspondente a um jogador. É acessível
através de `/game/[token]`, que é retornado no campo `Location` do cabeçalho
HTTP de retorno. Requer uma senha para que o criador faça modificações depois.

* Entrada: Objeto
 * `name`: string, opcional
 * `password`: string
* Código de retorno: `201 Created`
* Saída: Nenhum
* Exemplo:

```sh
$ curl --verbose --request POST --data '{"name": "top", "password": "kek"}' localhost:8000/game
# ...
< Location: abc123
```

### GET /game/[token]

Obtém os atributos correspondentes a um jogador.

* Entrada: Nenhum
* Código de retorno: `200 OK`
* Saída: Objeto
 * `name`: string
 * `hp`: int
 * `kills`: int
 * `posx`: int
 * `posy`: int
 * `movx`: int
 * `movy`: int
 * `lookx`: int
 * `looky`: int
* Exemplo:

```sh
$ curl --request GET localhost:8000/game/abc123
{"name": "top", "lookx": 0, "looky": 0, "movx": 0, "movy": 0, "posx": 0, "posy": 0, "hp": 10, "kills": 0}
$ curl --request GET --header 'If-Modified-Since: Mon, 01 Jan 2199 00:00:00 GMT' localhost:8000/game/abc123
# bloqueia até ter atualização
```

### PUT /game/[token]

Atualiza, do jogador, atributos passados como entrada. Requer a senha usada
para criação.

* Entrada: Objeto
 * `password`: string
 * `movement`: Objeto, opcional
 * `movx`: int, opcional
 * `movy`: int, opcional
 * `lookx`: int, opcional
 * `looky`: int, opcional
* Código de retorno: `202 Accepted`
* Saída: Nenhum
* Exemplo:

```sh
$ curl --request PUT --data '{"password": "kek", "lookx": 1, "movy": -1}' localhost:8000/game/abc123
$ curl --request GET localhost:8000/game/abc123
{"name": "top", "lookx": 1, "looky": 0, "movx": 0, "movy": -1, "posx": 0, "posy": 0, "hp": 10, "kills": 0}
```

### POST /game/[token]

Cria um recurso em `/game` que representa um projétil atirado pelo jogador.

* Entrada: Objeto
 * `password`: string
* Código de retorno: `201 Created`
* Saída: Nenhum
* Exemplo:

```sh
$ curl --request POST --data '{"password": "kek"}' localhost:8000/game/abc123
# ...
< Location: ghi789
$ curl --request GET localhost:8000/game/ghi789
{"name": "Projectile", "lookx": 1, "looky": 0, "movx": 1, "movy": 0, "posx": 1, "posy": 0, "hp": 1, "kills": 0}
```

### GET /game

Obtém todos os `[token]`s representando cada jogador presente.

* Entrada: Nenhum
* Código de retorno: `200 OK`
* Saída: Vetor: string
* Exemplo:

```sh
$ curl --request GET localhost:8000/game
["abc123", "def456"]
```

# Instruções

## Clonar

`sudo apt-get install git`

`git clone https://github.com/edupinhata/naval_gunbound_war`

## Atualizar

`cd naval_gunbound_war`

`git pull`

## Executar

### Servidor

* Rodar: `./server`

* Ver opções: `./server -h`

### Cliente

* Rodar: `./client`

* Ver opções: `./client -h`

