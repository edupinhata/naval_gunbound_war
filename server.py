#!/usr/bin/env python3

import socketserver
import http.server
import http.client
import email.utils
import collections
import threading
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

    # Método para encontrar um recurso dado um identificador (URI), separado
    # por '/'. Se não encontrá-lo, devolve o recurso "não encontrado". Por
    # exemplo, para encontrar o recurso identificado por "/game/abc123",
    # procura-se o recurso "game" no recurso raíz, e nele o recurso "abc123".
    def find_resource(self, uri):
        path = uri.split('/')
        path.pop(0)

        res = self.root
        for urn in path:
            try:
                res = res.children[urn]
            except KeyError:
                return self.not_found
        return res


# Esta classe é instanciada para cada requisição feita ao servidor, e é
# responsável por ler os dados de entrada, tratá-los e enviar a resposta.
# Neste programa, cada recurso é responsável por tratar requisições feitas a si
# mesmo, então o tratamento consiste em chamar o método correspondente no
# recurso e enviar como resposta o retorno.
class Handler(http.server.BaseHTTPRequestHandler):

    # Lê e retorna o tamanho da mensagem no cabeçalho. Se não estiver nele,
    # retorna zero.
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

    # Lê o corpo da mensagem formatado como JSON e retorna um dicionário
    # correspondente. Adiciona um campo timestamp correspondente à última
    # atualização do cliente. Recursos podem ou não fazer uso dele.
    def read(self):
        length = self.read_length()
        data = {'timestamp': self.read_timestamp()}
        try:
            text = self.rfile.read(length).decode('utf-8')
            data.update(json.loads(text))
        except:
            pass
        finally:
            return data

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

    # Trata uma requisição GET.
    def do_GET(self):
        self.reply(self.server.find_resource(self.path).do_GET(self.read()))

    # Trata uma requisição POST.
    def do_POST(self):
        self.reply(self.server.find_resource(self.path).do_POST(self.read()))

    # Trata uma requisição PUT.
    def do_PUT(self):
        self.reply(self.server.find_resource(self.path).do_PUT(self.read()))

    # Trata uma requisição DELETE.
    def do_DELETE(self):
        self.reply(self.server.find_resource(self.path).do_DELETE(self.read()))

    # Descomentar para suprimir logging de requisições respondidas.
    #def log_message(self, format, *args):
        #return


# Classe abstrata. Cada recurso tem um dicionário de recursos filhos, mapeados
# por um nome único (URN, Universal Resource Name, exemplo: "abc123").
# A concatenação dos URNs desde um recurso raíz até outro compõe o
# identificador (URI, Universal Resource Identifier, exemplo: "/game/abc123").
# A concatenação do endereço do servidor e o URI compõe a localização (URL,
# Universal Resource Location, exemplo: "http://localhost:8000/game/abc123").
# Um recurso tem métodos que respondem a requisições HTTP. Tipicamente, uma
# requisição GET retorna os dados do recurso, POST cria um recurso filho nele,
# e PUT atualiza os dados.
class Resource:

    # Construtor. Define o código de retorno padrão como "método não
    # permitido". É esperado que subclasses sobrescrevam este comportamento.
    def __init__(self, default_reply={'code': http.client.METHOD_NOT_ALLOWED}):
        self.children = {}
        self.on_delete = None
        self.on_add_sibling = None
        self.default_reply = default_reply
        self.lock = threading.Lock()

    # Adiciona um recurso filho. Se não especificado o URN desejado para o
    # recurso, usa-se um aleatório. Também modifica o recurso para que seu
    # ponteiro-para-função on_delete aponte para o método delete_child deste
    # objeto (com o argumento apropriado), e on_add_sibling para add_child.
    # Assim, o recurso chamar delete fará com que este objeto o remova dos
    # recursos filhos, e chamar add_sibling fará com que este adicione um
    # recurso filho.
    def add_child(self, resource, urn=None):
        if not urn:
            urn = hashlib.md5(os.urandom(4096)).hexdigest()
        with self.lock:
            self.children[urn] = resource
        with resource.lock:
            resource.on_add_sibling = self.add_child
            resource.on_delete = lambda: self.delete_child(urn)

    # Deleta um recurso filho. Recursos filhos deste objeto adicionados com
    # add_child chamarão este método ao chamar delete.
    def delete_child(self, urn):
        with self.lock:
            if urn in self.children:
                self.children.pop(urn)

    # Chama o ponteiro-para-função on_add_sibling, setado por add_child no
    # recurso pai.
    def add_sibling(self, resource, urn=None):
        if self.on_add_sibling:
            self.on_add_sibling(resource, urn)

    # Chama o ponteiro-para-função on_delete, setado por add_child no recurso
    # pai.
    def delete(self):
        if self.on_delete:
            self.on_delete()

    # Trata uma requisição GET.
    def do_GET(self, data):
        return self.default_reply

    # Trata uma requisição POST.
    def do_POST(self, data):
        return self.default_reply

    # Trata uma requisição PUT.
    def do_PUT(self, data):
        return self.default_reply

    # Trata uma requisição DELETE.
    def do_PUT(self, data):
        return self.default_reply


