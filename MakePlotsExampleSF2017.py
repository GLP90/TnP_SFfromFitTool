import ROOT
from myutils.HistoReader import HistoReader
from myutils.HistoPloter import HistoPloter
from myutils.Efficiency import Efficiency
import sys

#To run ROOT in batch mode
ROOT.gROOT.SetBatch(True)

if __name__ == "__main__":


    ##################


    #ID = [  'TnP_MC_NUM_LooseID_DEN_genTracks_PAR_pt_eta.root',
    #        'TnP_MC_NUM_TightID_DEN_genTracks_PAR_pt_eta.root',
    #        'TnP_MC_NUM_MediumID_DEN_genTracks_PAR_pt_eta.root',
    #        'TnP_MC_NUM_HighPtID_DEN_genTracks_PAR_newpt_eta.root',
    #        'TnP_MC_NUM_TrkHighPtID_DEN_genTracks_PAR_newpt_eta.root',
    #        'TnP_MC_NUM_SoftID_DEN_genTracks_PAR_pt_eta.root',
    #        'TnP_MC_NUM_MediumPromptID_DEN_genTracks_PAR_pt_eta.root'
    #        ]

    ISO = [ 'TnP_MC_NUM_TightRelIso_DEN_MediumID_PAR_pt_eta.root',
            'TnP_MC_NUM_LooseRelIso_DEN_MediumID_PAR_pt_eta.root',
            'TnP_MC_NUM_TightRelIso_DEN_TightIDandIPCut_PAR_pt_eta.root',
            'TnP_MC_NUM_LooseRelIso_DEN_LooseID_PAR_pt_eta.root',
            'TnP_MC_NUM_TightRelTkIso_DEN_TrkHighPtID_PAR_newpt_eta.root',
            'TnP_MC_NUM_LooseRelTkIso_DEN_TrkHighPtID_PAR_newpt_eta.root',
            'TnP_MC_NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_PAR_newpt_eta.root',
            'TnP_MC_NUM_LooseRelIso_DEN_TightIDandIPCut_PAR_pt_eta.root',
            'TnP_MC_NUM_TightRelTkIso_DEN_HighPtIDandIPCut_PAR_newpt_eta.root']

    ID = [  'TnP_MC_NUM_LooseID_DEN_genTracks_PAR_pt_eta.root']
    #ID = ['TnP_MC_NUM_LooseID_DEN_genTracks_PAR_pt_eta.root']
    #ID = ['TnP_MC_NUM_TightID_DEN_genTracks_PAR_pt_eta.root']
    #ID = ['TnP_MC_NUM_MediumID_DEN_genTracks_PAR_pt_eta.root']
    #ID = ['TnP_MC_NUM_HighPtID_DEN_genTracks_PAR_newpt_eta.root']
    #ID = ['TnP_MC_NUM_TrkHighPtID_DEN_genTracks_PAR_newpt_eta.root']
    #ID = ['TnP_MC_NUM_SoftID_DEN_genTracks_PAR_pt_eta.root']
    #ID = ['TnP_MC_NUM_MediumPromptID_DEN_genTracks_PAR_pt_eta.root']

    hr_data_List = []

    #for Id in ID+ISO:
    for Id in ID:
    #for Id in ISO:
    

        print 'Readind'
        print '================'
        print Id
        print '================'

        isid = True
        if Id in ISO: isid = False

         
        #The argument in the HistoPloter is the path where the plots are going to be stored
        hppath = '.'

        ##############
        #DATA
        ##############

        #note: all the lumi taken from the table in 
        #https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmV2017Analysis
        #(With normtag)

        if isid:
            fileBC = '/afs/cern.ch/user/f/fernanpe/public/for_Gael/Efficiencies_2017/EfficiencyID_BC/DATA_dataidBC/'+Id
        else: 
            fileBC = '/afs/cern.ch/user/f/fernanpe/public/for_Gael/Efficiencies_2017/EfficiencyISO_BC/DATA_dataidBC/'+Id
        hr_dataBC = HistoReader('DataBC')#Name of the historeader 
        hr_dataBC.readfile(fileBC)      #Inputfile: the Historeader reads all the efficiencies and fits
        hr_dataBC.SetNewRange(20, 120)  #(optional) Only bins betwen 20 and 120 are kep (inclusive)
        hr_dataBC.CleanBigError(0.05)   #(optional) Give a threhold for the maximum uncertainties allowed in the efficiency distributions. If too large, use average of neighbour bins
        hr_dataBC.setLumi(14.432)       #(optional) Put the lumi of the run. Need to define this when addition efficiencies together
        hr_dataBC.setInfo('BC')         #(optional) Give the run information. Used for legend. Can put whatever text you want.
        hr_dataBC.setType('data')       #(optional) Can be either 'data' or 'MC'. Used for legend

        if isid:
            fileBC = '/afs/cern.ch/user/f/fernanpe/public/for_Gael/Efficiencies_2017/EfficiencyID_BC/MC_mcidBC/'+Id
        else:
            fileF = '/afs/cern.ch/user/f/fernanpe/public/for_Gael/Efficiencies_2017/EfficiencyISO_BC/MC_mcidBC/'+Id
        hr_mcBC = HistoReader('MCBC')
        hr_mcBC.readfile(fileBC)      
        hr_mcBC.SetNewRange(20, 120)  
        hr_mcBC.CleanBigError(0.05)   
        hr_mcBC.setLumi(14.432)       
        hr_mcBC.setInfo('BC')         
        hr_mcBC.setType('mc')
        hp = HistoPloter(hppath)
        hp.PlotEff1D([hr_dataBC, hr_mcBC])
        del hp

        if isid:
           fileDE = '/afs/cern.ch/user/f/fernanpe/public/for_Gael/Efficiencies_2017/EfficiencyID_DE/DATA_dataidDE/'+Id
        else: 
           fileDE = '/afs/cern.ch/user/f/fernanpe/public/for_Gael/Efficiencies_2017/EfficiencyISO_DE/DATA_dataidDE/'+Id
        hr_dataDE = HistoReader('DataDE')
        hr_dataDE.readfile(fileDE)
        hr_dataDE.SetNewRange(20, 120)
        hr_dataDE.CleanBigError(0.05)
        hr_dataDE.setLumi(13.503)
        hr_dataDE.setInfo('DE')
        hr_dataDE.setType('data')
        hr_dataBC.Sum(hr_dataDE)

        if isid:
            fileDE = '/afs/cern.ch/user/f/fernanpe/public/for_Gael/Efficiencies_2017/EfficiencyID_DE/MC_mcidDE/'+Id
        else:
            fileDE = '/afs/cern.ch/user/f/fernanpe/public/for_Gael/Efficiencies_2017/EfficiencyISO_DE/MC_mcidDE/'+Id
        hr_mcDE = HistoReader('MCDE')
        hr_mcDE.readfile(fileDE)
        hr_mcDE.SetNewRange(20, 120)
        hr_mcDE.CleanBigError(0.05)
        hr_mcDE.setLumi(13.503)
        hr_mcDE.setInfo('DE')
        hr_mcDE.setType('mc')

        hp = HistoPloter(hppath)
        hp.PlotEff1D([hr_dataDE, hr_mcDE])
        del hp

        hr_mcBC.Sum(hr_mcDE)

        if isid:
            fileF = '/afs/cern.ch/user/f/fernanpe/public/for_Gael/Efficiencies_2017/EfficiencyID_F/DATA_dataidF/'+Id
        else:
            fileF = '/afs/cern.ch/user/f/fernanpe/public/for_Gael/Efficiencies_2017/EfficiencyISO_F/DATA_dataidF/'+Id

        hr_dataF = HistoReader('DataF')
        hr_dataF.readfile(fileF)
        hr_dataF.SetNewRange(20, 120)
        hr_dataF.CleanBigError(0.05)
        hr_dataF.setLumi(13.433)
        hr_dataF.setInfo('F')
        hr_dataF.setType('data')
        hr_dataBC.Sum(hr_dataF) #The efficiency distributions in hr_dataBC are now the lumi-reweigted sum of hr_dataBC, hr_dataDE, hr_dataF
 
        if isid:
            fileF = '/afs/cern.ch/user/f/fernanpe/public/for_Gael/Efficiencies_2017/EfficiencyID_F/MC_mcidF/'+Id
        else:
            fileF = '/afs/cern.ch/user/f/fernanpe/public/for_Gael/Efficiencies_2017/EfficiencyISO_F/MC_mcidF/'+Id

        hr_mcF = HistoReader('MCF')
        hr_mcF.readfile(fileF)
        hr_mcF.SetNewRange(20, 120)
        hr_mcF.CleanBigError(0.05)
        hr_mcF.setLumi(13.433)
        hr_mcF.setInfo('F')
        hr_mcF.setType('mc')

        hp = HistoPloter(hppath)
        hp.PlotEff1D([hr_dataF, hr_mcF])
        del hp

        hr_mcBC.Sum(hr_mcF) #The efficiency distributions in hr_mcF are now the lumi-reweigted sum of hr_mcBC, hr_mcDE, hr_mcF

        ##Make 1D efficiency plots for multiple sample
        #hp = HistoPloter(hppath)
        #hp.PlotEff1D([hr_dataBC, hr_mcBC])

