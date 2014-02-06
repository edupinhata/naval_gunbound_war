#!/usr/bin/env python3

import curses
import time
import threading

mybuffer=""
buffer_lock = threading.Lock()
produtor = 0
consumidor =0


#classe que irá ler o que está no buffer. Ao achar alguma palavra específica, ele imprime a palavra colorida
class EditorColorize(threading.Thread):
    
    def __init__(self,  mybuffer, buffer_lock, produtor, consumidor, screen):
        threading.Thread.__init__(self)
        self.mybuffer = mybuffer
        self.buffer_lock = buffer_lock
        self.produtor = produtor
        self.consumidor = consumidor
        self.screen = screen


class Editor(threading.Thread):

    def __init__(self, Curses,  mybuffer, buffer_lock, produtor, consumidor, screen):
        threading.Thread.__init__(self)
        self.buffer_lock = buffer_lock
        self.produtor = produtor
        self.consumidor = consumidor
        self.screen = screen
        self.Curses = Curses
        curses.curs_set(1)
        #self.start()
        #self.join()


    #função que exporta o script para um arquivo.py 
    def exportScript(self, mybuf):
        try: 
            script = open("scriptie.py", "w")
            script.write(mybuf)
            script.close()
        except: pass
        

    def run(self):
        while True:
            c = self.screen.getch()
            if c == curses.KEY_DC:
                with self.buffer_lock:
                    self.exportScript(self.mybuffer)
            else:
                with self.buffer_lock: 
                    self.Curses.mybuffer += chr(c)
                    self.produtor += 1
            

#curses.wrapper(lambda s: Editor(mybuffer, buffer_lock, produtor, consumidor, s, 5, 0))

