#! /usr/bin/env python3

class robo(objects) :


    def __init__(self, vida, energia, pos_x, pos_y, movimento, propulsor, CdForca, canhao):
        self.vida = vida
        self.vidaMax = vida
        self.energia = energia
        self.energiaMax = energia
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.CdForca = CdForca
        self.canhao = canhao
        self.movimento = movimento
        self.propulsor = propulsor
        self.dir = 2 #1:up, 2:right, 3:down, 4:left
        self.solid = True



    def getVida(self):
        return self.vida

    def getEnergia(self):
        return self.energia

    def getEnergiaMax(self):
        return self.energiaMax

    def getPosX(self):
        return self.pos_x

    def getPosY(self):
        return self.pos_y

    def getMovimento(self):
        return self.movimento

    def getPropulsor(self):
        return self.propulsor

    def getCdForca(self):
        return self.CdForca

    def getCanhao(self):
        return self.canhao

    def setDir(dir):
        if(dir==1 || dir==2 || dir==3 || dir==4):
            self.dir = dir

    def setStatus(movi, propulsor, CdForca, canhao): 
        self.movi = movi
        self.propulsor = propulsor
        self.CdForca = CdForca
        self.canhao = canhao


    def printStatus(self):
        print("Vida: %.2d\nEnergia: %.2d\nPos: %d x %d\nMovimento: %d\nPropulsor: %d\nCdForca: %d\nCanhao: %d" %((self.vida/self.vidaMax)*100.0, (self.energia/self.energiaMax)*100.0, self.getPosX(), self.getPosY(), self.getMovimento(), self.getPropulsor(), self.getCdForca(), self.getCanhao()))


r1 = robo(100,200, 1, 1, 10, 0, 30, 30)


r1.printStatus()   



    
