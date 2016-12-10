import datetime
import random
import numpy as np
import csv

class Brewhouse:
    def __init__(self):
        self.turnspot = 1
        self.volume = 0

class Tank:
    def __init__(self, name, turns):
        self.name = name
        self.brews = 0
        self.maxbrews = turns
        self.brew = Brew()
        self.fermdays = 0
        self.finishdays = self.brew.fermtime if self.brew else 0
        self.totalBBLs = 0
        self.brand = self.brew.brand
        self.bYield = self.brew.bYield
        self.cYield = self.brew.cYield

    def filled(self):
        if self.brews == self.maxbrews:
            return True
        else:
            return False

    def dayTick(self):
        if self.brews == self.maxbrews:
            self.fermdays += 1

    def checkFinish(self):
        if self.fermdays >= self.finishdays:
            self.totalBBLs = self.totalBBLs + (self.brews * self.bYield * (self.cYield/100) * .94)
            self.brews = 0
            self.fermdays = 0
    
class Brew:
    def __init__(self):
            self.brandNum = random.randrange(1,1000)
            if self.brandNum < 600:
                self.brand = 'IPA'
            if self.brandNum >= 600:
                self.brand = 'SUM'
            if self.brandNum > 900:
                self.brand = 'BRO'
            
            if self.brand == 'IPA':
                self.fermtime = 10
            elif self.brand == 'SUM':
                self.fermtime = 9
            elif self.brand == 'BRO':
                self.fermtime = 12
            else:
                self.fermtime = 10

            if self.brand == 'IPA':
                self.bYield = np.random.normal(87.5, 1, 1)
                self.cYield = np.random.normal(86, 2, 1)
            elif self.brand == 'SUM':
                self.bYield = np.random.normal(88.5, 1, 1)
                self.cYield = np.random.normal(86, 2, 1)
            elif self.brand == 'BRO' or 'SIS':
                self.bYield = np.random.normal(75, 2, 1)
                self.cYield = np.random.normal(75, 2, 1)
            else:
                self.bYield = np.random.normal(85, 2, 1)
                self.cYield = np.random.normal(80, 2, 1)


def generate_tanks(count_240, count_90):
    tanks = []
    for i in range(count_240):
        tanks.append(Tank('(240)FV ' + str(i), 3))
    for i in range(count_90):
        tanks.append(Tank('(90)FV ' + str(i), 1))
    return tanks

def get_new_brew():
    newbrew = Brew()
    return newbrew

def simulation(start,end,tanks):

  endDate = end
  delta = datetime.timedelta(days=1)
  d = start
  weekend = set([5,6])
  turn = 1
  brewcheck = 0
  weekSums = []
  f = open('testCSV.csv', 'w+')
  writer = csv.writer(f)
  writer.writerow( ('Tank', 'Brand', 'Date', 'Turn Bucket') )

  def emptyTanks():
    emptyList = []
    for tank in tanks:
        if tank.filled() == False:
            emptyList.append(tank.name)
    return emptyList        
    emptyList = []

  while d <= end:

    for tank in tanks:
        
        emptyList = emptyTanks()
        
        while tank.filled() == False and d.weekday() not in weekend and turn < 4:
            tank.brews += 1
            if tank.brews == 1:
                """ here would be where I should randomize brew at each fill.  What is below isn't working though... """
                tank.brew = get_new_brew()
                print "Tank ", tank.name, " filled with ", tank.brand
            writer.writerow( (tank.name, tank.brand, d.strftime("%a %Y-%m-%d"), turn) )
            turn += 1
        
        if len(emptyList) == 0 or d.weekday() in weekend:
            turn += 1
            if turn < 4:
                writer.writerow( ("EMPTY", "NULL", d.strftime("%a %Y-%m-%d"), turn) )
        
        if turn > 3:
            turn = 1
            d += delta
            for tank in tanks:
                tank.dayTick()
                tank.checkFinish()
        
            if d.weekday() == 6:
                l = []
                for tank in tanks:
                    l.append(tank.totalBBLs)
                bblSum = sum(l)
                if bblSum > 0:
                    weekSums.append(bblSum) 
                #print "total BBLs at end of week: ", bblSum 
                #print weekSums
                weekTots = [t - s for s, t in zip(weekSums, weekSums[1:])]
                #print weekTots

  #print weekSums
  print "Average Weekly Simulated BBLs: ", round(sum(weekTots)/len(weekTots), 2)
  #print "total bbls for period:  ", bblSum
  f.close()

#RUN SIMULATION!!
start = datetime.datetime.strptime('2016-1-1', '%Y-%m-%d')
end = datetime.datetime.strptime('2016-4-1', '%Y-%m-%d')
  

for i in range(5):

    tanks = generate_tanks(5,7)
 

#    FV1  = Tank('FV101',3,Brew())
#    FV2  = Tank('FV102',3,Brew())
#    FV3  = Tank('FV103',1,Brew())
#    FV4  = Tank('FV104',3,Brew())
#    FV5  = Tank('FV105',0,Brew())
#    FV6  = Tank('FV201',1,Brew())
#    FV7  = Tank('FV202',1,Brew())
#    FV8  = Tank('FV203',3,Brew())
#    FV9  = Tank('FV204',1,Brew())
#    FV10 = Tank('FV205',1,Brew())
#    FV11 = Tank('FV206',1,Brew())
#    FV12 = Tank('FV207',1,Brew())
#    FV13 = Tank('FV208',1,Brew())
#    FV14 = Tank('FV209',1,Brew())

#    tanks = [FV1, FV2, FV3, FV4, FV5, FV6, FV7, FV8, FV9, FV10, FV11, FV12, FV13, FV14]

    simulation(start,end,tanks)



