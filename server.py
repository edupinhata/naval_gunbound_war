#!/usr/bin/env python3

import socketserver
import http.server
import http.client
import email.utils
import collections
import threading
import functools
import argparse
import hashlib
import random
import json
import time
import sys
import os


# O servidor. Contém o recurso raíz, e um método para encontrar recursos a
# partir daquele.
class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):

    # Construtor. Cria um recurso raíz e um recurso simbolizando "não
    # encontrado".
    def __init__(self, address, port):
        socketserver.ThreadingMixIn.__init__(self)
        http.server.HTTPServer.__init__(self, (address, port), Handler)
        self.root = Resource()
        self.not_found = Resource({'code': http.client.NOT_FOUND})

    # Método para encontrar um recurso dado um caminho, separado por '/'.
    # Se não encontrá-lo, devolve o recurso "não encontrado". Por exemplo, para
    # encontrar o recurso /game/abc123, procura-se o recurso "game" no recurso
    # raíz, e nele o recurso "abc123".
    def find_resource(self, path):
        path_list = path.split('/')
        path_list.pop(0)

        res = self.root
        for name in path_list:
            try:
                res = res.children[name]
            except KeyError:
                return self.not_found
        return res


# Esta classe é instanciada para cada requisição feita ao servidor, e é
# responsável por ler os dados de entrada, tratá-los e enviar a resposta.
# Neste programa, cada recurso é responsável por tratar requisições feitas a si
# mesmo, então o tratamento consiste em chamar o método correspondente no
# recurso e enviar como resposta o retorno.
class Handler(http.server.BaseHTTPRequestHandler):

    # Trata uma requisição GET.
    def do_GET(self):
        self.reply(self.server.find_resource(self.path).do_GET(self.read()))

    # Trata uma requisição POST.
    def do_POST(self):
        self.reply(self.server.find_resource(self.path).do_POST(self.read()))

    # Trata uma requisição PUT.
    def do_PUT(self):
        self.reply(self.server.find_resource(self.path).do_PUT(self.read()))

    # Lê o corpo da mensagem formatado como JSON e devolve um dicionário
    # correspondente. Adiciona um campo timestamp correspondente à última
    # atualização do cliente. Recursos podem ou não fazer uso dele.
    def read(self):
        data = {}
        length = self.read_length()
        timestamp = self.read_timestamp()
        try:
            text = self.rfile.read(length).decode('utf-8')
            data = json.loads(text)
        except:
            pass
        finally:
            data.update({'timestamp': timestamp})
            return data

    # Lê o tamanho da mensagem no cabeçalho. Se não presente, assume 0.
    def read_length(self):
        h = 'Content-Length'
        return int(self.headers[h]) if h in self.headers else 0

    # Obtém o timestamp da requisição. Pode estar no cabeçalho, mas se não
    # estiver, usa a menor data possível para indicar que o cliente não tem
    # nenhum dado.
    def read_timestamp(self):
        field = 'If-Modified-Since'
        if field not in self.headers:
            return time.mktime(time.gmtime(0))
        return time.mktime(email.utils.parsedate((self.headers[field])))

    # Responde a requisição com um código de status, campos de cabeçalho e
    # corpo da mensagem, todos opcionais. O corpo da mensagem deve ser um
    # dicionário, a ser formatado como JSON para transmissão.
    def reply(self, args={}):
        response = {'code': http.client.OK, 'data': None, 'headers': []}
        response.update(args)

        code = response['code']
        headers = response['headers'] + [('Content-Type', 'text/json')]
        text = json.dumps(response['data'])

        try:
            self.send_response(code)

            for h in headers:
                self.send_header(h[0], h[1])
            self.end_headers()

            self.wfile.write(bytes(text, 'utf-8'))
        except:
            pass

    def log_message(self, format, *args):
        return

