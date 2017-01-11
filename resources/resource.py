from DCMGClasses.resources.math import interpolation
from DCMGClasses.CIP import wrapper

class Resource(object):
    
    def __init__(self,owner,location,name,capCost,**kwargs):
        self.owner = owner
        self.location = location
        self.capCost = capCost
        self.name = name
        
    def setOwner(self,newOwner):
        print("transferring ownership of {resource} from {owner} to {newowner}".format(resource = self, owner = self.owner, newowner = newOwner))
        self.owner = newOwner
        
    def printInfo(self):
        print("RESOURCE: {name} owned by {owner}\n    TYPE:{type}\n    LOCATION:{loc}".format(name = self.name, owner = self.owner, type = self.__class__.__name__, loc = self.location))

class Source(Resource):
    def __init__(self,owner,location,name,capCost,maxDischargePower,dischargeChannel,**kwargs):
        super(Source,self).__init__(owner,location,name,capCost)
        self.maxDischargePower = maxDischargePower
        self.dischargeChannel = dischargeChannel
        
        self.availDischargePower = 0
        
        
        DischargeChannel = Channel(dischargeChannel)
        
        
    def getInputUnregVoltage(self):
        voltage = self.DischargeChannel.getUnregV()
        return voltage
    
    def getOutputRegVoltage(self):
        voltage = self.DischargeChannel.getRegV()
        return voltage
        
    def getInputUnregCurrent(self):
        current = self.DischargeChannel.getUnregI()
        return current
        
    def getOutputUnregCurrent(self):
        current = self.DischargeChannel.getRegI()
        return current
    
    def connectSource(self,mode,setpoint):
        pass
    
    def disconnectSource(self):
        pass
    

class Storage(Source):
    
    def __init__(self,owner,location,name,capCost,maxDischargePower,maxChargePower,capacity,chargeChannel,dischargeChannel,**kwargs):
        super(Storage,self).__init__(owner,location,name,capCost,maxDischargePower,dischargeChannel,**kwargs)
        self.chargePower = maxChargePower
        self.capacity = capacity
        self.chargeChannel = chargeChannel
        
        
        self.SOC = 0
        self.energy = 0
        
        ChargeChannel = Channel(chargeChannel)
        
            
    def charge(self,setpoint):
        pass
    
class LeadAcidBattery(Storage):
    SOCtable = [(0, 11.8),(.25, 12.0),(.5, 12.2),(.75, 12.4),(1, 12.7)]
    def __init__(self,owner,location,name,capCost,maxDischargePower,maxChargePower,capacity,chargeChannel,dischargeChannel,**kwargs):
        super(LeadAcidBattery,self).__init__(owner,location,name,capCost,maxDischargePower,maxChargePower,capacity,chargeChannel,dischargeChannel,**kwargs)
        self.SOC = self.getSOCfromOCV()
        
        self.cyclelife = 1000
        
    def getSOC(self):
        #get SOC from PLC
        pass
    
    def getSOCfromOCV(self):
        #get battery voltage from PLC
        tagname = "SOURCE_{num}_REG_VOLTAGE".format(num = self.DischargeChannel.channelNumber)
        voltage = getTagValue(tagName)
        soc = interpolation.lininterp(self.SOCtable,voltage)
        return soc
    
        
class SolarPanel(Source):
    def __init__(self,owner,location,name,capCost,maxDischargePower,dischargeChannel,Voc,Vmpp,**kwargs):
        super(SolarPanel,self).__init__(owner,location,name,capCost,maxDischargePower,dischargeChannel,**kwargs)
        self.Voc = Voc
        self.Vmpp = Vmpp
        
        self.amortizationPeriod = 1000
        
    def powerAvailable(self):
        pass
        
    
class Channel():
    def __init__(self,channelNumber):
        self.channelNumber = channelNumber
        
    def getRegV(self):
        tagName = "SOURCE_{d}_REG_VOLTAGE".format(d = self.channelNumber)     
        #call to CIP wrapper
        value = getTagValue(tagName)
        return value   
        
    def getUnregV(self):
        tagName = "SOURCE_{d}_UNREG_VOLTAGE".format(d = self.channelNumber)
        value = getTagValue(tagName)
        return value
    
    def getRegI(self):
        tagName = "SOURCE_{d}_REG_CURRENT".format(d = self.channelNumber)
        value = getTagValue(tagName)
        return value
    
    def getUnregI(self):
        tagName = "SOURCE_{d}_UNREG_CURRENT".format(d = self.channelNumber)
        value = getTagValue(tagName)
        return value
    
def addResource(strlist,classlist,debug = False):
    def addOne(item,classlist):
        if type(item) is dict:
            resType = item.get("type",None)
            if resType == "solar":
                res = SolarPanel(**item)
            elif resType == "lead_acid_battery":
                res = LeadAcidBattery(**item)
            else:
                pass
            classlist.append(res)
        
    if type(strlist) is list:
        if len(strlist) > 1:
            if debug:
                print("list contains multiple resources")
            for item in strlist:
                if debug:
                    print("working on new element")
                addOne(item,classlist)                
        if len(strlist) == 1:
            if debug:
                print("list contains one resource")
            addOne(strlist[0],classlist)
    elif type(strlist) is dict:
        if debug:
            print("no list, just a single dict")
        addOne(strlist,classlist)
    if debug:
        print("here's how the classlist looks now: {cl}".format(cl = classlist))
        
        
        