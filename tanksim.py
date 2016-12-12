import datetime
import random
import numpy as np
import csv


class Tank:
    def __init__(self, name, turns):
        self.name = name
        self.brews = 0 #
        self.maxbrews = turns
        self.brew = Brew()
        self.fermdays = 0
        self.finishdays = self.brew.fermtime if self.brew else 0
        self.totalBBLs = 0
        self.brand = self.brew.brand
        self.bYield = self.brew.bYield
        self.cYield = self.brew.cYield
        self.pYield = self.brew.pYield

    def filled(self):
        if self.brews == self.maxbrews:
            return True
        else:
            return False
    
    def updateFill(self):
        self.brew = Brew()
        self.finishdays = self.brew.fermtime if self.brew else 0
        self.brand = self.brew.brand
        self.bYield = self.brew.bYield
        self.cYield = self.brew.cYield
        self.pYield = self.brew.pYield


    def dayTick(self):
        if self.brews == self.maxbrews:
            self.fermdays += 1

    def checkFinish(self):
        if self.fermdays >= self.finishdays:
            self.totalBBLs = self.totalBBLs + (self.brews * self.bYield * (self.cYield/100) * (self.pYield/100))
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

            self.pYield = np.random.normal(94, 2, 1)


def generate_tanks(count_240, count_90):
    tanks = []
    for i in range(count_240):
        tanks.append(Tank('(240)FV ' + str(i), 3))
    for i in range(count_90):
        tanks.append(Tank('(90)FV ' + str(i), 1))
    return tanks

def emptyTanks():
    emptyList = []
    for tank in tanks:
        if tank.filled() == False:
            emptyList.append(tank.name)
    return emptyList        
    emptyList = []

def simulation(start,end,tanks,maxturns):

  d = start
  endDate = end
  delta = datetime.timedelta(days=1)
  weekend = set([5,6])
  turn = 1
  weekSums = []
  

  f = open('testCSV.csv', 'w+')
  writer = csv.writer(f)
  writer.writerow( ('Tank', 'Brand', 'Date', 'Turn Bucket') )


  while d <= end:

    for tank in tanks:
        
        emptyList = emptyTanks()
        
        while tank.filled() == False and d.weekday() not in weekend and turn <= maxturns:
            tank.brews += 1
            if tank.brews == 1:
                # fill tank with random brew
                tank.updateFill()
                #print "Tank ", tank.name, " filled with ", tank.brand, tank.finishdays
            writer.writerow( (tank.name, tank.brand, d.strftime("%a %Y-%m-%d"), turn) )
            turn += 1
        
        if len(emptyList) == 0 or d.weekday() in weekend:
            if turn <= maxturns:
                writer.writerow( ("EMPTY", "NULL", d.strftime("%a %Y-%m-%d"), turn) )
            turn += 1
        
        if turn > maxturns:
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
tanks = generate_tanks(5,7) 
maxturns = 3

for i in range(5):

    simulation(start,end,tanks,maxturns)

# add user inputs: max turns per day, brewdays per week, holidays/planned downtime, 
# random unplanned downtime, yield entry, split tanks overnight boolean, ...



