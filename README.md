# naval_gunbound_war

Projeto de Sistemas Distribuídos. Implementação de um batalha naval distribuído.

# Dependências

* Python 3

# API RESTful

## Entradas e Saídas

Toda entrada/saída é um objeto JSON contendo atributos de um jogador.

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

### /game

1. POST

 * Atributos de entrada: `name`
 * Código de retorno: `201 Created`

Cria um recurso no servidor correspondente a um jogador. É acessível através de
`/game/<token>`, que é especificado no campo `Location` do cabeçalho de retorno,
junto com o código de retorno.

Exemplo:

```json
$ curl --verbose --data '{"name": "foo"}' localhost:8000/game
...
HTTP/1.0 201 Created
...
Location: /game/abcdefghijklmnopqrstuvwxyz0123456789
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
`./server``[porta]`

### Cliente

# RASCUNHO DO PROJETO

Atributos dos barcos
* mobilidade //quantos quadrados pode se movimenta
* vida //quanto de dano ele resiste
* itens //armas, escudos, itens de reparo
* tamanho do barco //comprimento do barco. Inicialmente de 1 a 5 quadrados
* orientação // se o barco está na orizontal ou vertical



Itens
- espaço //quanto de espaço ocupa no barco
ativar(); //se for uma arma, atira, se for um item de recuperação, recupera

Armas

