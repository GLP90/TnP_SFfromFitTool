import ROOT

class Efficiency:
    
    def __init__(self, raw_name, type_, name, h, xpar, ypars, hpassing, hfailing, funcfailing, funcpassing):
        self.raw_name = raw_name
        self.type_ = type_
        self.name = name
        self.addHist(h)
        self.xpar = xpar
        self.ypars = ypars
        self.addFits(hpassing, hfailing, funcfailing, funcpassing)


        #dimention of the efficiency


    def addHist(self, h):
        '''h is the efficiency histogram'''
        self.heff = h

    def addFits(self, hpassing, funcpassing, hfailing, funcfailing):
        '''canvas is a list of canvases'''
        self.hpassing = hpassing
        self.hfailing = hfailing
        self.funcfailing = funcfailing
        self.funcpassing = funcpassing




    
