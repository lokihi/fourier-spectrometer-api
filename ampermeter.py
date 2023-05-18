from Gpib import *

class AMP:
    
    def __init__(self):
        self = Gpib('amperemeter')
        self.clear()
        self.write('configure:current:dc\n')
        self.write('format:elements reading\n')
        self.write('display:digits 7\n')

    def READ_CURRENT_DC(self):
        return(1)
        return self.read().decode("utf-8")

    def RST(self):
        self.write('*rst\n')
