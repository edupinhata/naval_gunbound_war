#! /usr/bin/env python3


#classe que representa uma unidade de objeto. Por exemplo:
#uma parede e um objeto, um robo  um objeto e um tiro e um objeto
#para esse jogo, acredito que apenas esses tres elementos bastam
#Todos os objetos tem uma representacao, podem ser impressos,
#tem uma posicao definida, tem tratamento de colisoes

#A principio, cada objeto ocupa dois espacos, por exemplo, 
#uma parede e representada por ||                       
#um robo pode ser representado por uma letra e num. Ex: r1
#um tiro sera representado pela letra o

class objects:

    def __init__(self, pos_x, pos_y, represent, solid):
        self.represent = represent
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.solid = solid

    #metodos get/set
    
    def getX(self):
        return self.pos_x

    def getY(self):
        return self.pos_y

    def getRep(self):
        return represent

    def getSolid(self):
        return solid

    def solid(self):
        self.solid = true

    def non_solid(self):
        self.solid = false

    def setX(self, newX):
        self.pos_x = newX

    def setY(self, newY):
        self.pos_y = newY

    #movimentacao

    def moveUp(self):
        self.pos_y -= 1
        
    def moveDown(self):
        self.pos_y += 1

    def moveRight(self):
        self.pos_x += 2

    def moveLeft(self):
        self.pos_x -= 2

    #tratamento de colisoes
    
