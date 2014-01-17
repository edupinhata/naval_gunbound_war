# naval_gunbound_war

Projeto de Sistemas Distribuídos. Implementação de um batalha naval distribuído.

# Dependências

* Python 3

# API RESTful

## Entradas e Saídas

Toda entrada/saída é um objeto JSON contendo um ou mais atributos pertencentes a
um jogador. Estes atributos podem ser usados, dependendo do método, para adição,
atualização ou remoção de jogadores no servidor.

### Exemplo

```json
{
    "name": "",
    "hp": "",
    "position": {
        "x": 0,
        "y": 0,
    },
    "movement": {
        "x": 0,
        "y": 0,
    },
    "combat": {
        "x": 0,
        "y": 0,
    },
    "delete": false
}
```

## Recursos e Métodos

### POST /game

Cria um recurso `[token]` no servidor correspondente a um jogador. É acessível
através de `/game/[token]`, que é retornado no campo `Location` do cabeçalho
HTTP de retorno.

* Atributos de entrada: `name`
* Código de retorno: `201 Created`

#### Exemplo

```sh
$ curl --verbose --request POST --data '{"name": "foo"}' localhost:8000/game
[...]
< Location: /game/abcdef0123456789
```

### GET /game/[token]

Obtém os atributos correspondentes a um jogador.

* Código de retorno: `200 OK`
* Atributos de saída: Todos

#### Exemplo

```sh
$ curl --request GET localhost:8000/game/abcdef0123456789
{"name": "foo", "combat": {"y": 0, "x": 0}, "movement": {"y": 0, "x": 0}, "position": {"y": 0, "x": 0}, "hp": 10}
```

### PUT /game/[token]

Atualiza, do jogador, atributos passados como entrada.

* Atributos de entrada: `movement` `combat`
* Código de retorno: `202 Accepted`

#### Exemplo

```sh
$ curl --request PUT --data '{"combat": {"x": 1, "y": -1}}' localhost:8000/game/abcdef0123456789
$ curl --request GET localhost:8000/game/abcdef0123456789
{"name": "foo", "combat": {"y": -1, "x": 1}, "movement": {"y": 0, "x": 0}, "position": {"y": 0, "x": 0}, "hp": 10}
```

### GET /game

* Código de retorno: `200 OK`
* Atributos de saída: Todos

Este método acessa a próxima atualização de atributos de qualquer jogador,
incluindo adição ou remoção de jogadores. A requisição é bloqueada pelo servidor
até que haja uma atualização, efetivamente implementando *polling* no lado do
servidor. Espera-se que clientes continuamente solicitem (através de por exemplo
*threads*) este recurso para se atualizarem.

#### Exemplo

1. ```sh
   $ while true; do curl --request GET localhost:8000/game; done
   ```

2. ```sh
   $ curl --request POST --data '{"name": "foo"}' localhost:8000/game
   $ curl --request POST --data '{"name": "bar"}' localhost:8000/game
   $ curl --request PUT --data '{"combat": {"x": 1, "y": -1}}' localhost:8000/game/abcdef0123456789
   ```

1. ```sh
   {"name": "foo", "combat": {"y": 0, "x": 0}, "movement": {"y": 0, "x": 0}, "position": {"y": 0, "x": 0}, "hp": 10}
   {"name": "bar", "combat": {"y": 0, "x": 0}, "movement": {"y": 0, "x": 0}, "position": {"y": 0, "x": 0}, "hp": 10}
   {"name": "foo", "combat": {"y": 1, "x": -1}, "movement": {"y": 0, "x": 0}, "position": {"y": 0, "x": 0}, "hp": 10}
   ```

### DELETE /game/[token]

Remove do servidor o recurso que representa o jogador.

#### Exemplo

```sh
$ curl --request DELETE localhost:8000/game/abcdef0123456789
$ curl --verbose --request GET localhost:8000/game/abcdef0123456789
[...]
< HTTP/1.0 404 Not Found
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

