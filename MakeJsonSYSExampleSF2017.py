#Creates all the jsons
#

import ROOT
from myutils.HistoReader import HistoReader
from myutils.HistoPloter import HistoPloter
from myutils.Efficiency import Efficiency
from myutils.JsonMaker import JsonMaker
from myutils.RootFileMaker import RootFileMaker
import sys as system

#To run ROOT in batch mode
ROOT.gROOT.SetBatch(True)

if __name__ == "__main__":



    ID = [  'TnP_MC_NUM_LooseID_DEN_genTracks_PAR_pt_eta.root',
            'TnP_MC_NUM_TightID_DEN_genTracks_PAR_pt_eta.root',
            'TnP_MC_NUM_MediumID_DEN_genTracks_PAR_pt_eta.root',
            'TnP_MC_NUM_HighPtID_DEN_genTracks_PAR_newpt_eta.root',
            'TnP_MC_NUM_TrkHighPtID_DEN_genTracks_PAR_newpt_eta.root',
            'TnP_MC_NUM_SoftID_DEN_genTracks_PAR_pt_eta.root',
            'TnP_MC_NUM_MediumPromptID_DEN_genTracks_PAR_pt_eta.root'
            ]

    ISO = [ #'TnP_MC_NUM_TightRelIso_DEN_MediumID_PAR_pt_eta.root',
            #'TnP_MC_NUM_LooseRelIso_DEN_MediumID_PAR_pt_eta.root',
            #'TnP_MC_NUM_TightRelIso_DEN_TightIDandIPCut_PAR_pt_eta.root',
            #'TnP_MC_NUM_LooseRelIso_DEN_LooseID_PAR_pt_eta.root',
            #'TnP_MC_NUM_TightRelTkIso_DEN_TrkHighPtID_PAR_newpt_eta.root',
            #'TnP_MC_NUM_LooseRelTkIso_DEN_TrkHighPtID_PAR_newpt_eta.root',
            #'TnP_MC_NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_PAR_newpt_eta.root',
            #'TnP_MC_NUM_LooseRelIso_DEN_TightIDandIPCut_PAR_pt_eta.root',
            #'TnP_MC_NUM_TightRelTkIso_DEN_HighPtIDandIPCut_PAR_newpt_eta.root'
            ]

    #for the systematics
    sysList = ['nominal', 'mass_up', 'mass_down', 'tag_up', 'tag_down', 'signalvar', 'nbins_up', 'nbins_down']

    path_in = '/afs/cern.ch/user/f/fernanpe/public/for_Gael/Systematics_2017_Full_May18'

    Run = ['BC', 'DE', 'F']
    #Run = ['BC']
    Type = ['mc', 'data']
    #Num = ['ISO', 'ID']
    Num = ['ID']
    #Num = ['ISO']

    NumDic = {'ISO':ISO, 'ID':ID}
    LumiDic = {'BC':14.432, 'DE':13.503, 'F':13.433}


    #########
    #Will contain hr for run BC, DE and F to compute SF on BCDEF
    #########
    for n in Num:
        #Used for SF
        SF_MapList = []
        MC_MapList = []
        DATA_MapList = []
        SFoutputJSONname ='RunBCDEF_%s_%s'%('SF',n)
        #jSF = JsonMaker(SFoutputJSONname)
        #rSF = RootFileMaker(SFoutputJSONname)
        # Will now loop over the syslist. Need to store the the SF map for each variation
        sysSFMapList = {} 
        for sys in sysList:
            # for each sys variation, store data and mc maps
            sysSFMapList[sys] = {} 
            for t in Type:
                MapList = []
                ##All the rest will be within the json file
                #outputJSONname ='RunBCDEF_%s_%s'%(t,n)
                #j = JsonMaker(outputJSONname)
                #r_ = RootFileMaker(outputJSONname)
                MapList = []
                for s in NumDic[n]:
                    #Contains hr from Run BC, DE and F that will be summed up at the end
                    hrList = []
                    for r in Run: 
                        file_ = '%s/Efficiency%s_%s_%s/%s_%sid%s_%s/%s'%(path_in,n,r,sys,t.upper(),t,r,sys,s)
                        hr = HistoReader('hr')
                        hr.setInfo(sys+' '+t)         
                        hr.readfile(file_)     
                        hr.SetNewRange(20, 120) 
                        hr.setLumi(LumiDic[r])
                        #hr.CleanBigError(0.05)  
                        hr.setType(t)      
                        hrList.append(hr)

                    #lumi sum of all the hr
                    hr0 = hrList[0]
                    for hr in hrList[1:]:
                        hr0.Sum(hr)

                    MapList.append(hr0.eff2D)

                    ##For SF
                    #if t == 'mc':
                    #    MC_MapList.append(hr0.eff2D)
                    #elif t == 'data':
                    #    DATA_MapList.append(hr0.eff2D)

                    #print 't is', t
                sysSFMapList[sys][t] = hr0.eff2D

        # done looping over all the sys
        # create SF map for all the sys
        for sys in sysSFMapList:
            SF_map = sysSFMapList[sys]['data'].divideMap(sysSFMapList[sys]['mc'])
            sysSFMapList[sys]['sf'] = SF_map

        # loop over all the sys and store corresponding jsons and root files
        for sys in sysSFMapList:
            for t in Type+['sf']:
                IDname = sysSFMapList[sys][t].name 
                JSONname = 'DYJsonSYS/Run%s_%s_%s_%s'%('BCDEF',t,sys,IDname)
                jSF = JsonMaker(JSONname)
                rSF = RootFileMaker(JSONname)
                jSF.makeJSON([sysSFMapList[sys][t]])
                rSF.makeROOT([sysSFMapList[sys][t]])

                # save nominal/sys ratio (to see change)
                sys_ratio_map = sysSFMapList['nominal'][t].divideMap(sysSFMapList[sys][t])
                IDname = sys_ratio_map.name 
                JSONname = 'DYJsonSYS/Run%s_%s_nominalRatio_%s_%s'%('BCDEF',t,sys,IDname)
                rSF = RootFileMaker(JSONname)
                rSF.cutstomRange(0.95, 1.05)
                rSF.makeROOT([sys_ratio_map])

        # computing the sys uncertainties here
        # list of 2DMap. The first items is the nominal. Other items are all the sys variation (order not relevant)
        #sysVarList = []

        # first test on data
        # add nominal value
        # add rest of sys
        for t in Type+['sf']:
            sysVarList = []
            for sys in sysSFMapList:
                if sys == 'nominal': continue
                sysVarList.append(sysSFMapList[sys][t])

            sysMap = sysSFMapList['nominal'][t].evalSysUncertainties(sysVarList)
            IDname = sysMap.name 
            JSONname = 'DYJsonSYS/Run%s_%s_%s_%s'%('BCDEF',t,'SYS',IDname)
            jSF = JsonMaker(JSONname)
            rSF = RootFileMaker(JSONname)
            jSF.makeJSON([sysMap])
            rSF.makeROOT([sysMap])
