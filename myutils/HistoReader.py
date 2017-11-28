import ROOT
#from collections import Counter
import sys
from Efficiency import Efficiency



class HistoReader:
    '''Contains a list of efficiency class'''

    def __init__(self, type_):
        #choose type to indentify the data/sample. e.g.: type = '2016 RunB', type = 'MC 92X'. Will be used for directory names and legends
        self.type_ = type_
        pass

    def readfile(self, inputTree):
        #List of all efficiencies
        self.EffList = []
        file = ROOT.TFile.Open(inputTree)
        rootoutput = file.GetDirectory('tpTree')
        nextkey = ROOT.TIter(rootoutput.GetListOfKeys())
        key = nextkey.Next()
        while (key): #loop
            if key.IsFolder() != 1:
                continue
            self.rawname = key.GetTitle()
            print 'rawname is', self.rawname

            directory = rootoutput.GetDirectory(key.GetTitle())
            effdir = directory.GetDirectory('fit_eff_plots')
            effList = effdir.GetListOfKeys()
            effKey = ROOT.TIter(effList)
            ##Check if 1D efficiency
            #if len(effList) == 1:
            #    self.eff = Efficiency(key.GetTitle())
            ##    print '1D efficiency'
            ##for 2D efficiencies. Finalise later
            #else: 
            ##################################################
            ##More than 1D: need to create multiple efficiency
            ##################################################
            #    pass
            #    #print 'len(effList) is ', len(effList)
            #    #eff = Efficiency('dummy',2)

            #add all the efficieny ditribution in the efficiency 
            effkey = effKey.Next()
            #efflist = []
            #AllEff = {}
            AllEffList = []
            while (effkey):
                #efflist.append(effdir.Get(effkey.GetName()))
                AllEffList.append(effkey.GetName())
                #AllEff[effkey.GetName()] = effdir.Get(effkey.GetName())
                effkey = effKey.Next()
            #print 'AllEff are', AllEff
            self.EffRemover(AllEffList)
            #print 'after removal, AllEff are', AllEff
            #sys.exit()


            #self.eff.addHist([efflist])

            for effkey in AllEffList:
                if not effkey.startswith(self.xpar+'_PLOT'):
                    print 'skiped key', effkey
                    continue

                cEff = effdir.Get(effkey)#TCanvas containing efficiency distribution
                hEff = cEff.GetPrimitive('hxy_fit_eff')
                #cEff.GetListOfPrimitives().ls()
                #print 'heff is', hEff
                
                #sys.exit()
                #self.EffList.append(Efficiency(self.rawname, effkey, effdir.Get(effkey), self.xpar, self.ypars))

                ###
                #Write info about yparams bins
                print 'effkey is', effkey
                yParBinInfo = effkey.split('PLOT')[1]
                yBinList = []
                for y in self.ypars:
                    if '%s_bin' %y in yParBinInfo:
                        yBin = int(yParBinInfo.split('%s_bin' %y)[1].split('_')[0])
                        yBinList.append('%s_bin%i' %(y,yBin))
                #print 'yBinList is', yBinList


                #print 'efflist is', self.EffList
                #    self.eff = Efficiency(key, AllEff[key], xpar)

                #efficienciesForThisID = {}
                ####################
                #Add fit info
                ####################
                keyInDir = ROOT.TIter(directory.GetListOfKeys())
                subkey = keyInDir.Next()

                #Dictonary containing all fits. The key correspond to the bin number
                self.fitDic = {}
                while (subkey):
                    #print 'subkeyname is', subkey.GetName()
                    if subkey.IsFolder() != 1:
                        subkey = keyInDir.Next()
                        continue
                    if subkey.GetName() == 'fitter_tree' or subkey.GetName() == 'fit_eff_plots' or subkey.GetName() == 'cnt_eff_plots':
                        subkey = keyInDir.Next()
                        continue

                    yBinNotFound = False 
                    for yBin in yBinList:
                        if not yBin in subkey.GetName():
                            yBinNotFound = True

                    if yBinNotFound: 
                        print 'skiped', subkey.GetName()
                        subkey = keyInDir.Next()
                        continue
                  
                    ##Retrieve the xbin number
                    xBin = int(subkey.GetName().split('%s_bin' %self.xpar)[1].split('_')[0])

                    ########
                    #Retrieve fit plots
                    ########
                    canvDir = rootoutput.GetDirectory(key.GetTitle()+"/"+subkey.GetName())
                    canv = canvDir.Get('fit_canvas')
                    
                    nbin = self.getBinNumber(subkey.GetName())
                    self.histoFromCanvas(canv, xBin)
                    
                    ###########

                    #self.eff.hpassing[nbin] = self.hpassing
                    #self.eff.funcpassing[nbin] = self.funcpassing
                    #self.eff.hfailing[nbin] = self.hfailing
                    #self.eff.funcfailing[nbin] = self.funcfailing
                       #subkey = keyInDir.Next()
                    if "ratio" in subkey.GetName():
                        theHistoPlot = rootoutput.Get(key.GetTitle()+"/"+subkey.GetName())
                        #efficienciesForThisID[subkey.GetName()] = getHistoContentInJson(theHistoPlot)
                    subkey = keyInDir.Next()
                    
                    ##

                    ##data[key.GetTitle()]=efficienciesForThisID
                    #subkey = keyInDir.Next()

                    #################
                    ##Handle plot bin
                    #################
                    ##BinName = subkey.GetName()
                    ##BinNameList = [b for b in self.ypars BinName.split('__') if ('bin' in b)]

                    ##print 'BinName is', BinName

                    ##canvDir = rootoutput.GetDirectory(key.GetTitle()+"/"+subkey.GetName())
                self.orderFitHisto()
                #self.EffList.append(Efficiency(self.rawname, self.type_,  effkey, effdir.Get(effkey), self.xpar, self.ypars, self.hpassing, self.funcpassing, self.hfailing, self.funcfailing))
                self.EffList.append(Efficiency(self.rawname, self.type_,  effkey, hEff, self.xpar, self.ypars, self.hpassing, self.funcpassing, self.hfailing, self.funcfailing))

            #self.effList.append(self.eff)
            key = nextkey.Next()

    def getBinNumber(self, s):
        binlist = []
        binStringList = s.split('bin')[1:]
        for b in binStringList:
            sbin = b.split('__')[0]
            try:
                nbin =int(sbin)
            except ValueError: 
                print '@ERROR: the nbin is not a string. Aborting'
            binlist.append(nbin)
        print 'binlist is', binlist 
        return nbin

    def EffRemover(self, AllEffList):
        '''When making 2D efficiencies (e.g. pt X eta), all permutation are stored in the .root file. Here only one set of efficiency is keep. The selection criteria is: efficiencies are ploted wrt the  parameter with the largerst number of bins '''
        keyPrefixList = []
        for key in AllEffList:
            keyPrefix = key.split('_PLOT')[0]
            if '_' in keyPrefix: continue
            keyPrefixList.append(keyPrefix)

        #counter = Counter(keyPrefixList)
        #count = {i:keyPrefixList.count(i) for i in keyPrefixList}
        #print 'most commond is', counter.most_common[1][0][1]
        #x = set(keyPrefixList)
        #print 'x is', x 
        self.xpar  = min(set(keyPrefixList), key=keyPrefixList.count)
        print 'xpar is', self.xpar
        print 'keyPrefixList are ', set(keyPrefixList)
        #self.ypars = set(keyPrefixList).remove(self.xpar)
        self.ypars = set(keyPrefixList)
        self.ypars.remove(self.xpar)
        print 'ypars are', self.ypars

        ##print 'occurence is', xvar 
        #for key in AllEffDic.keys():
        #    keyPrefix = key.split('_PLOT')[0]
        #    if keyPrefix != xpar:
        #        del AllEffDic[key]

    def IsCurrentXparam(self, xpar, BinName):
        pass
    



    def histoFromCanvas(self, canvas, xbin):
        '''Read canvas containing passing, failing, passing+failing probe and fit function. Retrieve info and store them in Efficiency'''

        #print 'listing canvas' 
        #canvas.ls()
        #print 'canvas name is', canvas.GetName()
        #print "name is ", subkey.GetName()
        #pad = canvas.GetPad(1)
        #print 'pad name is', pad.GetName()
        #sys.exit()

        fitList = []
        for i in range(1,3):
            print 'canvas name is', canvas.GetName()
            #print 'nbin is', nbin
            pad = canvas.GetPad(i)
            primList = pad.GetListOfPrimitives()
            print primList
            primKey = ROOT.TIter(primList)
            prim = primKey.Next()

            hist = pad.GetPrimitive('h_data_binned')
            #print 'hist name is', hist.GetName()
            #print 'integral is', hist.Integral()
            #fitfunc = pad.GetPrimitive('RooCurvesimPdf_Norm[mass]_Comp[backgroundPass,backgroundFail]')
            #pdfFail_Norm[mass]
            if i == 1:#passing muon
                #fitfunc = pad.GetPrimitive('pdfPass_Norm[mass]_Comp[backgroundPass]')
                fitfunc = pad.GetPrimitive('pdfPass_Norm[mass]')
            elif i == 2: 
                #fitfunc = pad.GetPrimitive('pdfFail_Norm[mass]_Comp[backgroundFail]')
                fitfunc = pad.GetPrimitive('pdfFail_Norm[mass]')
            fitList.append(hist)
            fitList.append(fitfunc)
        #print 'fitList is', fitList
        #sys.exit()
        self.fitDic[xbin] = fitList
            #if i == 1:
            #    #self.hpassing = hist
            #    #self.funcpassing = fitfunc
            #elif i == 2:
            #    #self.hfailing = hist
            #    #self.funcfailing = fitfunc
            #elif i == 3:
            #    #pass
            ##if i == 1:
            ##    self.eff.hpassing[nbin] = hist
            ##    self.eff.funcpassing[nbin] = fitfunc
            ##elif i == 2:
            ##    self.eff.hfailing[nbin] = hist
            ##    self.eff.funcfailing[nbin] = fitfunc
            ##elif i == 3:
            ##    pass

            ###print 'pad name is', pad.GetName()
            ###print 'list of pad objects are'
            ##while (prim):
            ##    #print 'key name is', prim.GetName()
            ###    #pad.GetPrimitive(primKey.GetName())
            ##     
            ##    prim = primKey.Next()
            ###primKey = primKey.Next()
            ##pad.ls()
        pass

    def orderFitHisto(self):
        #self.fitDic = {}
        binlist = sorted(list(self.fitDic))
        self.hpassing = []
        self.funcpassing = []
        self.hfailing = []
        self.funcfailing = []
        for nbin in binlist:
            self.hpassing.append(self.fitDic[nbin][0])
            self.funcpassing.append(self.fitDic[nbin][1])
            self.hfailing.append(self.fitDic[nbin][2])
            self.funcfailing.append(self.fitDic[nbin][3])

        #print '----------'
        #print self.hpassing 
        #print self.funcpassing
        #print self.hfailing
        #print self.funcfailing
        #sys.exit()

    def DrawEfficiency(self):
        pass
        

if __name__ == "__main__":
    
    #test_file = 'FitForTest/TnP_MC_NUM_HighPtID_DEN_genTracks_PAR_phi.root'
    test_file = 'FitForTest/TnP_MC_NUM_hlt_Mu17_Mu8_OR_TkMu8_leg8_DEN_LooseIDnISO_PAR_pt_eta.root'

    hr = HistoReader()
    hr.readfile(test_file)
