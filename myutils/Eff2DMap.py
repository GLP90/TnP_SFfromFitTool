import ROOT
import json
import math

class Eff2DMap:
    '''Contain 2D efficiencies'''

    def __init__(self, name):
        self.name = name 
        self.nominal = [] #2D, [y][x]
        self.up = [] #2D, [y][x]
        self.down = [] #2D, [y][x]
        self.xbins = None 
        self.ybins = None
        #Name of the bins
        self.xname = None 
        self.yname = None

        #If map contains SF values, self.up = self.down and full error propagation has already been done during ratio
        self.sf = False

    def Print(self, yval = 'nominal'):
        '''yval can be nominal, up or down'''

        print 'Map\t name\n'
        print yval+'\n'
        print 'x par:\t'+str(self.xname)
        print 'y par:\t'+str(self.yname)

        xhead = '\tx:\t\t'
        for x in self.xbins:
            xhead +=  str(x) + '\t'
        print xhead

        for y in range(0, len(self.ybins)):
            ystr = '\ny:\t' + str(self.ybins[y])
            for x in range(0, len(self.xbins)):
                ystr += '\t'+str(getattr(self,yval)[y][x])
            print ystr

    #def makeJSON(self):
    #    '''Create Json file from map'''
    #    data = {}
    #    par_pair = '%s_%s'%(self.yname,self.xname)
    #    data[par_pair] = {}
    #    for y in range(0, len(self.ybins)):
    #        ypar = '%s:[%.2f,%.2f]'%(self.yname,self.ybins[y][0],self.ybins[y][1])
    #        data[par_pair][ypar] = {}
    #        for x in range(0, len(self.xbins)):
    #            xpar = '%s:[%.2f,%.2f]'%(self.xname, self.xbins[x][0], self.xbins[x][1])
    #            nom = self.nominal[y][x]
    #            err = (math.sqrt(self.up[y][x]**2 +self.down[y][x]**2))
    #            data[par_pair][ypar][xpar] = {'value':nom, 'error':err}

    #    with open ('test.txt', 'w') as f:
    #        json.dump(data, f, sort_keys = False, indent = 4)

    def getJSONdic(self):
        '''Return dictionnary to be written in json file. Used by JsonMaker to make final json file'''
        data = {}
        par_pair = '%s_%s'%(self.yname,self.xname)
        data[par_pair] = {}
        for y in range(0, len(self.ybins)):
            ypar = '%s:[%.2f,%.2f]'%(self.yname,self.ybins[y][0],self.ybins[y][1])
            data[par_pair][ypar] = {}
            for x in range(0, len(self.xbins)):
                xpar = '%s:[%.2f,%.2f]'%(self.xname, self.xbins[x][0], self.xbins[x][1])
                nom = self.nominal[y][x]
                #case of null value
                if self.up[y][x] == -1 and self.down[y][x] == -1:
                    err = -1
                else:
                    if not self.sf: 
                        err = (math.sqrt(self.up[y][x]**2 +self.down[y][x]**2))
                    else: 
                        if not self.up[y][x] == self.down[y][x]:
                            print '@ERROR: SF map but self.down != self.up. Aborting'
                        err = self.up[y][x]
                if nom == -1 and err == -1:
                    data[par_pair][ypar][xpar] = {'value':'null', 'error':'null'}
                    print '@INFO: values for', ypar, 'and', xpar, 'are null. The fit is probably empty'
                else:
                    data[par_pair][ypar][xpar] = {'value':nom, 'error':err}

        return data

    def divideMap(self, effmap):
        '''Return a new map, that is sefl divided by effmap'''
        if self.xbins != effmap.xbins:
            print '@ERROR: maps do not have the same xbins. Cannot divide. Aborting'
        if self.ybins != effmap.ybins:
            print '@ERROR: maps do not have the same ybins. Cannot divide. Aborting'
        if self.name != effmap.name:
            print '@ERROR: map do not have the same name (DEN/NUM)'
            print 'Name of num map is', self.name
            print 'Name of den map is', effmap.name

        #Copy trivial parameters
        ratioMap = Eff2DMap(self.name)
        ratioMap.xbins = self.xbins
        ratioMap.ybins = self.ybins
        ratioMap.xname = self.xname
        ratioMap.yname = self.yname

        nominal = []
        up = []
        down = []
        for y in range(0, len(self.ybins)):
            nominal.append([])
            up.append([])
            down.append([])
            for x in range(0, len(self.xbins)):
                nn, dn = self.nominal[y][x], effmap.nominal[y][x]
                #-1 values are filed in the map when the fit has empty bins
                if nn != -1 and dn != -1 and dn !=0:
                    nominal[y].append(nn/dn)
                else: 
                    #this will be a null value in the json
                    nominal[y].append(-1)

                #Compute error 
                if nn != -1 and dn != -1 and dn !=0:
                    nu, nd, du, dd = self.up[y][x], self.down[y][x], effmap.up[y][x], effmap.down[y][x]
                    err = math.sqrt( (nu/dn)**2 + (nd/dn)**2 + (du/(dn**2))**2  + (dd/(dn**2))**2 )
                else: 
                    #this will be a null value in the json
                    err = -1
                up[y].append(err)
                down[y].append(err)

        ratioMap.nominal = nominal 
        ratioMap.up = up
        ratioMap.down = down
        return ratioMap
                
