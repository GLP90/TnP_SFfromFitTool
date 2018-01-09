import ROOT
from Efficiency import Efficiency
import os
import sys
import numpy as np
import copy as copy
import math

import array

ROOT.gROOT.LoadMacro('include/GoodnessOfFit.cc+')
ROOT.gROOT.LoadMacro('include/KSandADWithToys.cc+')
ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.WARNING)


class HistoPloter:
    '''Plot the relevant histogram, fits'''

    def __init__(self, outputpath):
        self.outputpath = outputpath
        self.effUpRange = 1.05
        self.effDownRange = 0.8
        self.KSs      = [] 
        self.ADs      = [] 
        self.maxPulls = []
        self.chi2s    = []
        self.sFactors = []

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
        print 'we are here'
        #Start by creating directory if not existing
        #directory = self.CreateOutputFolder('%s/%s/%s'%('Plots/Fits',eff.type_.replace(' ',''),eff.name.replace('&','and'),))
        directory = self.FormatOutputPath('%s/%s/%s'%('Plots/Fits',eff.type_,eff.name))
        directory = self.CreateOutputFolder(directory)

        print 'eff.hpassing is', eff.hpassing
        print 'eff.funcpassing is', eff.funcpassing
        print 'eff.hfail is', eff.hfailing
        print 'eff.funcfail is', eff.funcfailing
        print 'eff.rooworksp is', eff.rooworksp
        nbin = 0 
        if eff.hpassing:
            print 'len is', len(zip(eff.hpassing, eff.funcpassing, eff.hfailing, eff.funcfailing))

        for w in eff.rooworksp:
            if not w: continue
            nbin += 1
            mass = w.var('mass')
            data = w.data('data')
            
            KS_pf      = []
            AD_pf      = []
            maxPull_pf = []
            chi_pf     = []
            sFactor_pf = []
            
            for ty in ['Pass','Fail']:
                frame   = mass.frame()
                redData = data.reduce(ROOT.RooArgSet(mass), "_efficiencyCategory_==%d"%(1 if ty == 'Pass' else 0))
                redData.Print()
                hist = ROOT.RooAbsData.createHistogram(redData, ty+'Hist',mass)

                pdf     = w.pdf('pdf'+ty)
                redData.plotOn(frame)
                pdf    .plotOn(frame)
                
                pullHist = frame.pullHist()
                hPullHist=ROOT.TGraph(pullHist)
                x = ROOT.Double(0); y = ROOT.Double(0)
                ys = []
                ys2= []

                for i in range(1, pullHist.GetN()+1):
                    pullHist.GetPoint(i, x, y)
                    ys.append(ROOT.Double(y))
                    ys2.append(0 if not hist.GetBinContent(i) else ROOT.Double(y)/math.sqrt(hist.GetBinContent(i)))

                c = ROOT.TCanvas('c','c')
                c.cd()
                frame.Draw()

                pullFrame = mass.frame()
                pullFrame.addPlotable(pullHist)


                maxPull = max(ys)
                minPull = min(ys)

                maxSFac = max(ys2); minSFac=min(ys2)

                maxPull = max(map(abs, [maxPull,minPull]))
                sFactor = max(map(abs, [maxSFac,minSFac]))

                KS=ROOT.EvaluateADDistance(pdf, redData, mass, True)
                AD=ROOT.EvaluateADDistance(pdf, redData, mass, False)

                # model = ROOT.RooStats.ModelConfig()
                # model.SetPdf(pdf)
                # calculator = ROOT.RooStats.AsymptoticCalculator(data, model, model)
                

                # KS = ROOT.Double(0.)
                # AD = ROOT.Double(0.)
                
                # ROOT.KSandADWithToys(KS, AD, redData, pdf, mass)
                


                
                tl1 = ROOT.TLatex(110,0.10*frame.GetMaximum(), '#chi^{2}/ndof = %4.2f'%frame.chiSquare())
                tl2 = ROOT.TLatex(110,0.15*frame.GetMaximum(), 'maxPull = %4.2f'%maxPull )
                tl3 = ROOT.TLatex(110,0.20*frame.GetMaximum(), 'KS = %4.2f'%KS )
                tl4 = ROOT.TLatex(110,0.25*frame.GetMaximum(), 'AD = %4.2f'%AD )
                tl5 = ROOT.TLatex(110,0.30*frame.GetMaximum(), 'S-factor = %4.2f'%sFactor )
                
                KS_pf     .append(KS*math.sqrt(data.numEntries()))     
                AD_pf     .append(AD)                                  
                maxPull_pf.append(maxPull)
                chi_pf    .append(frame.chiSquare())
                sFactor_pf.append(sFactor_pf)

                tl1.Draw('same')
                tl2.Draw('same')
                tl3.Draw('same')
                tl4.Draw('same')
                tl5.Draw('same')

                c.SaveAs(directory+'/%s_%i.pdf' %(ty, nbin))
                c.SaveAs(directory+'/%s_%i.png' %(ty, nbin))
                c.SaveAs(directory+'/%s_%i.root'%(ty, nbin))
                
                
            self.KSs     .append(max(KS_pf))
            self.ADs     .append(max(AD_pf))
            self.maxPulls.append(max(maxPull_pf))
            self.chi2s   .append(max(chi_pf))
            self.sFactors.append(max(sFactor_pf))

