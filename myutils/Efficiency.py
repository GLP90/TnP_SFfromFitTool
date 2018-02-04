import ROOT
import numpy as np
import sys

class Efficiency:
    
    def __init__(self, raw_name, type_, name, h, xpar, ypars, hpassing, hfailing, funcfailing, funcpassing, fitResult, rooworksp):
        self.raw_name = raw_name
        self.type_ = type_
        self.name = name
        self.addHist(h)
        self.xpar = xpar
        self.ypars = ypars
        self.fitResult=fitResult
        self.rooworksp=rooworksp
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

    def ProcessEff(self, gr, xmin = None, xmax=None, error_threshold = None):
        '''Modifies efficiency distribution. This includes
        -Remove bins below the xmin parameter
        -Remove bins above the xmax parameter
        -Modify large uncertainy e.g. take the average of the two neighbour bins
        '''

        #Create subrange from current histogram
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

            ##Reduce error if specified
            #for yr in [y_hi, ylow]:
            #    if yr/y > error_threshold:
            #        print 'Too large error:', yr

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
                if ybinsL[l] > ybins[n]*error_threshold:
                    print 'too large error, it is', ybinsL[l]
                    ER_new = 999
                    if l == 0:
                        ER_new = ybinsL[1]
                    elif l == new_nbins:
                        ER_new = ybinsL[new_nbins-1]
                    else:
                        ER_new = 0.5*(ybinsL[l+1]+ybinsL[l-1])

                    print 'new error is', ER_new

                    ybinsL_ER.append(ER_new)

                else: ybinsL_ER.append(ybinsL[l])

                if ybinsH[l] > ybins[n]*error_threshold:
                    ER_new = 999
                    print 'too large error, it is', ybinsH[l]
                    if l == 0:
                        ER_new = ybinsH[1]
                    elif l == new_nbins:
                        ER_new =  ybinsH[new_nbins-1]
                    else:
                        ER_new = 0.5*(ybinsH[l+1]+ybinsH[l-1])

                    print 'new error is',  ER_new

                    ybinsH_ER.append(ER_new)

                else: ybinsH_ER.append(ybinsH[l])

            ybinsL = ybinsL_ER
            ybinsH = ybinsH_ER

        #Set all the bins to create new function 
        xbins_ =    np.array([i for i in xbins],dtype=np.float64)
        xbinsL_ =   np.array([i for i in xbinsL],dtype=np.float64)
        xbinsH_ =   np.array([i for i in xbinsH],dtype=np.float64)
        ybins_ =    np.array([i for i in ybins],dtype=np.float64)
        ybinsL_ =   np.array([i for i in ybinsL],dtype=np.float64)
        ybinsH_ =   np.array([i for i in ybinsH],dtype=np.float64)


        #print xbins_    
        #print xbinsL_   
        #print xbinsH_   
        #print ybins_    
        #print ybinsL_   
        #print ybinsH_   

        new_gr = ROOT.TGraphAsymmErrors(new_nbins, xbins_, ybins_, xbinsL_, xbinsH_, ybinsL_, ybinsH_)
        return new_gr
        #self.addHist(new_gr)

    def SetNewRange(self, xmin, xmax):
        '''Clear the distributions and fit histograms within the a certain range'''
        #Create subrange from current histogram
        self.addHist(self.ProcessEff(self.heff, xmin=xmin, xmax=xmax))

    def CleanBigError(self, threshold):
        #Create subrange from current histogram
        self.addHist(self.ProcessEff(self.heff, error_threshold=threshold))



        




    
