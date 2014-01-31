#!/usr/bin/env python3

import http.client
import email.utils
import threading
import functools
import argparse
import hashlib
import locale
import curses
import json
import copy
import time
import os


# Faz uma requisição a partir de uma nova conexão HTTP e devolve a resposta.
def new_request(host, method, resource, data={}, headers={}):
    connection = http.client.HTTPConnection(host)
    connection.request(method, resource,
            bytes(json.dumps(data), 'utf-8'), headers)
    return connection.getresponse()

def init_curses():
    s = curses.initscr()
    curses.curs_set(0)
    curses.noecho()
    curses.cbreak()
    return s

def terminate_curses():
    curses.nocbreak()
    curses.echo()
    curses.curs_set(2)
    curses.endwin()


# Classe abstrata que requisita repetidamente um recurso e espera até que o
# servidor tenha atualizações, e então passa os dados recebidos para o método
# abstrato update().
class Poller(threading.Thread):

    # Construtor. Inicializa o timestamp como o menor possível, pois ainda não
    # há dados recebidos.
    def __init__(self, host, resource):
        threading.Thread.__init__(self)
        self.host = host
        self.resource = resource
        self.timestamp = time.mktime(time.gmtime(0))

    # Requisita (atualizações de) o recurso repetidamente. Ao receber os dados,
    # atualiza o timestamp, e passa para o método update. Se encontrar erro na
    # conexão, pára.
    def run(self):
        connection = http.client.HTTPConnection(self.host)
        while True:
            connection.request('GET', self.resource,
                               headers={'If-Modified-Since':
                                   email.utils.formatdate(self.timestamp)})
            response = connection.getresponse()
            if response.status == http.client.NOT_FOUND:
                break

            last_modified = response.getheader('Last-Modified',
                    email.utils.formatdate(time.time()))
            self.timestamp = time.mktime(email.utils.parsedate(last_modified))

            data = {}
            try:
                data = json.loads(response.read().decode('utf-8'))
            except:
                pass
            finally:
                response.close()
                self.update(data)

    # Método abstrato para lidar com os dados recebidos.
    def update(self, data):
        pass


# Mantém jogadores, mapeados por tokens, e o próprio jogador. Recebe
# atualizações sobre a lista de jogadores e age de acordo. A variável
# on_game_update é uma função que é chamada a cada atualização. Pode ser setado
# por uma interface que queira ser atualizada.
class Game(Poller):

    # Construtor. Recebe um filename para o script a ser executado na
    # atualização dos jogadores, Recebe também os dados para criação do próprio
    # jogador, e o cria.
    def __init__(self, host, resource, script, data):
        Poller.__init__(self, host, resource)

        self.players = {}
        self.on_game_update = None
        threading.Thread(target=self.game_update).start()

        self.you = You(host, resource, script, data)

    # Implementado da superclasse. Dados recebidos são uma lista de tokens
    # representando cada jogador. Tokens que não estão no nosso dicionário são
    # adicionados como jogadores novos, e tokens no nosso dicionário que não
    # estão nos dados recebidos são jogadores removidos.
    def update(self, data):
        players = {t: p for t, p in self.players.items()
                   if t in data and t != self.you.token}
        players.update({t: self.create_player(t) for t in data
                        if t not in self.players and t != self.you.token})
        self.players = players

    # Cria um objeto Player 
    def create_player(self, token):
        p = Player(self.host, self.resource + '/' + token)
        p.on_update = self.game_update
        p.start()
        return p

    # Executa o script.
    def game_update(self):
        while True:
            time.sleep(0.1)
            self.you.execute(self.players)
            if self.on_game_update:
                self.on_game_update()


# Um jogador. A variável on_update é uma função que pode ser setada pelo jogo
# para sinalizar atualização do jogador.
class Player(Poller):

    # Construtor. Inicia sua thread que escuta atualizações.
    def __init__(self, host, resource):
        Poller.__init__(self, host, resource)
        self.attributes = {'posx': 0, 'posy': 0, 'movx': 0,
                'movy': 0, 'lookx': 0, 'looky': 0}

    # Método implementado da superclasse. Os dados recebidos são os atributos
    # do jogador.
    def update(self, data):
        self.attributes = data


