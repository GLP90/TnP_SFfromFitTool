import ROOT
import numpy as np
import sys
import math
import pdb

class Efficiency:
    
    def __init__(self, raw_name, type_, name, h, xpar, ypars, ypar, hpassing, hfailing, funcfailing, funcpassing, fitResult, rooworksp):
        self.raw_name = raw_name
        self.type_ = type_
        self.name = name
        self.addHist(h)
        self.xpar = xpar
        self.ypars = ypars
        self.ypar = ypar
        self.fitResult=fitResult
        self.rooworksp=rooworksp
        self.addFits(hpassing, hfailing, funcfailing, funcpassing)
        self.lumi = None

        #dimention of the efficiency

    def setLumi(self, lumi):
        '''Add luminosity. Used when ploting and summing efficiencies together'''
        self.lumi = lumi


    def addHist(self, h):
        '''h is the efficiency histogram'''
        self.heff = h

    def addFits(self, hpassing, funcpassing, hfailing, funcfailing):
        '''canvas is a list of canvases'''
        self.hpassing = hpassing
        self.hfailing = hfailing
        self.funcfailing = funcfailing
        self.funcpassing = funcpassing

    def SumEfficiency(self, eff):
        '''Modify efficiency by adding eff. Lumi and the TGraphs are modified accordingly'''

        if not self.lumi or not eff.lumi:
            print '@ERROR: Efficiency don\'t have any lumi value. Cannot add them. @Aborting'
            sys.exit()

        self.addHist(self.AddGraph(self.heff, eff.heff, self.lumi, eff.lumi))
        self.setLumi(self.lumi + eff.lumi)

    def DivideEfficiency(self, eff):

        self.addHist(self.DivideGraph(self.heff, eff.heff))

    def DivideGraph(self, eff1, eff2):
        '''Return one single TGraphError that is the sum of eff1, and eff2. The sum is lumi-reweighted'''

        xbins = []
        xbinsL = [] 
        xbinsH = [] 
        ybins = [] 
        ybinsL = [] 
        ybinsH = [] 

        nbins = eff1.GetN()
        #if nbins != eff2.GetN():
        #    print "@ERROR: number of efficiency bin do not match. Cannot sum the Graphs. Aborting"
        #    sys.exit()

        #note: current fix only works if all missing pt bins are in high pT
        bins = range(0,max(nbins,eff2.GetN()))
        #bins = range(0,nbins)
        new_nbins = 0
        for bin_ in bins:
            print 'bin is', bin_
            #x1, x2 = ROOT.Double(999), ROOT.Double(999)
            x, x2 = ROOT.Double(999), ROOT.Double(999)
            y1, y2 = ROOT.Double(999), ROOT.Double(999)

            filled1 = eff1.GetPoint(bin_, x, y1)
            filled2 = eff2.GetPoint(bin_, x2, y2) 

            if filled1  == -1 or filled2 == -1:
                y_hi1, y_hi2    = 0,0
                y_low1, y_low2  = 0,0
                y1, y2 = 0, 1

                if filled1 != -1:
                    x_hi = eff1.GetErrorXhigh(bin_)
                    x_low = eff1.GetErrorXlow(bin_)
                elif filled2 != -1:
                    x_hi = eff2.GetErrorXhigh(bin_)
                    x_low = eff2.GetErrorXlow(bin_)
                else: continue

            else:
                y_hi1, y_hi2    = eff1.GetErrorYhigh(bin_),eff2.GetErrorYhigh(bin_),
                y_low1, y_low2  = eff1.GetErrorYlow(bin_), eff2.GetErrorYlow(bin_),
                x_hi = eff1.GetErrorXhigh(bin_)
                x_low = eff1.GetErrorXlow(bin_)
                x_hi2 = eff2.GetErrorXhigh(bin_)
                x_low2 = eff2.GetErrorXlow(bin_)


            xbins.append(x)
            xbinsL.append(x_low)
            xbinsH.append(x_hi)
            ybins.append(y1/y2)
            ybinsL.append(math.sqrt((y_low1/y2)**2+(y1*y_low2/(y2*y2))**2))
            ybinsH.append(math.sqrt((y_hi1/y2)**2+(y1*y_hi2/(y2*y2))**2))
            new_nbins += 1

        print 'finish the loop'

        #Set all the bins to create new function 
        xbins_ =    np.array([i for i in xbins],dtype=np.float64)
        xbinsL_ =   np.array([i for i in xbinsL],dtype=np.float64)
        xbinsH_ =   np.array([i for i in xbinsH],dtype=np.float64)
        ybins_ =    np.array([i for i in ybins],dtype=np.float64)
        ybinsL_ =   np.array([i for i in ybinsL],dtype=np.float64)
        ybinsH_ =   np.array([i for i in ybinsH],dtype=np.float64)

        new_gr = ROOT.TGraphAsymmErrors(new_nbins, xbins_, ybins_, xbinsL_, xbinsH_, ybinsL_, ybinsH_)
        return new_gr

    def AddGraph(self, eff1, eff2, lumi1, lumi2):

        xbins = []
        xbinsL = [] 
        xbinsH = [] 
        ybins = [] 
        ybinsL = [] 
        ybinsH = [] 

        nbins = eff1.GetN()
        if nbins != eff2.GetN():
            print "@ERROR: number of efficiency bin do not match. Cannot sum the Graphs. Aborting"
            sys.exit()

        bins = range(0,nbins)
        new_nbins = 0
        for bin_ in bins:
            #x1, x2 = ROOT.Double(999), ROOT.Double(999)
            x, x2 = ROOT.Double(999), ROOT.Double(999)
            y1, y2 = ROOT.Double(999), ROOT.Double(999)

            eff1.GetPoint(bin_, x, y1)
            eff2.GetPoint(bin_, x2, y2)

            x_hi = eff1.GetErrorXhigh(bin_)
            x_low = eff1.GetErrorXlow(bin_)
            y_hi1, y_hi2    = eff1.GetErrorYhigh(bin_),eff2.GetErrorYhigh(bin_),
            y_low1, y_low2  = eff1.GetErrorYlow(bin_), eff2.GetErrorYlow(bin_),

            l1 = lumi1/((lumi1+lumi2)*1.0)
            l2 = lumi2/((lumi1+lumi2)*1.0)

            xbins.append(x)
            xbinsL.append(x_low)
            xbinsH.append(x_hi)
            ybins.append(y1*l1 + y2*l2)
            ybinsL.append(math.sqrt((l1*y_low1)**2+(l2*y_low2)**2))
            ybinsH.append(math.sqrt((l1*y_hi1)**2+(l2*y_hi2)**2))
            new_nbins += 1

        #Set all the bins to create new function 
        xbins_ =    np.array([i for i in xbins],dtype=np.float64)
        xbinsL_ =   np.array([i for i in xbinsL],dtype=np.float64)
        xbinsH_ =   np.array([i for i in xbinsH],dtype=np.float64)
        ybins_ =    np.array([i for i in ybins],dtype=np.float64)
        ybinsL_ =   np.array([i for i in ybinsL],dtype=np.float64)
        ybinsH_ =   np.array([i for i in ybinsH],dtype=np.float64)

        new_gr = ROOT.TGraphAsymmErrors(new_nbins, xbins_, ybins_, xbinsL_, xbinsH_, ybinsL_, ybinsH_)
        return new_gr

    def ProcessEff(self, gr, xmin = None, xmax=None, error_threshold = None):
        '''Modifies efficiency distribution. This includes
        -Remove bins below the xmin parameter
        -Remove bins above the xmax parameter
        -Modify large uncertainy e.g. take the average of the two neighbour bins
        '''


        xbins = []
        xbinsL = [] 
        xbinsH = [] 
        ybins = [] 
        ybinsL = [] 
        ybinsH = [] 

        nbins = gr.GetN()
        bins = range(0,nbins)
        new_nbins = 0

        for bin_ in bins:
            x = ROOT.Double(999)
            y = ROOT.Double(999)
            gr.GetPoint(bin_,x,y)
            x_hi = gr.GetErrorXhigh(bin_)
            x_low = gr.GetErrorXlow(bin_)
            y_hi = gr.GetErrorYhigh(bin_)
            y_low = gr.GetErrorYlow(bin_)

            #Remove bins if specified
            if xmin and x - x_low < xmin:
                continue
            if xmax and x + x_hi > xmax: 
                continue
            xbins.append(x)
            xbinsL.append(x_low)
            xbinsH.append(x_hi)
            ybins.append(y)
            ybinsL.append(y_low)
            ybinsH.append(y_hi)
            new_nbins += 1

        if error_threshold:
            ybinsL_ER= []
            ybinsH_ER= []
            for n, l, h in zip((range(0,new_nbins)), range(0,new_nbins), range(0,new_nbins)):

                ER_new_low = 999
                ER_new_high = 999

                if ybinsL[l] > ybins[n]*error_threshold:
                    print '@WARNING: too large error, it is', ybinsL[l]
                    ER_new_low = 999
                    if l == 0:
                        ER_new_low = ybinsL[1]
                    elif l == new_nbins-1:
                        ER_new_low = ybinsL[new_nbins-2]
                    else:
                        ER_new_low = 0.5*(ybinsL[l+1]+ybinsL[l-1])

                    if ER_new_low > ybins[n]*error_threshold:
                        print 'ER_new still higher after taking neighbour bin. Taking the min of the two errors'
                        ER_new_low  = min(ybinsH[l], ybinsL[l])

                    print 'new error is', ER_new_low

                else: ER_new_low = ybinsL[l]

                #else: ybinsL_ER.append(ybinsL[l])

                if ybinsH[l] > ybins[n]*error_threshold:
                    ER_new_high = 999
                    print '@WARNING: too large error, it is', ybinsH[l]
                    if l == 0:
                        ER_new_high = ybinsH[1]
                    elif l == new_nbins-1:
                        ER_new_high =  ybinsH[new_nbins-2]
                    else:
                        ER_new_high = 0.5*(ybinsH[l+1]+ybinsH[l-1])

                    if ER_new_high > ybins[n]*error_threshold:
                        print 'ER_new still higher after taking neighbour bin. Taking the min of the two errors'
                        ER_new_high = min(ybinsH[l], ybinsL[l])

                    print 'new error is',  ER_new_high

                else: ER_new_high = ybinsH[l]

                ybinsL_ER.append(ER_new_low)
                ybinsH_ER.append(ER_new_high)

            ybinsL = ybinsL_ER
            ybinsH = ybinsH_ER

        #Set all the bins to create new function 
        xbins_ =    np.array([i for i in xbins],dtype=np.float64)
        xbinsL_ =   np.array([i for i in xbinsL],dtype=np.float64)
        xbinsH_ =   np.array([i for i in xbinsH],dtype=np.float64)
        ybins_ =    np.array([i for i in ybins],dtype=np.float64)
        ybinsL_ =   np.array([i for i in ybinsL],dtype=np.float64)
        ybinsH_ =   np.array([i for i in ybinsH],dtype=np.float64)


        new_gr = ROOT.TGraphAsymmErrors(new_nbins, xbins_, ybins_, xbinsL_, xbinsH_, ybinsL_, ybinsH_)
        return new_gr

    def SetNewRange(self, xmin, xmax):
        '''Clear the distributions and fit histograms within the a certain range'''
        #Create subrange from current histogram
        self.addHist(self.ProcessEff(self.heff, xmin=xmin, xmax=xmax))

    def CleanBigError(self, threshold):
        #Create subrange from current histogram
        self.addHist(self.ProcessEff(self.heff, error_threshold=threshold))



        




    
