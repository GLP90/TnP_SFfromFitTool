#Make all the plots
#

import ROOT
from myutils.HistoReader import HistoReader
from myutils.HistoPloter import HistoPloter
from myutils.Efficiency import Efficiency
from myutils.JsonMaker import JsonMaker
from  multiprocessing import Process
import sys

#To run ROOT in batch mode
ROOT.gROOT.SetBatch(True)

if __name__ == "__main__":


    ##################
    #Main path where all the root files are stored
    path_in =  '/afs/cern.ch/user/f/fernanpe/public/for_Gael/Systematics_2017'

    
    #List of all the systematic variations 
    sysList = ['nominal', 'mass_up', 'mass_down', 'tag_up', 'tag_down', 'signalvar']

    #

    #ID = ['TnP_MC_NUM_LooseID_DEN_genTracks_PAR_pt_eta.root']

    ID = [  
            'TnP_MC_NUM_LooseID_DEN_genTracks_PAR_pt_eta.root',
            'TnP_MC_NUM_TightID_DEN_genTracks_PAR_pt_eta.root',
            'TnP_MC_NUM_MediumID_DEN_genTracks_PAR_pt_eta.root',
            'TnP_MC_NUM_HighPtID_DEN_genTracks_PAR_newpt_eta.root',
            'TnP_MC_NUM_TrkHighPtID_DEN_genTracks_PAR_newpt_eta.root',
            'TnP_MC_NUM_SoftID_DEN_genTracks_PAR_pt_eta.root',
            'TnP_MC_NUM_MediumPromptID_DEN_genTracks_PAR_pt_eta.root'
            ]

    #ISO = []

    ISO = [ 
            'TnP_MC_NUM_TightRelIso_DEN_MediumID_PAR_pt_eta.root',
            'TnP_MC_NUM_LooseRelIso_DEN_MediumID_PAR_pt_eta.root',
            'TnP_MC_NUM_TightRelIso_DEN_TightIDandIPCut_PAR_pt_eta.root',
            'TnP_MC_NUM_LooseRelIso_DEN_LooseID_PAR_pt_eta.root',
            'TnP_MC_NUM_TightRelTkIso_DEN_TrkHighPtID_PAR_newpt_eta.root',
            'TnP_MC_NUM_LooseRelTkIso_DEN_TrkHighPtID_PAR_newpt_eta.root',
            'TnP_MC_NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_PAR_newpt_eta.root',
            'TnP_MC_NUM_LooseRelIso_DEN_TightIDandIPCut_PAR_pt_eta.root',
            'TnP_MC_NUM_TightRelTkIso_DEN_HighPtIDandIPCut_PAR_newpt_eta.root'
    ]


    Run = ['BC', 'DE', 'F']
    #Run = ['BC']
    Type = ['mc', 'data']
    #Type = ['mc']
    Num = ['ISO', 'ID']
    Num = ['ISO', 'ID']

    NumDic = {'ISO':ISO, 'ID':ID}
    LumiDic = {'BC':14.432, 'DE':13.503, 'F':13.433}

    def makePlots(n, r, s, t):
        hrList = [] 
        for sys in sysList:
        #All the rest will be within the json file
            print t
            file_ = '%s/Efficiency%s_%s_%s/%s_%sid%s_%s/%s'%(path_in,n,r,sys,t.upper(),t,r,sys,s)
            print 'file_ is', file_
            hr = HistoReader('%s%s%s'%(n,t,sys))
            hr.readfile(file_)     
            hr.SetNewRange(20, 120) 
            hr.setInfo(sys)         
            hr.CleanBigError(0.01)  
            hr.setType(t)      
            hrList.append(hr)
        
        hp = HistoPloter('.')
        hp.setRatioRange(0.98, 1.02)#Set the ratio range. Default one is 0.85, 1.15
        hp.PlotEff1D(hrList)#making the 1D plot


    #########
    #Provide Plots for run BC, DE and F
    #########
    jobs = []
    for n in Num:
        for r in Run: 
            for s in NumDic[n]:
                for t in Type:
                    #print 'yeah'
                    #makePlots(n, r, s, t)
                    p = Process(target=makePlots, args=(n,r,s,t,))
                    jobs.append(p)
                    p.start()
                    #hrList = [] 
                    #for sys in sysList:
                    ##All the rest will be within the json file
                    #    print t
                    #    file_ = '%s/Efficiency%s_%s_%s/%s_%sid%s_%s/%s'%(path_in,n,r,sys,t.upper(),t,r,sys,s)
                    #    print 'file_ is', file_
                    #    hr = HistoReader('%s%s%s'%(n,t,sys))
                    #    hr.readfile(file_)     
                    #    hr.SetNewRange(20, 120) 
                    #    hr.setInfo(sys)         
                    #    hr.CleanBigError(0.01)  
                    #    hr.setType(t)      
                    #    hrList.append(hr)

                    #hp = HistoPloter('.')
                    #hp.setRatioRange(0.98, 1.02)#Set the ratio range. Default one is 0.85, 1.15
                    #hp.PlotEff1D(hrList)#making the 1D plot

