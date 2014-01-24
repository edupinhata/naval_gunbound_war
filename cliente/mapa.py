#! /usr/bin/env python3

#classe que imprime um mapa onde acontecera as batalhas
#o mapa sera composto por uma matriz grande, onde || e a unidade de bloco

class mapa:

    def __init__(self, size_x, size_y):
        for x in range(0, size_x):
            for y in range(0, size_y):
                mapa_matriz[x][y] = "  "
            


    def gera_bordas(self):
        blocos_count=0
        bloco = []
        for x in range(0, len(self.mapa_matriz)):
            bloco.append(objects(x,0,"||", True))
            bloco.append(objects(x,len(self.mapa_matriz), "||", True))
            for x in range(1, len(self.mapa_matriz[0])-1):
                bloco.append(objects(0, x, "||", True))
                bloco.append(objects(len(self.mapa_matriz[0]), x, "||", True))


    def printMat(self):
        for x in range(0, len(self.mapa_matriz)):
            for y in range(0, len(self.mapa_matriz[0])):
                print(mapa_matriz[x][y],)
            print("\n",)


                            
      
    
                      
                         