# O próprio jogador. Possui métodos para reagir a atualizações dos outros
# jogadores e enviar modificações do estado para o servidor.
class You(Player):

    # Construtor. Inicializa o script e cria o recurso no servidor.
    def __init__(self, host, parent_resource, script, data):
        Player.__init__(self, host, parent_resource)
        self.init_script(script)
        self.init_player(data)
        self.start()

    # Lê o script, deixando-o pronto pra ser executado.
    def init_script(self, filename):
        f = open(filename)
        self.script = f.read()
        f.close()
        self.script_lock = threading.Lock()

    # Cria o nosso jogador. Como o construtor recebeu '/game', adiciona o token
    # ao caminho.
    def init_player(self, data):
        self.password = data['password']
        response = new_request(self.host, 'POST', self.resource, data)
        self.token = response.getheader('Location') # TODO validar
        response.close()
        self.resource += '/' + self.token

    # Atira.
    def shoot(self):
        data = {'password': self.password}
        response = new_request(self.host, 'POST', self.resource, data)

    # Executa o script, expondo uma cópia dos atributos dos jogador e os outros
    # jogadores.  Ao final, se foram feitas modificações nos atributos, pede ao
    # servidor para atualizá-las.
    def execute(self, other_players):
        with self.script_lock:
            attributes = self.attributes.copy()
            exec(self.script, {'attributes': attributes, 'shoot': self.shoot,
                'players': other_players})

            for i, j in attributes.items():
                if self.attributes[i] != j:
                    threading.Thread(target=self.refresh,
                            kwargs={'data': attributes}).start()
                    break

    # Informa o servidor sobre o novo estado do jogador.
    def refresh(self, data):
        data.update({"password": self.password})
        new_request(self.host, 'PUT', self.resource, data).close()


# Interface textual.
class Curses:

    # Construtor. Recebe o jogo, e seta a variável on_game_update para
    # self.draw, ou seja, quando o jogo for atualizado, chamará self.draw,
    # atualizando a tela.
    def __init__(self, screen, game):
        self.game = game
        self.game.on_game_update = self.draw

        self.messages = ['' for i in range(3)]
        self.draw_lock = threading.Semaphore()

        self.screen = screen
        self.window = curses.newwin(self.get_window_height(), self.get_window_width())

        self.status_width = 12
        self.status_height = 3
        self.status = curses.newwin(self.status_height, self.status_width,
                1, 1)

        self.log_width = curses.COLS
        self.log_height = 5
        self.log = curses.newwin(self.log_height, self.log_width,
                self.get_window_height(), 0)

    def get_window_width(self):
        return curses.COLS

    def get_window_height(self):
        return curses.LINES - 5

    def get_x(self):
        return int(self.get_window_width() / 2)

    def get_y(self):
        return int(self.get_window_height() / 2)

    # Desenha a tela. 
    def draw(self):
        self.add_message(str(self.game.you.attributes))

        self.draw_lock.acquire()

        self.draw_window()
        self.draw_status()
        self.draw_log()

        self.window.refresh()
        self.status.refresh()
        self.log.refresh()

        self.draw_lock.release()

    # Desenha a janela principal do jogo.
    def draw_window(self):
        self.window.erase()
        self.window.border()
        self.draw_players()

    # Desenha os personagens na tela.
    def draw_players(self):
        for p in self.game.players.values():
            x = self.get_x() + p.attributes['posx'] - self.game.you.attributes['posx']
            y = self.get_y() + p.attributes['posy'] - self.game.you.attributes['posy']
            if (x not in range(0, self.get_window_width()) or
                y not in range(0, self.get_window_height())):
                continue
            if 'type' not in p.attributes:
                continue
            mark = '.' if p.attributes['type'] == 'projectile' else '#'
            self.window.addstr(y, x, mark)
        self.window.addstr(self.get_y(), self.get_x(), '@')

    def draw_player(self, player, selfx, selfy):
        #with player.lock:
        pass

    # Desenha o status do jogador.
    def draw_status(self):
        self.status.erase()
        self.status.addstr(1, 1, '░░░░░░░░░░')
        self.status.addnstr(1, 1, '██████████', self.game.you.attributes['hp'])
        self.status.addnstr(0, 1, self.game.you.attributes['name'], 10)

    # Desenha o log de mensagens. #TODO deprecado por uso de scripts.
    def draw_log(self):
        self.log.erase()
        self.log.border()
        for i in range(3):
            self.log.addstr(3 - i, 1, self.messages[i])

    # Adiciona uma mensagem.
    def add_message(self, message):
        self.messages.pop()
        self.messages.insert(0, message)
        self.draw_log()


# Main.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Cliente do jogo',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-n', '--name',
            default='HP',
            help='O nome do jogador.')
    parser.add_argument('-w', '--password',
            default=hashlib.md5(os.urandom(4096)).hexdigest(),
            help='A senha do jogador.')
    parser.add_argument('-s', '--script',
            default='script.py',
            help='O script do jogador.')
    parser.add_argument('-p', '--path',
            default='localhost:8000',
            help='O endereço do servidor.')
    args = parser.parse_args()

    g = Game(args.path, '/game', args.script,
             {"name": args.name, "password": args.password})
    c = Curses(init_curses(), g)

    g.start()
    try:
        g.join()
    except:
        terminate_curses()