#         for hp, fp, hf, ff, w in zip(eff.hpassing, eff.funcpassing, eff.hfailing, eff.funcfailing, eff.rooworksp):
#             nbin += 1
#             print 'nbin is', nbin
#             mass = w.var('mass')
#             data = w.data('data')     

#             framePass = mass.frame()
#             frameFail = mass.frame()

#             #Draw passing
#             c = ROOT.TCanvas('c','c')
#             c.cd()
#             hp.Draw()
#             fp.Draw('same')
            
#             dataPass=data.reduce(ROOT.RooArgSet(mass), "_efficiencyCategory_==1")
#             pdfPass =w.pdf('pdfPass')
#             dataPass.plotOn(framePass)
#             pdfPass.plotOn(framePass)
#             print hp

#             maxPull = max( map( abs, [framePass.pullHist().GetMaximum(),framePass.pullHist().GetMinimum()]))
#             print maxPull
#             print hp.getYAxisMax()
# #            tl = ROOT.TLatex(110,0.1*hp.getYAxisMax(), '#chi^{2}/4 = %4.2f'%fp.chiSquare(hp,4))
#             tl = ROOT.TLatex(110,0.1*hp.getYAxisMax(), '#chi^{2}/ndof = %4.2f'%framePass.chiSquare())

#             print 0.1*hp.getYAxisMax()
#             tl = ROOT.TLatex(110,0.1*hp.getYAxisMax(), 'maxPull = %4.2f'%maxPull)
#             print '#chi^{2}/4 = %4.2f'%fp.chiSquare(hp,4)
#             tl.Draw('same')
#             c.SaveAs(directory+'/pass_%i.pdf'%nbin)
#             c.SaveAs(directory+'/pass_%i.png'%nbin)
#             c.SaveAs(directory+'/pass_%i.root'%nbin)


#             framePull = mass.frame()
#             pull = framePass.pullHist()
#             framePull.addPlotable(pull,'P')

            
#             c2 = ROOT.TCanvas('c2','c2')
#             framePull.Draw()
#             c2.SaveAs(directory+'/pass_pull%i.png'%nbin)
#             print 'maximum and minimum are', 
#             for i in pull.GetX(): print i,

#             #Draw failing
#             c = ROOT.TCanvas('c','c')
#             c.cd()
#             hf.Draw()
#             ff.Draw('same')
#             dataFail=data.reduce(ROOT.RooArgSet(mass), "_efficiencyCategory_==0")
#             pdfFail = w.pdf('pdfFail')
#             dataFail.plotOn(frameFail)
#             pdfFail .plotOn(frameFail)
# #            tl = ROOT.TLatex(110,0.1*hf.getYAxisMax(), '#chi^{2}/4 = %4.2f'%ff.chiSquare(hf,4))
#             pull = frameFail.pullHist()
#             mn = ROOT.TMath.LocMin( pull.GetN(), pull.GetX())
#             mx = ROOT.TMath.LocMax( pull.GetN(), pull.GetX())

#             print 'maximum and minimum are', mn, mx, pull.GetN()
#             for i in pull.GetX(): print i,


#             maxPull = max( map( lambda x : abs(pull.GetX()[x]), [mn, mx] ))
#             tl = ROOT.TLatex(110,0.1*hf.getYAxisMax(), '#chi^{2}/ndof = %4.2f'%frameFail.chiSquare())
#             tl = ROOT.TLatex(110,0.2*hf.getYAxisMax(), 'maxPull = %4.2f'%maxPull)
#             print '#chi^{2}/4 = %4.2f'%ff.chiSquare(hf,4)
#             tl.Draw('same')
#             c.SaveAs(directory+'/fail_%i.pdf'%nbin)
#             c.SaveAs(directory+'/fail_%i.png'%nbin)
#             c.SaveAs(directory+'/fail_%i.root'%nbin)
#             print kk
    def PlotFitList(self, effList):
        '''Plot and save fits for a list of efficiencies'''
        print 'efflist is', effList
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

        if len(effList[0]) == 0: return

        effFolder = effList[0][0].type_
        for effL in effList[1:]:
            effFolder+= '_AND_%s'%effL[0].type_
        print '#######', effFolder
        effFolder = self.FormatOutputPath(effFolder)
        
        #print 'effFolder is', effFolder
        directory = self.CreateOutputFolder('%s/%s'%('Plots/Efficiency',effFolder))
        #directory = self.FormatOutputPath(directory)
        
        print 'directory is', directory

        cDict = {} #Dictionnary of canvas
        for eff in effList[0]:
            if not eff.heff: continue
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


