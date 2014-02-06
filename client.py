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
import Editor

# Classe abstrata que requisita repetidamente um recurso e atualiza seus dados.
class Poller(threading.Thread):

    # Construtor. Inicializa o timestamp como o menor possível, pois ainda não
    # há dados recebidos.
    def __init__(self, host, uri):
        threading.Thread.__init__(self)
        self.host = host
        self.uri = uri
        self.timestamp = time.mktime(time.gmtime(0))
        self.lock = threading.Lock()

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

    # Método abstrato que obtém os dados do objeto.
    def get_data(self):
        pass

    # Método abstrato para lidar com os dados recebidos.
    def update(self, data):
        pass

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


# Um objeto do jogo.
class Object(Poller):

    # Construtor.
    def __init__(self, host, uri):
        Poller.__init__(self, host, uri)
        self.attributes = {'posx': 0, 'posy': 0,
                'movx': 0, 'movy': 0, 'lookx': 0, 'looky': 0}

    # Sobrescrito de Poller. Os dados do objeto são seus atributos.
    def get_data(self):
        with self.lock:
            return self.attributes.copy()

    # Sobrescrito de Poller. Os dados recebidos são os atributos do objeto.
    def update(self, data):
        with self.lock:
            self.attributes = data


# Mantém jogadores, mapeados por tokens, e o próprio jogador. Recebe
# atualizações sobre a lista de jogadores e age de acordo. A variável
# on_game_update é uma função que é chamada a cada atualização. Pode ser setado
# por uma interface que queira ser atualizada.
class Game(Poller):

    # Construtor. Recebe um filename para o script a ser executado na
    # atualização dos jogadores, Recebe também os dados para criação do próprio
    # jogador, e o cria.
    def __init__(self, host, uri, name, password, script):
        Poller.__init__(self, host, uri)
        self.objects = {}
        self.name = name
        self.password = password

        f = open(script)
        self.script = f.read()
        f.close()

    # Sobrescrito de Poller. Os dados são os objetos do jogo.
    def get_data(self):
        with self.lock:
            return self.objects.copy()

    # Cria um objeto e o faz escutar por modificações.
    def create_object(self, name):
        p = Object(self.host, self.uri + '/' + name)
        p.start()
        return p

    # Cria o próprio jogador.
    def create_self(self):
        data = {'name': self.name, 'password': self.password,
                'script': self.script}

        connection = http.client.HTTPConnection(self.host)
        connection.request('POST', self.uri, bytes(json.dumps(data), 'utf-8'))

        response = connection.getresponse()
        urn = response.getheader('Location') # TODO validar
        response.close()

        self.player = self.create_object(urn)

    # Sobrescrito de Poller. Dados recebidos são uma lista de URNs
    # representando cada objetos. URNs que não estão no nosso dicionário são
    # adicionados como objetos novos, e tokens no nosso dicionário que não
    # estão nos dados recebidos são objetos removidos.
    def update(self, data):
        with self.lock:
            objects = {n: p for n, p in self.objects.items()
                       if n in data and n != self.name}
            objects.update({n: self.create_object(n) for n in data
                            if n not in self.objects and n != self.name})
            self.objects = objects


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

        self.mybuffer = ""
        self.produtor = 0
        self.consumidor =0
        self.editor = Editor.Editor(self, self.mybuffer, self.game.lock, self.produtor, self.consumidor, self.screen) 

        self.editor.start()
        self.start()
        self.join()
        self.editor.join()

    # Desenha os objetos na tela.
    def draw_objects(self):

        midx = int(curses.COLS / 2)
        midy = int(curses.LINES / 4)

        selfattrs = self.game.player.get_data()
        selfx = selfattrs['posx']
        selfy = selfattrs['posy']

        marks = {'player': 'O', 'projectile': '.', 'rock': '#'}

        for obj in self.game.get_data().values():
            oattrs = obj.get_data()
            if 'type' not in oattrs:
                continue

            ox = midx + oattrs['posx'] - selfx
            oy = midy + oattrs['posy'] - selfx
            if (ox not in range(0, curses.COLS) or
                oy not in range(0, curses.LINES)):
                continue

            self.screen.addstr(oy, ox, marks[oattrs['type']])

        self.screen.addstr(midy, midx, '@')

    # Desenha o status do jogador.
    def draw_status(self):
        selfattrs = self.game.player.get_data()
        try:
            self.screen.addstr(1, 1, self.game.name + ': ' +
                    str(selfattrs['kills']))
            self.screen.addstr(2, 1, '░░░░░░░░░░')
            self.screen.addnstr(2, 1, '██████████', selfattrs['hp'])
        except:
            pass

    # Desenha o script que está sendo usado
    def draw_script(self):
        try:
            script = open("script.py", "r")
            buffer = script.read()
            self.screen.addstr((int)(curses.LINES/2), 0, "-------------------------------------------------------------------------------------")
            self.screen.addstr((int)(curses.LINES/2)+1, 0, buffer)
            script.close()
        except: 
            pass

    # Desenha o buffer do editor na parte baixa da tela
    def draw_editor(self):
        try:
            self.screen.addstr(int(curses.LINES/2), 0, "----------------------------------------------------------------------------------------------------------------")
            with self.game.lock:
                self.screen.addstr(int(curses.LINES/2) + 1, 0, self.mybuffer)
        except:
            pass

    # Sobrescrito de Thread. Desenha a tela a cada intervalo de tempo.
    def run(self):
        while True:
            self.screen.erase()
            self.draw_objects()
            self.draw_status()
            self.draw_editor()
            self.screen.refresh()
            time.sleep(self.step)


# Main.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Cliente do jogo',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-n', '--name', default='HP',
            help='O nome do jogador.')
    parser.add_argument('-w', '--password', default='teste',
            help='A senha do jogador para modificações.')
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
    g = Game(args.path, args.uri, args.name, args.password, args.script)
    g.create_self()
    g.start()

    # Cria a interface.
    curses.wrapper(lambda s: Curses(g, s, args.refresh))