# Classe abstrata. Cada recurso tem um dicionário de recursos filhos, mapeados
# por um nome, ou caminho relativo. Sabem responder requisições feitas a ele.
# Tipicamente, uma requisição GET retorna os dados do recurso, POST cria um
# recurso filho nele, e PUT atualiza os dados.
class Resource:

    # Construtor. Define o código de retorno padrão como "método não
    # permitido". É esperado que subclasses sobrescrevam este comportamento.
    def __init__(self, default_reply={'code': http.client.METHOD_NOT_ALLOWED}):
        self.children = {}
        self.on_delete = None
        self.on_add_sibling = None
        self.default_reply = default_reply
        self.lock = threading.Lock()

    # Adiciona um recurso filho dado um nome do recurso, que é o caminho
    # relativo ao caminho deste recurso. Também faz com que, ao chamar o método
    # delete(), chame o método delete_child() deste objeto. É thread-safe pois
    # todas as operações são realizadas dentro de blocos de exclusão mútua.
    def add_child(self, name, resource):
        with self.lock:
            self.children[name] = resource
        with resource.lock:
            resource.on_add_sibling = self.add_child
            resource.on_delete = functools.partial(self.delete_child, name)

    # Delete um recurso filho. É thread-safe pois a operação é realizada dentro
    # de um bloco de exclusão mútua.
    def delete_child(self, name):
        with self.lock:
            if name in self.children:
                self.children.pop(name)

    # Adiciona um recurso irmão, chamando a função on_add_sibling, geralmente
    # setada pelo recurso pai no método add_child(). O método setado deve ser
    # thread-safe.
    def add_sibling(self, name, resource):
        if self.on_add_sibling:
            self.on_add_sibling(name, resource)

    # Deleta este recurso. Se tiver sido adicionado a um recurso pai através de
    # add_child(), chamará o método dele para remover este recurso, que é
    # thread-safe.
    def delete(self):
        if self.on_delete:
            self.on_delete()

    # Trata uma requisição GET. É thread-safe pois default_reply é imutável.
    def do_GET(self, data):
        return self.default_reply

    # Trata uma requisição POST. É thread-safe pois default_reply é imutável.
    def do_POST(self, data):
        return self.default_reply

    # Trata uma requisição PUT. É thread-safe pois default_reply é imutável.
    def do_PUT(self, data):
        return self.default_reply


# Classe abstrata que monitora sua data de atualização. Requisições GET de
# clientes que já tenham o recurso atualizado serão bloqueadas até que o evento
# sinalizando atualização seja disparado.
class Monitor(Resource):

    # Construtor. Define a última data de atualização como "agora".
    def __init__(self):
        Resource.__init__(self)
        self.timestamp = time.time()
        self.update_event = threading.Event()

    # Trata uma requisição GET, bloqueando se for necessário. Após a liberação,
    # retorna os dados do recurso. É thread-safe pois acessa o timestamp dentro
    # de um bloco de exclusão mútua. get_data() deve ser thread-safe.
    def do_GET(self, data):
        with self.lock:
            timestamp = self.timestamp
        if data['timestamp'] >= self.timestamp:
            self.update_event.wait()
        return {'data': self.get_data(),
                'headers': [('Last-Modified',
                             email.utils.formatdate(self.timestamp))]}

    # Atualiza o timestamp e dispara o evento sinalizando atualização. É
    # thread-safe pois tudo é realizado dentro de um bloco de exclusão mútua.
    def notify(self):
        with self.lock:
            self.timestamp = time.time()
            self.update_event.set()
            self.update_event.clear()

    # Método abstrato que obtém os dados do recurso. Deve ser thread-safe.
    def get_data(self):
        return None


# Recurso cujos dados são os recursos filhos, e os monitora por adições e
# remoções.
class Container(Monitor):

    # Implementado da superclasse. Retorna uma lista do caminho relativo de
    # cada recurso filho. É thread-safe pois acessos estão em um bloco de
    # exclusão mútua, e retorna uma nova lista.
    def get_data(self):
        with self.lock:
            return [name for name in self.children]

    # Ao adicionar um recurso filho, notifica por atualizações. É thread-safe
    # pois Resource.add_child() e Resource.notify() são.
    def add_child(self, path, resource):
        Resource.add_child(self, path, resource)
        self.notify()

    # Ao remover um recurso filho, notifica por atualizações.
    def delete_child(self, path):
        Resource.delete_child(self, path)
        self.notify()


