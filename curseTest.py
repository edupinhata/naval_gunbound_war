#!/usr/bin/env python3

import curses
import time
import threading

mybuffer=""
buffer_lock = threading.Lock()
produtor = 0
consumidor =0

class Editor(threading.Thread):

    def __init__(self, mybuffer, buffer_lock, produtor, consumidor, screen):
        threading.Thread.__init__(self)
        self.mybuffer = mybuffer
        self.buffer_lock = buffer_lock
        self.produtor = produtor
        self.consumidor = consumidor

        self.screen = screen
        curses.curs_set(1)
        self.start()
        self.join()

    def run(self):
        self.screen.addstr(0,0, "Teste\n")
        self.screen.refresh()
        while True:
            c = self.screen.getch()
            if c == curses.KEY_DC:
               break
            else:
                with self.buffer_lock: 
                    self.mybuffer += chr(c)
                    self.produtor += 1
                    #self.screen.addstr(5,5, "teste")
                    self.screen.addstr(0,0, self.mybuffer)
            self.screen.refresh()
    

curses.wrapper(lambda s: Editor(mybuffer, buffer_lock, produtor, consumidor, s))

