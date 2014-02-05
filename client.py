#!/usr/bin/env python3

import http.client
import email.utils
import threading
import argparse
import hashlib
import curses
import json
import copy
import time
import os


# Classe abstrata que requisita repetidamente um recurso e atualiza seus dados.
class Poller(threading.Thread):

    # Construtor. Inicializa o timestamp como o menor possível, pois ainda não
    # há dados recebidos.
    def __init__(self, host, uri):
        threading.Thread.__init__(self)
        self.host = host
        self.uri = uri
        self.timestamp = time.mktime(time.gmtime(0))

    # Atualiza o timestamp a partir de uma resposta HTTP. Se não contém tal
    # informação, usa o tempo atual.
    def stamp(self, response):
        last_modified = response.getheader('Last-Modified',
                email.utils.formatdate(time.time()))
        self.timestamp = time.mktime(email.utils.parsedate(last_modified))

    # Lê o conteúdo de uma resposta HTTP formatado em JSON, e retorna um
    # dicionário correspondente.
    def read(self, response):
        try:
            return json.loads(response.read().decode('utf-8'))
        except:
            return {}

    # Requisita (atualizações de) o recurso repetidamente. Ao receber os dados,
    # atualiza o timestamp, e passa para o método update. Se encontrar erro na
    # conexão, pára.
    def run(self):
        connection = http.client.HTTPConnection(self.host)
        while True:
            connection.request('GET', self.uri,
                               headers={'If-Modified-Since':
                                   email.utils.formatdate(self.timestamp)})
            response = connection.getresponse()
            if response.status == http.client.NOT_FOUND:
                break

            self.stamp(response)
            data = self.read(response)
            response.close()

            self.update(data)

    # Método abstrato para lidar com os dados recebidos.
    def update(self, data):
        pass


# Um jogador.
class Player(Poller):

    # Construtor.
    def __init__(self, host, uri):
        Poller.__init__(self, host, uri)
        self.attributes = {'posx': 0, 'posy': 0,
                'movx': 0, 'movy': 0, 'lookx': 0, 'looky': 0}

    # Sobrescrito de Poller. Os dados recebidos são os atributos do jogador.
    def update(self, data):
        self.attributes = data


# Mantém jogadores, mapeados por tokens, e o próprio jogador. Recebe
# atualizações sobre a lista de jogadores e age de acordo. A variável
# on_game_update é uma função que é chamada a cada atualização. Pode ser setado
# por uma interface que queira ser atualizada.
class Game(Poller):

    # Construtor. Recebe um filename para o script a ser executado na
    # atualização dos jogadores, Recebe também os dados para criação do próprio
    # jogador, e o cria.
    def __init__(self, host, uri, name, script):
        Poller.__init__(self, host, uri)
        self.players = {}
        self.name = name

        f = open(script)
        self.script = f.read()
        f.close()

    # Cria um objeto Player e o faz escutar por modificações.
    def create_player(self, name):
        p = Player(self.host, self.uri + '/' + name)
        p.start()
        return p

    # Cria o próprio jogador.
    def create_self(self):
        data = {'name': self.name, 'script': self.script}

        connection = http.client.HTTPConnection(self.host)
        connection.request('POST', self.uri, bytes(json.dumps(data), 'utf-8'))

        response = connection.getresponse()
        urn = response.getheader('Location') # TODO validar
        response.close()

        self.player = self.create_player(urn)

    # Sobrescrito de Poller. Dados recebidos são uma lista de URNs
    # representando cada jogador. URNs que não estão no nosso dicionário são
    # adicionados como jogadores novos, e tokens no nosso dicionário que não
    # estão nos dados recebidos são jogadores removidos.
    def update(self, data):
        players = {n: p for n, p in self.players.items()
                   if n in data and n != self.name}
        players.update({n: self.create_player(n) for n in data
                        if n not in self.players and n != self.name})
        self.players = players


# Interface textual.
class Curses(threading.Thread):

    # Construtor. Recebe o jogo, um screen curses, e o intervalo de tempo entre
    # atualizações.
    def __init__(self, game, screen, step):
        threading.Thread.__init__(self)
        curses.use_default_colors()
        curses.curs_set(0)
        self.screen = screen
        self.game = game
        self.step = step

        self.start()
        self.join()

    # Desenha os objetos na tela.
    def draw_players(self):

        x = int(curses.COLS / 2)
        y = int(curses.LINES / 2)

        for p in self.game.players.values():
            marks = {'player': 'O', 'projectile': '.', 'rock': '#'}
            if 'type' not in p.attributes:
                continue

            px = x + p.attributes['posx'] - self.game.player.attributes['posx']
            py = y + p.attributes['posy'] - self.game.player.attributes['posy']
            if (px not in range(0, curses.COLS) or
                py not in range(0, curses.LINES)):
                continue

            self.screen.addstr(py, px, marks[p.attributes['type']])

        self.screen.addstr(y, x, '@')

    # Desenha o status do jogador.
    def draw_status(self):
        try:
            self.screen.addstr(1, 1, self.game.name + ': ' +
                    str(self.game.player.attributes['kills']))
            self.screen.addstr(2, 1, '░░░░░░░░░░')
            self.screen.addnstr(2, 1, '██████████',
                    self.game.player.attributes['hp'])
        except:
            pass

    # Sobrescrito de Thread. Desenha a tela a cada intervalo de tempo.
    def run(self):
        while True:
            self.screen.erase()
            self.draw_players()
            self.draw_status()
            self.screen.refresh()
            time.sleep(self.step)


# Main.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Cliente do jogo',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-n', '--name', default='HP',
            help='O nome do jogador.')
    parser.add_argument('-s', '--script', default='script.py',
            help='O script do jogador.')
    parser.add_argument('-p', '--path', default='localhost:8000',
            help='O endereço do servidor.')
    parser.add_argument('-u', '--uri', default='/game',
            help='O identificador de recurso do jogo.')
    parser.add_argument('-r', '--refresh', default=0.1,
            help='O tempo entre redesenhos da tela.')
    args = parser.parse_args()

    # Cria o jogo.
    g = Game(args.path, args.uri, args.name, args.script)
    g.create_self()
    g.start()

    # Cria a interface.
    curses.wrapper(lambda s: Curses(g, s, args.refresh))