# O jogo é um container cujo recursos filhos monitorados são os jogadores.
# Adicionalmente, executa sua lógica a cada intervalo de tempo.
class Game(Container, threading.Thread):

    # Construtor. Recebe o intervalo de tempo entre cada execução da lógica.
    def __init__(self, time_step):
        threading.Thread.__init__(self)
        Container.__init__(self)
        self.time_step = time_step

    # Cria um recurso filho (um jogador), validando dados de entrada. Como o
    # conjunto de jogadores foi alterado, dispara notificação ao final. É
    # thread-safe pois o método add_child é.
    def do_POST(self, data):
        if 'password' not in data:
            return {'code': http.client.EXPECTATION_FAILED}

        accepted = ['name']

        attributes={k: v for k, v in data.items() if k in accepted}
        password = data['password']

        p = Player(attributes, password)

        token = hashlib.md5(os.urandom(4096)).hexdigest()
        self.add_child(token, p)

        return {'code': http.client.CREATED,
                'headers': [('Location', token)]}


    # Sobrescrito de Thread. Executa operações pendentes e chama o método move
    # de cada jogador, fornecendo um dicionário de posições ocupadas por outros
    # jogadores. O próprio jogador então trata colisões com outros. É
    # thread-safe pois acesso aos jogadores é feito em um bloco de exclusão
    # mútua, e Player.move() é.
    def run(self):
        while True:
            time.sleep(self.time_step)

            occupied = self.get_occupied()
            with self.lock:
                players = self.children.copy().values()

            for p in players:
                p.do_pending()
                p.move(occupied)

    # Retorna um dicionário que mapeia para cada X um dicionário. Este mapeia,
    # para cada Y, um jogador. Substitui uma matriz. É thread-safe pois acesso
    # aos jogadores é feito em um bloco de exclusão mútua e Player.get_data()
    # é.
    def get_occupied(self):
        d = collections.defaultdict(dict)
        with self.lock:
            d.update({p.get_data()['posx']: {p.get_data()['posy']: p}
                      for p in self.children.copy().values()})
        return d


# Um jogador monitora seu estado, que é um conjunto de atributos. Quando
# requisições PUT ou POST são feitas, são setadas como pendentes até que o
# servidor dê o seu passo, para evitar sobrecarga de processamento.
class Player(Monitor):

    # Construtor. Recebe uma senha para modificações.
    def __init__(self, data, password):
        Monitor.__init__(self)
        self.password = password
        self.attributes = data
        self.pending_put = None
        self.pending_post = None
        self.update({'type': 'player', 'hp': 10, 'kills': 0,
            'posx': random.randrange(0, 20), 'posy': random.randrange(0, 20),
            'movx': 0, 'movy': 0, 'lookx': 1, 'looky': 1})

    # Implementado da superclasse. Uma requisição GET retorna os atributos do
    # jogador. É thread-safe pois usa exclusão mútua, e retorna uma cópia dos
    # atributos.
    def get_data(self):
        with self.lock:
            return self.attributes.copy()

    # Valida dados de entrada e chama atualização. Aceita apenas modificações
    # em movement e look, cujos valores devem ser entre -1 e 1. As mudanças só
    # são aplicadas quando o evento update_event for disparado, para evitar
    # recursão infinita de atualização no servidor -> atualização no cliente ->
    # mudança no cliente -> atualização no servidor... É thread-safe pois
    # update() é.
    def do_PUT(self, data):
        if 'password' not in data:
            return {'code': http.client.EXPECTATION_FAILED}
        if data['password'] != self.password:
            return {'code': http.client.FORBIDDEN}

        accepted = ['movx', 'movy', 'lookx', 'looky']
        with self.lock:
            self.pending_put = {k: v for k, v in data.items()
                    if k in accepted and v in range(-1, 2)}

        return {'code': http.client.ACCEPTED}

    # Cria um novo recurso a partir de um jogador, ou seja, um tiro. Também
    # depende do evento update_event. É thread-safe pois get_data() e
    # Resource.add_sibling() são.
    def do_POST(self, data):
        if 'password' not in data:
            return {'code': http.client.EXPECTATION_FAILED}
        if data['password'] != self.password:
            return {'code': http.client.FORBIDDEN}

        p = Projectile(self)
        token = hashlib.md5(os.urandom(4096)).hexdigest()
        with self.lock:
            self.pending_post = (token, p)

        return {}

    # Executa operações pendentes. Geralmente chamado em intervalos de tempo. É
    # thread-safe pois acessos e modificações são feitos em um bloco de
    # exclusão mútua, e update() e Resource.add_sibling() são.
    def do_pending(self):
        with self.lock:
            put = self.pending_put
            post = self.pending_post
            self.pending_put = None
            self.pending_post = None
        if put:
            self.update(put)
        if post:
            self.add_sibling(*post)

    # Método que move o jogador. Recebe um dicionário de dicionários
    # substituindo uma matriz, para verificar se já existem jogadores no
    # destino. Se houver, colisões devem ser tratadas. É thread-safe pois
    # get_data, collide e update() são.
    def move(self, occupied):
        a = self.get_data()
        oldx, oldy = a['posx'], a['posy']
        movx, movy = a['movx'], a['movy']
        lookx, looky = a['lookx'], a['looky']

        x, y = oldx + movx, oldy + movy
        if x == oldx and y == oldy:
            return

        if lookx == movx:
            x += 1
        if looky == movy:
            y += 1

        if x in occupied and y in occupied[x] and occupied[x][y] is not self:
            self.collide(occupied[x][y])
            occupied[x][y].collide(self)
        else:
            occupied[x][y] = self
            self.update({'posx': x, 'posy': y})

    # Método que trata colisão com outro jogador. Um jogador que colide apenas
    # pára de se mover. É thread-safe pois Player.update() é.
    def collide(self, player):
        self.update({'movx': 0, 'movy': 0})

    # Computa dano ao jogador, vindo de outro. Se chegar a 0, morre. É
    # thread-safe pois Player.update() e Resource.delete() são.
    def damage(self):
        self.update({'hp': self.attributes['hp'] - 1})
        if self.attributes['hp'] < 1:
            self.delete()

    # Atualiza dados e dispara notificação caso haja mudanças. É thread-safe
    # pois a modificação está dentro de um bloco de exclusão mútua, e
    # get_data() e Monitor.notify() são.
    def update(self, data):
        changes = False

        a = self.get_data()
        for i, j in data.items():
            if i not in a or j != a[i]:
                changes = True

        if changes:
            with self.lock:
                self.attributes.update(data)
            self.notify()