# Recurso que monitora sua data de atualização, mantendo um timestamp.
# Requisições GET de clientes que já tenham o recurso atualizado serão
# bloqueadas até que o evento sinalizando atualização seja disparado.
class Monitor(Resource):

    # Construtor. Define a última data de atualização como "agora". Cria uma
    # variável para indicar se o objeto foi modificado, para que múltiplas
    # modificações possam ser feitas antes de se disparar o evento de
    # atualização.
    def __init__(self):
        Resource.__init__(self)
        self.dirty = False
        self.timestamp = time.time()
        self.update_event = threading.Event()

    # Método abstrato que obtém os dados do recurso.
    def get_data(self):
        return None

    # Se a variável que define se o objeto foi modificado for True, atualiza o
    # timestamp e dispara o evento de atualização, desbloqueando threads que
    # estejam esperando por ele.
    def notify(self):
        with self.lock:
            if self.dirty:
                self.timestamp = time.time()
                self.update_event.set()
                self.update_event.clear()
            self.dirty = False

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


# Um objeto monitora um conjunto de atributos.
class Object(Monitor):

    # Construtor.
    def __init__(self):
        Monitor.__init__(self)
        self.attributes = {'hp': 10, 'type': None,
                           'posx': 0, 'posy': 0,
                           'movx': 0, 'movy': 0,
                           'lookx': 1, 'looky': 1}

    # Implementado de Monitor. Uma requisição GET retorna uma cópia dos
    # atributos do objeto em formato dicionário.
    def get_data(self):
        with self.lock:
            return self.attributes.copy()

    # Computa dano ao objeto. Se chegar a 0, é deletado.
    def add_damage(self, source):
        if self is source:
            return
        with self.lock:
            self.dirty = True
            self.attributes['hp'] -= 1
            if self.attributes['hp'] < 1:
                self.delete()

    # Método que trata colisão com outro objeto. Em princípio, o objeto pára de
    # se mover.
    def collide(self, player):
        with self.lock:
            for i in ['movx', 'movy']:
                self.dirty = True
                self.attributes[i] = 0

    # Método que move o objeto. Recebe um dicionário que mapeia cada X para um
    # dicionário que mapeia para cada Y um objeto para verificar se já existem
    # objetos no destino. Se houver, chama o método de tratamento de colisão.
    # Se não houver, atualiza o dicionário.
    def move(self, occupied):
        with self.lock:
            x, y = self.attributes['posx'], self.attributes['posy']
            mx, my = self.attributes['movx'], self.attributes['movy']
            lx, ly = self.attributes['lookx'], self.attributes['looky']
        if mx == 0 and my == 0:
            return

        # Se está olhando para onde está se movendo, ganha bônus.
        x += mx + (1 if lx == mx else 0)
        y += my + (1 if ly == my else 0)

        # Tratamento de colisão.
        if x in occupied and y in occupied[x] and occupied[x][y] is not self:
            self.collide(occupied[x][y])
            occupied[x][y].collide(self)
            return

        # Movido com sucesso.
        occupied[x][y] = self
        with self.lock:
            self.dirty = True
            self.attributes['posx'] = x
            self.attributes['posy'] = y

    # Método abstrato que executa o script do objeto a partir dos outros objetos.
    def execute(self, others):
        pass


