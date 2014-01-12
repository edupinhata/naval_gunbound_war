naval_gunbound_war
==================

Projeto de Sistemas Distribuídos. Implementação de um batalha naval distribuído.


Compilando o servidor
=====================

* Dependências: `git` `ant`

`sudo apt-get install git ant`

* Clonando o repositório:

`git clone https://github.com/edupinhata/naval_gunbound_war`

* Compilar:

`cd naval_gunbound_war/servidor`

`ant`

Testando o servidor
===================

* Dependência: `curl`

`sudo apt-get install curl`

* Rodar o servidor (porta 80 necessita de sudo) (bloqueia o terminal):

`sudo ant run`

* Criar um usuário no servidor (HTTP POST):

`TOKEN=$(curl -d "" "localhost/token")`

* Escutar mensagens direcionadas ao usuário do servidor (HTTP GET) (bloqueia o terminal):

`curl "localhost/stream?token=$TOKEN"`

* Enviar mensagens para todos os usuários do servidor (HTTP POST):

`curl -d "mensagem" "localhost/broadcast"`

RASCUNHO DO PROJETO
==============================

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

