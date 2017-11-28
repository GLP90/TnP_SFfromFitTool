import ROOT
from myutils.HistoReader import HistoReader
from myutils.HistoPloter import HistoPloter
from myutils.Efficiency import Efficiency

#To run ROOT in batch mode
ROOT.gROOT.SetBatch(True)

if __name__ == "__main__":
    
    #input root file containing all the efficiencies
    test_file = 'FitForTest/TnP_MC_NUM_hlt_Mu17_Mu8_OR_TkMu8_leg8_DEN_LooseIDnISO_PAR_pt_eta.root'
    #path where all the plots are going to be saved
    plot_path = '/afs/cern.ch/work/g/gaperrin/private/TnP/TnP_SFfromFitTool/CMSSW_9_2_4/src/MuonAnalysis/TagAndProbe/test/zmumu/TnP_SFfromFitTool'

    hr = HistoReader('Data test2')
    hr.readfile(test_file)

    effList = hr.EffList  

    hp = HistoPloter(plot_path)

    ##Plot add the fits
    #hp.PlotFitList(effList)

    #Make all 1D efficiency plots
    hp.PlotEff1D([effList])
    #hp.PlotEff1D([effList,effList])

