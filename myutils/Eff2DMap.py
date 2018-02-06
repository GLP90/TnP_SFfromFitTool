import ROOT

class Eff2DMap:
    '''Contain 2D efficiencies'''

    def __init__(self, name):
        self.name = name 
        self.nominal = [] #2D, [y][x]
        self.up = [] #2D, [y][x]
        self.down = [] #2D, [y][x]
        self.xbins = None 
        self.ybins = None

    def Print(self, yval = 'nominal'):
        '''yval can be nominal, up or down'''

        print 'Map\t name\n'
        print yval+'\n'

        xhead = '\tx:\t\t'
        for x in self.xbins:
            xhead +=  str(x) + '\t'
        print xhead

        for y in range(0, len(self.ybins)):
            ystr = '\ny:\t' + str(self.ybins[y])
            for x in range(0, len(self.xbins)):
                ystr += '\t'+str(getattr(self,yval)[y][x])
            print ystr