# Um objeto que não se move mas é destruível.
class Rock(Object):

    # Construtor. Recebe a posição inicial.
    def __init__(self, x, y):
        Object.__init__(self)
        self.attributes.update({'hp': 5, 'type': 'rock',
                                'posx': x, 'posy': y})


# Um jogador é um objeto com atributos adicionais.
class Player(Object):

    # Construtor. Recebe o script, e uma senha para que o cliente possa fazer
    # modificações.
    def __init__(self, password, script):
        Object.__init__(self)
        self.password = password
        self.script = script
        self.attributes.update({'hp': 10, 'type': 'player',
                                'shots': 0, 'shooting': False, 'kills': 0})

    # Atira, criando um recurso irmão da classe Projectile. Máximo 5 tiros por
    # vez.
    def add_shot(self):
        with self.lock:
            if self.attributes['shots'] >= 5:
                return
            self.attributes['shots'] += 1
            self.dirty = True
        urn = hashlib.md5(os.urandom(4096)).hexdigest()
        self.add_sibling(Projectile(self), urn)

    # Indica que um tiro foi removido.
    def remove_shot(self):
        with self.lock:
            self.attributes['shots'] -= 1
            self.dirty = True

    # Adiciona 1 aos kills do jogador.
    def add_kill(self):
        with self.lock:
            self.dirty = True
            self.attributes['kills'] += 1

    # Sobrescrito de Object. Se o jogador morrer, cede um kill para o jogador
    # que o matou.
    def add_damage(self, source):
        Object.add_damage(self, source)
        with self.lock:
            if self.attributes['hp'] < 1:
                source.add_kill()

    # Sobrescrito de Object. Expõe uma cópia de alguns atributos do jogador e
    # dos outros jogadores. Ao final, atualiza os dados, e atira se for
    # necessário.
    def execute(self, others):
        attributes = self.get_data()
        players = [p.get_data() for p in others]
        exec(self.script, {'attributes': attributes, 'players': players})

        # Verifica diferenças nos atributos e na cópia passada. TODO validar.
        with self.lock:
            for i in ['movx', 'movy', 'lookx', 'looky', 'shooting']:
                if self.attributes[i] != attributes[i]:
                    self.attributes[i] = attributes[i]
                    self.dirty = True

        # Verifica se o jogador está atirando.
        if attributes['shooting']:
            self.add_shot()

    # Sobrescrito de Resource. Altera o script.
    def do_PUT(self, data):
        for i in['password', 'script']:
            if i not in data:
                return {'code': http.client.EXPECTATION_FAILED}
        if data['password'] != self.password:
            return {'code': http.client.FORBIDDEN}

        with self.lock:
            self.script = data['script']

        return {'code': http.client.ACCEPTED}

    # Sobrescrito de Resource. Deleta o jogador.
    def do_DELETE(self, data):
        if 'password' not in data:
            return {'code': http.client.EXPECTATION_FAILED}
        if data['password'] != self.password:
            return {'code': http.client.FORBIDDEN}

        self.delete()

        return {'code': http.client.NO_CONTENT}


# Um projétil é um objeto que move em uma direção até colidir com outro
# jogador, ou até passar do seu alcance.
class Projectile(Object):

    # Construtor. Recebe o jogador de origem para determinar a direção de
    # movimento, e é posicionado um passo à frente para não coincidir com ele.
    def __init__(self, player):
        Object.__init__(self)
        self.player = player
        self.range = 20

        a = player.get_data()
        x, y = a['posx'], a['posy']
        lx, ly = a['lookx'], a['looky']

        self.attributes.update({'hp': 1, 'type': 'projectile',
                                'posx': x + 2 * lx, 'posy': y + 2 * ly,
                                'movx': lx, 'movy': ly})

    # Sobrescrito de Resource. Reduz a contagem de tiros no jogador de origem.
    def delete(self):
        Resource.delete(self)
        self.player.remove_shot()

    # Sobrescrito de Object. Um projétil que colide com outro objeto reduz o HP
    # daquele, e se deleta.
    def collide(self, other):
        a = other.get_data()
        other.add_damage(self.player)
        self.delete()

    # Sobrescrito de Object. Cada movimento reduz o alcance do projétil, e se
    # chegar a zero, é deletado.
    def move(self, occupied):
        Object.move(self, occupied)
        with self.lock:
            self.range -= 1
            if self.range < 1:
                self.delete()


