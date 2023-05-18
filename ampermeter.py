from Gpib import *

class PS:

    def __init__(self):
        self = Gpib('ps')
        self.clear()

    def SET_VOLTAGE_DC(self, voltage):
        self.write('vset {}\n'.format(voltage))

    def RST(self):
        self.write('*rst\n')