# Um projétil é um "jogador" que se move em uma direção até colidir com outro
# jogador.
class Projectile(Player):

    # Construtor. Recebe a posição de origem, e a direção na qual o projétil
    # deve se mover. É posicionado um passo à frente, para não coincidir com o
    # jogador que o atirou.
    def __init__(self, player):
        a = player.get_data()
        Player.__init__(self, {'name': a['name'] + '\'s projectile'}, None)
        self.player = player

        posx, posy = a['posx'], a['posy']
        lookx, looky = a['lookx'], a['looky']

        with self.lock:
            self.attributes.update({'type': 'projectile',
                'movx': lookx, 'movy': looky,
                'posx': posx + lookx, 'posy': posy + looky})


    # Sobrescrito de Player. Um projétil não pode ter seu estado alterado
    # explicitamente por qualquer cliente. É thread-safe pois default_reply é
    # imutável.
    def do_PUT(self, data):
        return self.default_reply

    # Sobrescrito de Player. Um projétil que colide com outro jogador reduz o
    # HP daquele, e se deleta. É thread-safe pois Player.damage() e
    # Resource.delete() são.
    def collide(self, player):
        d = player.get_data()
        if d['type'] == 'projectile':
            return
        player.damage()
        if d['hp'] < 1:
            with self.player.lock:
                self.player.attributes['kills'] += 1
        self.delete()

    # Sobrescrito de Player. É thread-safe pois Monitor.get_data() e
    # Resource.delete() são. #TODO fazer com que projétil tenha duração de
    # tempo.
    def update(self, data):
        Player.update(self, data)
        d = self.get_data()
        for i in ['posx', 'posy']:
            if d[i] not in range(-50, 51):
                self.delete()


# Main.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Servidor do jogo.',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-p', '--port', type=int, default=8000,
            help='A porta para hospedar o servidor.')
    parser.add_argument('-s', '--step', type=float, default=0.2,
            help='O intervalo de tempo em segundos entre atualizações.')
    args = parser.parse_args()

    server = Server('localhost', args.port)
    game = Game(args.step)
    server.root.add_child('game', game)

    game.start()
    server.serve_forever()


