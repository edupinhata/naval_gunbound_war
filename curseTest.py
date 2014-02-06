#!/usr/bin/env python3

import curses
import time
import threading

class Editor(threading.Thread):

    def __init__(self, mybuffer, buffer_lock, produtor, consumidor, screen):
        threading.Thread.__init__(self)
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
                with buffer_lock: 
                    my_buffer += chr(c)
                    produtor += 1
                    #self.screen.addstr(5,5, "teste")
                    self.screen.addstr(0,0, my_buffer)
            self.screen.refresh()
    

mybuffer=""
buffer_lock = threading.Lock()
produtor = 0
consumidor =0

curses.wrapper(lambda s: Editor(mybuffer, buffer_lock, produtor, consumidor, s))

