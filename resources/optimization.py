
def generateStates(inputs,grid,nextgrid):
    for state in grid:
        for u in inputs:
            totalcost = 0
            for dev in u.devices:
                statecost = dev.costFn(state[dev.name])
                [endstate, controlcost] = dev.previewstep(state[dev.name],u[dev.name])
                stepcost = statecost + controlcost;
                #interpolate optimal cost from end state
                nextstepopt = dpinterp(endstate,nextstate)

class StateGridPoint(object):
    def __init__(self,period,components,costfunc):
        self.components = components
        self.statecost = costfunc(period,components)
        self.optimalinput = None 
        
    def setoptimalinput(self,input):
        self.optimalinput = input
        
        
    def printInfo(self, depth = 0):
        tab = "    "
        print(tab*depth + "STATE {comps}".format(comps = self.components))
        print(tab*depth + "STATE COST: {sta}".format(sta = self.statecost))
        if self.optimalinput:
            print(tab*depth + "OPTIMAL INPUT:")
            self.optimalinput.printinfo(depth + 1)       
                                
class StateGrid(object):
    def __init__(self,period,gridstates,costfunc):
        self.grid = []
        self.makeGrid(period,gridstates,costfunc)
        
    def match(self,comps):
        for point in self.grid:
            if point.components == comps:
                return point
        return None
    
    def makeGrid(self,period,gridstates,costfunc):
        #clear to be safe
        self.grid = []
        for state in gridstates:
            self.grid.append(StateGridPoint(period,state,costfunc))
        
    def addGridPoint(self,point):
        self.grid.append(point)
        
    def getPoint(self,indices):
        a = self.grid
        for index in indices:
            a = a[index]
        return a
    
    def setPoint(self,indices,value):
        a = self.grid
        for index in indices:
            if index == indices[-1]:
                a[index] = value
            else:
                a = a[index]
            
    def interpolatepath(self,x,debug = False):
        #use inverse distance weighting interpolation
        if debug:
            print("****finding path cost value at {x} using inverse distance weighting interpolation".format(x = x))
        #power to which distance should be raised
        p = 4
        
        nsum = 0
        dsum = 0
        for point in self.grid:
            #if there is no optimal input, this may be an end state
            if not point.optimalinput:
                if debug:
                    print("there is no optimal input for this point")
                return 0
            
            #if the point falls directly on a grid point, just use that point's value
            if point.components == x:
                if debug:
                    print("****point falls on a grid point: {pnt}".format(pnt = point.components))
                return point.optimalinput.pathcost
            
            d = self.getdistance(x,point.components)
            w = d**-p
            dsum += w
            nsum += w*point.optimalinput.pathcost
            
            if debug:
                print("****contribution from {pnt}: \n        DISTANCE: {dist}, \n        WEIGHT: {weight}, \n        VALUE: {val}".format(pnt = point.components, dist = d, weight = w, val = point.optimalinput.pathcost))
        
        intval = nsum/dsum
        
        if debug:
            print("****FINISHED INTERPOLATING! interpolated value = {int}".format(int = intval ))
        
        return intval
    
    def interpolatestate(self,x,debug = False):
        #use inverse distance weighting interpolation
        if debug:
            print("****finding state cost value at {x} using inverse distance weighting interpolation".format(x = x))
        #power to which distance should be raised
        p = 4
        
        nsum = 0
        dsum = 0
        for point in self.grid:
            #if the point falls directly on a grid point, just use that point's value
            if point.components == x:
                if debug:
                    print("****point falls on a grid point: {pnt}".format(pnt = point.components))
                return point.statecost
            
            d = self.getdistance(x,point.components)
            w = d**-p
            dsum += w
            nsum += w*point.statecost
            
            if debug:
                print("****contribution from {pnt}: \n        DISTANCE: {dist}, \n        WEIGHT: {weight}, \n        VALUE: {val}".format(pnt = point.components, dist = d, weight = w, val = point.statecost))
        
        intval = nsum/dsum
        
        if debug:
            print("****FINISHED INTERPOLATING! interpolated value = {int}".format(int = intval ))
        
        return intval
            
    def getdistance(self,a,b):
        sumsq = 0
        for key in a:
            sumsq += (a[key] - b[key])**2
        return sumsq ** .5
                
    def printInfo(self,depth = 0):
        tab = "    "
        print(tab*depth + "STATE GRID has {n} grid points".format(n = len(self.grid)))
    
class InputSignal(object):
    def __init__(self,comps,gridconnected,drpart):
        self.gridconnected = gridconnected
        self.drevent = drpart
        self.components = comps
        self.transcost = None
        self.pathcost = None
    
    #sets cost of transition associated with input
    #returns old the old cost
    def setcost(self,cost):
        temp = self.transcost
        self.transcost = cost
        return temp
    
    def printInfo(self,depth = 0):
        tab = "    "
        print(tab*depth + "INPUT: {inp}".format(inp = self.components))
        if self.pathcost:
            print(tab*depth + "PATH COST: {cost}".format(cost = self.pathcost))

    
