import ROOT
from Efficiency import Efficiency
import os
import sys
import numpy as np
import copy as copy

class HistoPloter:
    '''Plot the relevant histogram, fits'''

    def __init__(self, outputpath):
        self.outputpath = outputpath
        self.effUpRange = 1.05
        self.effDownRange = 0.8
    

    def CreateOutputFolder(self, subfolder = None):
        '''Create output path to store the files if not existing'''
        if subfolder:
            directory = self.outputpath + '/' + subfolder
        else: 
            directory = self.outputpath

        if not os.path.exists(directory):
            os.makedirs(directory)

        return directory

    def FormatOutputPath(self, path):
        '''Modify output path (remvove space, etc)'''
        return path.replace(' ','').replace('&','And')

    def TGraph2TH1F(self, gr):
        '''Convert a TGraphAsymmErrors to TH1F. Errors are conservative i.e. max of the low/high error is take'''
        nbins = gr.GetN()
        bins = range(0,nbins)
        xbins = np.array([0 for i in range(0,nbins+1)],dtype=np.float64)
        for bin_ in bins:
            x = ROOT.Double(999)
            y = ROOT.Double(999)
            gr.GetPoint(bin_,x,y)
            x_hi = gr.GetErrorXhigh(bin_)
            x_low = gr.GetErrorXlow(bin_)
            if bin_ == nbins -1:
                xbins[bin_] = x - x_low
                xbins[bin_+1] = x + x_hi
            else:
                xbins[bin_] = x - x_low

        print 'xbins is', xbins
        h = ROOT.TH1F('h', 'h', nbins, xbins)

        for bin_ in bins:
            num_x = ROOT.Double(999)
            num_y = ROOT.Double(999) 
            num_y_hi = 999 
            num_y_low = 999 

            gr.GetPoint(bin_,num_x,num_y)
            num_y_hi = gr.GetErrorYhigh(i)
            num_y_low = gr.GetErrorYlow(i)

            max_error = max(num_y_hi,num_y_low)

            #Convert into TH1D
            h.SetBinContent(h.FindBin(num_x), num_y)
            h.SetBinError(h.FindBin(num_x), max_error)

        return h

    def PlotFit(self, eff):
        '''Plot and save fits for a given efficiency'''

        #Start by creating directory if not existing
        #directory = self.CreateOutputFolder('%s/%s/%s'%('Plots/Fits',eff.type_.replace(' ',''),eff.name.replace('&','and'),))
        directory = self.FormatOutputPath('%s/%s/%s'%('Plots/Fits',eff.type_,eff.name))
        directory = self.CreateOutputFolder(directory)

        print 'eff.hpassing is', eff.hpassing
        print 'eff.funcpassing is', eff.funcpassing
        print 'eff.hfail is', eff.hfailing
        print 'eff.funcfail is', eff.funcfailing

        nbin = 0 
        print 'len is', len(zip(eff.hpassing, eff.funcpassing, eff.hfailing, eff.funcfailing))



        for hp, fp, hf, ff in zip(eff.hpassing, eff.funcpassing, eff.hfailing, eff.funcfailing):
            nbin += 1
            print 'nbin is', nbin
            #Draw passing
            c = ROOT.TCanvas('c','c')
            c.cd()

            hp.Draw()
            fp.Draw('same')
            tl = ROOT.TLatex(110,0.1*hp.getYAxisMax(), '#chi^{2}/4 = %4.2f'%fp.chiSquare(hp,4))
            print '#chi^{2}/4 = %4.2f'%fp.chiSquare(hp,4)
            tl.Draw('same')
            c.SaveAs(directory+'/pass_%i.pdf'%nbin)
            c.SaveAs(directory+'/pass_%i.png'%nbin)
            c.SaveAs(directory+'/pass_%i.root'%nbin)

            #Draw failing
            c = ROOT.TCanvas('c','c')
            c.cd()
            hf.Draw()
            ff.Draw('same')
            tl = ROOT.TLatex(110,0.1*hf.getYAxisMax(), '#chi^{2}/4 = %4.2f'%ff.chiSquare(hf,4))
            print '#chi^{2}/4 = %4.2f'%ff.chiSquare(hf,4)
            tl.Draw('same')
            c.SaveAs(directory+'/fail_%i.pdf'%nbin)
            c.SaveAs(directory+'/fail_%i.png'%nbin)
            c.SaveAs(directory+'/fail_%i.root'%nbin)

    def PlotFitList(self, effList):
        '''Plot and save fits for a list of efficiencies'''
        for eff in effList:
            self.PlotFit(eff)

    def CheckFit(self, eff):
        '''Plot and save fits for a given efficiency'''

        #Start by creating directory if not existing
        #directory = self.CreateOutputFolder('%s/%s/%s'%('Plots/Fits',eff.type_.replace(' ',''),eff.name.replace('&','and'),))
        directory = self.FormatOutputPath('%s/%s/%s'%('Plots/Fits',eff.type_,eff.name))
        directory = self.CreateOutputFolder(directory)

        print 'eff.hpassing is', eff.hpassing
        print 'eff.funcpassing is', eff.funcpassing
        print 'eff.hfail is', eff.hfailing
        print 'eff.funcfail is', eff.funcfailing

        #print 'chi2', eff.funcfailing.chiSquare(eff.hfailing,4)
        #print 'chi2', eff.funcpassing.chiSquare(eff.hpassing,4)


    def CheckFitList(self, effList):
        '''Check if the fits are good enough (with several methods (to be built))'''
        for eff in effList:
            self.CheckFit(eff)

    def PlotEff1D(self, effList):
        '''Plot 1D efficiency distributions. Here effList is a container of efficiency lists. Each list should correspond to another sample. e.g. effList[0] a list of data efficiency, effList[1] a list of MC1 efficiency,  effList[2] a list of MC2 efficiency. All efficiencies will be ploted on the same canvas. The first list i.e. effList[0] will be used as reference in the ratio plot'''

        effFolder = effList[0][0].type_
        for effL in effList[1:]:
            effFolder+= '_AND_%s'%effL[0].type_
        
        effFolder = self.FormatOutputPath(effFolder)
        
        #print 'effFolder is', effFolder
        directory = self.CreateOutputFolder('%s/%s'%('Plots/Efficiency',effFolder))
        #directory = self.FormatOutputPath(directory)
        
        print 'directory is', directory

        cDict = {} #Dictionnary of canvas
        for eff in effList[0]:
            effname = eff.name
            c = ROOT.TCanvas('c_%s'%effname,'c_%s'%effname)

            theff = self.TGraph2TH1F(eff.heff)
            theff.GetYaxis().SetRangeUser( self.effDownRange, self.effUpRange)

            if len(effList) == 1:#no ratio needed if only one efficiency
                c.cd()
                theff.DrawCopy()
                #eff.heff.Draw()
                cDict[effname] =  c
                print 'list len is 1'
                #sys.exit()

        # finish this part in order to make multiple 1D efficiency
        #    else:
        #        c.cd()
        #        #Make Pads
        #        t = ROOT.TPad('t_%s'%effname,'t_%s'%effname, 0, 0.3, 1, 1.0)#top pad
        #        t.SetBottomMargin(0.)
        #        t.SetTopMargin(0.1)
        #        t.Draw()
        #        t.cd()
        #        theff.Draw()
        #        cDict[effname] =  c

        ##add efficiency from other samples on the canvas
        #first_ratio = True 
        #theffDic = {}
        #for key in cDict.keys():
        #    for effL in effList[1:]:
        #        found = False
        #        for eff in effL:
        #            if not eff.name == key:
        #                continue

        #            found = True
        #            theff2 = self.TGraph2TH1F(eff.heff)
        #            ratio = copy.copy(theff2)
        #            ratio.Divide(theff2)
        #            theffDic[key].append([theff2, ratio])

        #        if not found:
        #            print '@ERROR: the file %s doesn\'t containt the efficiency %s. Aborting.' %(effL, eff.name)
        #            sys.exit

        #for key in cDict.keys():
        #    first_ratio = True
        #    for th in theffDic[key]:
        #            cDict[key].GetPad(0).cd()




        #

        #            #found = True
        #            #cDict[key].GetPad(0).cd()
        #            #theff2 = self.TGraph2TH1F(eff.heff)
        #            #theff2.Draw('SAME')
        #            ##cDict[key].GetListOfPrimitives().ls()
        #            ##sys.exit()
        #            ##Draw Ratio
        #            ##cDict[key].GetPad(1).cd()

        #            #ratio = copy.copy(theff2)
        #            #ratio.Divide(theff2)
        #            #if first_ratio:
        #            #    c = cDict[key]
        #            #    print '------------'
        #            #    c.GetListOfPrimitives().ls()
        #            #    c.cd()
        #            #    b = ROOT.TPad('b_%s'%effname,'b_%s'%effname, 0, 0., 1, 0.3)#bottom pad
        #            #    b.SetTopMargin(0.0)
        #            #    b.SetBottomMargin(0.35)
        #            #    b.SetGridy()
        #            #    b.Draw('SAME')
        #            #    b.cd()
        #            #    ratio.GetYaxis().SetRangeUser(0.5, 1.5)
        #            #    ratio.Draw()
        #            #    first_ratio = False 
        #            #    print '------------'
        #            #    c.GetListOfPrimitives().ls()
        #            #    sys.exit()
        #            #    cDict[key] = c
        #            #else: 
        #            #    cDict[key].GetListOfPrimitives().ls()
        #            #    cDict[key].GetPad(0).cd()
        #            #    ratio.Draw('SAME')

        #        #if not found:
        #        #    print '@ERROR: the file %s doesn\'t containt the efficiency %s. Aborting.' %(effL, eff.name)
        #        #    sys.exit

        for key in cDict.keys():
            cDict[key].SaveAs(self.FormatOutputPath('%s/%s.pdf' %(directory,key)))
            cDict[key].SaveAs(self.FormatOutputPath('%s/%s.png' %(directory,key)))


