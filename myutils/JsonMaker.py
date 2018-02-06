import ROOT
import json
import pkl

class JsonMaker:
    '''Make a json from a group of Eff2DMap or hr.'''

    def __init__(self, filename):
        self.filename = filename

    def makeJSON(self, Eff2MmapList):
        data = {}
        for eff in Eff2MmapList:
            data[eff.name]  = eff.getJSONdic()

        with open ('%s.json'%self.filename, 'w') as f:
            json.dump(data, f, sort_keys = False, indent = 4)

        with open ('%s.pkl'%self.filename, 'w') as f:
            pkl.dump(data, f)


