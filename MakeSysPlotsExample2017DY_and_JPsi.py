#Make all the plots
#

import ROOT
from myutils.HistoReader import HistoReader
from myutils.HistoPloter import HistoPloter
from myutils.Efficiency import Efficiency
from myutils.JsonMaker import JsonMaker
from  multiprocessing import Process
import time
#import sys as SYS

#To run ROOT in batch mode
ROOT.gROOT.SetBatch(True)

if __name__ == "__main__":

    #####################
    #Some function you need
    #####################


    def Gethr(lumi, run, file, name, info):
        ''' retrieve historeader for a single efficiency'''
        hr = HistoReader(name)
        hr.setInfo(info)         
        hr.readfile(file)
        hr.setLumi(lumi)
        hr.setType(info)
        return hr

    def GetSumLumihr(lumiDic, runList, file, name, info):
        ''' retrieve historeader in case separated for multiple runs'''
        hr = HistoReader(name)
        for run in runList:
            file = file.replace('RUN', run)
            if run == runList[0]:
                hr = Gethr(lumiDic[run], run, file, name, info)
            else:
                hr_run = Gethr(lumiDic[run], run, file, name, info)
                hr.Sum(hr_run)

        return hr

    ######################
    #Compare the efficiency
    ######################


    ############To make efficiency comparison
    #This is a list of historeader. All the historeader in this list will be ploted simultaneously
    hrList = []

    #Histogram from DY
    runList = ['BC', 'DE', 'F']
    lumiDic = {'BC':14.432, 'DE':13.503, 'F':13.433}
    file = '/afs/cern.ch/user/f/fernanpe/public/for_Gael/Efficiencies_2017/EfficiencyID_RUN/DATA_dataidRUN/TnP_MC_NUM_LooseID_DEN_genTracks_PAR_pt_eta.root'
    name = 'DY'

    hr = GetSumLumihr(lumiDic, runList, file, name, 'DY')
    hr.SetNewRange(20, 40) 
    hrList.append(hr)


    #file for loose J/Psi: 
    file = '/afs/cern.ch/user/s/sfonseca/public/for_Gael/nominal/EfficiencyRun2017B_F/DATA_data_all/TnP_MC_NUM_LooseID_DEN_genTracks_PAR_pt_eta.root'
    hr = Gethr( '1', 'BCDEF', file, 'JPsi', 'Jpsi')
    hrList.append(hr)
    
    hp = HistoPloter('.')
    hp.PlotEff1D(hrList)#making the 1D plot


    ######################
    #Compare the SF (work in progess..., do not use now)
    ######################

    ##Histogram from DY
    #runList = ['BC', 'DE', 'F']
    #lumiDic = {'BC':14.432, 'DE':13.503, 'F':13.433}

    #file_data = '/afs/cern.ch/user/f/fernanpe/public/for_Gael/Efficiencies_2017/EfficiencyID_RUN/DATA_dataidRUN/TnP_MC_NUM_LooseID_DEN_genTracks_PAR_pt_eta.root'
    #name = 'DY'

    #hr_data = GetSumLumihr(lumiDic, runList, file_data, name)
    #print 'debug 1'

    #file_mc = '/afs/cern.ch/user/f/fernanpe/public/for_Gael/Efficiencies_2017/EfficiencyID_RUN/MC_mcidRUN/TnP_MC_NUM_LooseID_DEN_genTracks_PAR_pt_eta.root'
    #hr_mc = GetSumLumihr(lumiDic, runList, file_mc, name)
    #print 'debug 2'

    #hr_SF_DY = hr_data.Divide(hr_mc)
    #print 'debug 3'


    ##on DY

    ##on J/Psi
    ##Make data hr
    #file_data = '/afs/cern.ch/user/s/sfonseca/public/for_Gael/nominal/EfficiencyRun2017B_F/DATA_data_all/TnP_MC_NUM_LooseID_DEN_genTracks_PAR_pt_eta.root'
    #hr_data = Gethr('1', 'BCDEF', file_data, 'JPsi')
    ##hr_data.SetNewRange(20, 40) 
    #print 'debug'

    #file_mc = '/afs/cern.ch/user/s/sfonseca/public/for_Gael/nominal/EfficiencyRun2017B_F/MC_mc_all/TnP_MC_NUM_LooseID_DEN_genTracks_PAR_pt_eta.root'
    #hr_mc = Gethr('1', 'BCDEF', file_mc, 'JPsi')
    ##hr_mc.SetNewRange(20, 40) 

    #hr_SF_JPsi = hr_data.Divide(hr_mc)
    #hr_SF_JPsi.SetNewRange(20, 40) 

    #hp = HistoPloter('.')
    ##hp.PlotEff1D([hr_SF_DY, hr_SF_JPsi])
    ##hp.PlotEff1D([hr_SF_DY])


   