# Monitor cujos dados são os recursos filhos. Adição ou remoção marcará este
# recurso como modificado.
class Container(Monitor):

    # Sobrescrito de Monitor. Retorna uma lista de URNs dos recursos filhos.
    def get_data(self):
        with self.lock:
            return [urn for urn in self.children]

    # Sobrescrito de Resource. Ao adicionar um recurso filho, marca este objeto
    # como modificado.
    def add_child(self, resource, urn=None):
        Resource.add_child(self, resource, urn)
        with self.lock:
            self.dirty = True

    # Sobrescrito de Resource. Ao remover um recurso filho, marca este objeto
    # como modificado.
    def delete_child(self, urn):
        Resource.delete_child(self, urn)
        with self.lock:
            self.dirty = True


# O jogo é um Container cujo recursos filhos monitorados são os jogadores.
# Ainda, a cada intervalo de tempo, chama os métodos dos jogadores que definem
# a lógica do jogo.
class Game(Container, threading.Thread):

    # Construtor. Recebe o intervalo de tempo entre cada passo do jogo.
    def __init__(self, time_step):
        threading.Thread.__init__(self)
        Container.__init__(self)
        self.time_step = time_step

    # Uma requisição POST cria um recurso filho (um jogador), validando dados
    # de entrada. Retorna uma resposta com o campo Location do cabeçalho
    # contendo a URN do jogador criado.
    def do_POST(self, data):
        for i in['name', 'password', 'script']:
            if i not in data:
                return {'code': http.client.EXPECTATION_FAILED}

        name = data['name']
        password = data['password']
        script = data['script']

        # O nome deve ser único.
        with self.lock:
            if name in self.children:
                return {'code': http.client.EXPECTATION_FAILED} # TODO outro código

        self.add_child(Player(password, script), name)
        return {'code': http.client.CREATED,
                'headers': [('Location', name)]}

    # Retorna um dicionário que mapeia para cada X um dicionário que mapeia,
    # para cada Y, um jogador, assim substituindo uma matriz.
    def get_occupied(self):
        d = collections.defaultdict(dict)
        with self.lock:
            d.update({p.get_data()['posx']: {p.get_data()['posy']: p}
                      for p in self.children.copy().values()})
        return d

    # Sobrescrito de Thread. Executa operações pendentes e chama o método move
    # de cada jogador, fornecendo um dicionário de posições ocupadas por outros
    # jogadores. O próprio jogador então trata colisões com outros.
    def run(self):
        while True:
            time.sleep(self.time_step)

            # Movimenta jogadores.
            with self.lock:
                players = self.children.copy().values()
            for p in players:
                p.move(self.get_occupied())

            # Executa os scripts e notifica caso hajam modificações.
            for p in players:
                p.execute(players)
                p.notify()

            # Notifica clientes caso hajam modificações.
            self.notify()
            for p in players:
                p.notify()


# Main.
if __name__ == '__main__':
    # Cria argumentos de linha de comando.
    parser = argparse.ArgumentParser(description='Servidor do jogo.',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-p', '--port', type=int, default=8000,
            help='A porta para hospedar o servidor.')
    parser.add_argument('-s', '--step', type=float, default=0.1,
            help='O intervalo de tempo em segundos entre atualizações.')
    parser.add_argument('-r', '--rocks', type=int, default=20,
            help='O número de pedras no campo, assim como a distância máxima.')
    args = parser.parse_args()

    # Cria o servidor.
    server = Server('localhost', args.port)

    # Cria o jogo e adiciona pedras.
    game = Game(args.step)
    server.root.add_child(game, 'game')
    for i in range(args.rocks):
        game.add_child(Rock(random.randrange(args.rocks),
                            random.randrange(args.rocks)))

    # Inicia o jogo e o servidor.
    game.start()
    server.serve_forever()