################
#OLD Below
###############

#    #########
#    #Provide Plots separetly for run BCDEF
#    #########
#    for n in Num:
#        for s in NumDic[n]:
#            DATA_hrList = []
#            MC_hrList = []
#            for r in Run: 
#                #All the rest will be within the json file
#                for t in Type:
#                    file_ = '/afs/cern.ch/user/f/fernanpe/public/for_Gael/Efficiencies_2017/Efficiency%s_%s/%s_%sid%s/%s'%(n,r,t.upper(),t,r,s)
#                    hr = HistoReader('%s%s'%(t,r))
#                    hr.readfile(file_)     
#                    hr.SetNewRange(20, 120) 
#                    hr.setInfo(r)         
#                    hr.CleanBigError(0.01)  
#                    hr.setLumi(LumiDic[r])
#                    hr.setType(t)      
#                    #For SF
#                    if t == 'mc':
#                        MC_hrList.append(hr)
#                    elif t == 'data':
#                        DATA_hrList.append(hr)
#
#            DATA_hr = DATA_hrList[0]
#            MC_hr = MC_hrList[0]
#            for d in DATA_hrList[1:]:
#                DATA_hr.Sum(d)
#
#            for d in MC_hrList[1:]:
#                MC_hr.Sum(d)
#
#            hp = HistoPloter('.')
#            hp.PlotEff1D([DATA_hr, MC_hr])
#
#    #########
#    #Will contain hr for run BC, DE and F to compute SF on BCDEF
#    #########
#    for n in Num:
#        #Used for SF
#        SF_MapList = []
#        MC_MapList = []
#        DATA_MapList = []
#        SFoutputJSONname ='RunBCDEF_%s_%s'%('SF',n)
#        jSF = JsonMaker(SFoutputJSONname)
#        for t in Type:
#            #All the rest will be within the json file
#            outputJSONname ='RunBCDEF_%s_%s'%(t,n)
#            j = JsonMaker(outputJSONname)
#            MapList = []
#            for s in NumDic[n]:
#                #Contains hr from Run BC, DE and F that will be summed up at the end
#                hrList = []
#                for r in Run: 
#                    file_ = '/afs/cern.ch/user/f/fernanpe/public/for_Gael/Efficiencies_2017/Efficiency%s_%s/%s_%sid%s/%s'%(n,r,t.upper(),t,r,s)
#                    hr = HistoReader('hr')
#                    hr.readfile(file_)     
#                    hr.SetNewRange(20, 120) 
#                    hr.setLumi(LumiDic[r])
#                    hr.CleanBigError(0.05)  
#                    hr.setInfo('dummy')         
#                    hr.setType(t)      
#                    hrList.append(hr)
#
#                #lumi sum of all the hr
#                hr0 = hrList[0]
#                for hr in hrList[1:]:
#                    hr0.Sum(hr)
#
#                MapList.append(hr0.eff2D)
#
#                #For SF
#                if t == 'mc':
#                    MC_MapList.append(hr0.eff2D)
#                elif t == 'data':
#                    DATA_MapList.append(hr0.eff2D)
#            #For DATA, MC
#            j.makeJSON(MapList)
#
#        #For SF
#        for mcm, datam in zip(MC_MapList,DATA_MapList):
#            SF_MapList.append(datam.divideMap(mcm))
#
#        jSF.makeJSON(SF_MapList)
