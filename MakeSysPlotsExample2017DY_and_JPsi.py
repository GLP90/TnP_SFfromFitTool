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

    #This is a list of historeader. All the historeader in this list will be ploted simultaneously
    hrList = []

    #file for loose DY:
    LumiDic = {'BC':14.432, 'DE':13.503, 'F':13.433}
    hr = HistoReader('DY')
    for run in ['BC', 'DE', 'F']:

        file_DY = '/afs/cern.ch/user/f/fernanpe/public/for_Gael/Efficiencies_2017/EfficiencyID_%s/DATA_dataid%s/TnP_MC_NUM_LooseID_DEN_genTracks_PAR_pt_eta.root' % (run,run)

        if run == 'BC':
            hr = HistoReader('DY')
            hr.setInfo(run)         
            hr.readfile(file_DY)
            hr.setLumi(LumiDic[run])
        else:
            hr_run = HistoReader('DY')
            hr_run.setInfo(run)         
            hr_run.readfile(file_DY)
            hr_run.setLumi(LumiDic[run])
            hr.Sum(hr_run)

    hrList.append(hr) 


    hr.readfile(file_DY)     
    hr.SetNewRange(20, 40) 
    hr.setInfo('DY')         
    #hr.CleanBigError(0.01)  
    hr.setType('DY')      
    hrList.append(hr)

    #file for loose J/Psi: 
    file_JPsi = '/afs/cern.ch/user/s/sfonseca/public/for_Gael/nominal/EfficiencyRun2017B_F/DATA_data_all/TnP_MC_NUM_LooseID_DEN_genTracks_PAR_pt_eta.root'
    hr = HistoReader('JPsi')
    hr.readfile(file_JPsi)     
    hr.setInfo('JPsi')         
    #hr.CleanBigError(0.01)  
    hr.setType('JPsi')      
    hrList.append(hr)
    
    hp = HistoPloter('.')
    hp.PlotEff1D(hrList)#making the 1D plot


