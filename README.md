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
o campo `If-Modified-Since`, especificando uma data superior ao `timestamp` de
modificação do recurso. Isto permite que clientes façam requisições
continuamente sem sobrecarregar suas redes.

## Recursos e Métodos

### POST /game

Cria um recurso `[token]` no servidor correspondente a um jogador. É acessível
através de `/game/[token]`, que é retornado no campo `Location` do cabeçalho
HTTP de retorno. Requer uma senha para que o criador faça modificações depois.

* Entrada: Objeto
 * `name`: string, opcional
 * `password`: string
* Código de retorno: `201 Created`.
* Saída: Nenhum.

#### Exemplo

```sh
$ curl --verbose --request POST --data '{"name": "top", "password": "kek"}' localhost:8000/game
[...]
< Location: /game/abc123
```

### GET /game/[token]

Obtém os atributos correspondentes a um jogador.

* Entrada: Nenhum
* Código de retorno: `200 OK`
* Saída: Objeto
 * `name`: string
 * `hp`: int
 * `position`: Objeto
  * `x`: int
  * `y`: int
 * `movement`: Objeto
  * `x`: int
  * `y`: int
 * `combat`: Objeto
  * `x`: int
  * `y`: int

#### Exemplo

```sh
$ curl --request GET localhost:8000/game/abc123
{"name": "top", "combat": {"y": 0, "x": 0}, "movement": {"y": 0, "x": 0}, "position": {"y": 0, "x": 0}, "hp": 10}
```

### PUT /game/[token]

Atualiza, do jogador, atributos passados como entrada. Requer a senha usada
para criação.

* Entrada: Objeto
 * `password`: string
 * `movement`: Objeto, opcional
  * `x`: int, opcional
  * `y`: int, opcional
 * `combat`: Objeto, opcional
  * `x`: int, opcional
  * `y`: int, opcional
* Código de retorno: `202 Accepted`
* Saída: Nenhum

#### Exemplo

```sh
$ curl --request PUT --data '{"password": "kek", "combat": {"x": 1, "y": -1}}' localhost:8000/game/abc123
$ curl --request GET localhost:8000/game/abc123
{"name": "top", "combat": {"y": -1, "x": 1}, "movement": {"y": 0, "x": 0}, "position": {"y": 0, "x": 0}, "hp": 10}
```

### GET /game

* Entrada: Nenhum
* Código de retorno: `200 OK`
* Saída: Vetor: string

Obtém todos os `[token]`s representando cada jogador presente.

#### Exemplo

```sh
$ curl --request GET localhost:8000/game
["abc123", def456"]
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

`cd servidor`

`./server [porta]`

### Cliente

Ainda não implementado.

