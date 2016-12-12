import datetime
import random
import numpy as np
import csv


class Tank:
    def __init__(self, name, turns):
        self.name = name
        self.num_brews_in_tank = 0
        self.maxnum_brews_in_tank = turns
        # The type of brew in the tank
        self.brand = None
        # Counter for days of fermentation -- only increments when tank is filled
        self.fermdays = 0
        # Total barrels produced from one fill of the tank 
        self.totalBBLs = 0

    def is_filled(self):
        return self.num_brews_in_tank == self.maxnum_brews_in_tank
    
    def update_fill(self):
        """Set a new brand for the tank"""
        self.brand = Brand()

    def day_tick(self):
        """When tank is full, increment fermdays by 1"""
        if self.is_filled():
            self.fermdays += 1
    
    def get_volume(self):
        """Factor in brew yield, cellar yield, packaging yield per each brew in tank"""
        return self.num_brews_in_tank * self.brand.bYield * (self.brand.cYield/100) * (self.brand.pYield/100)

    def reset_tank_if_complete(self):
        if self.brand and self.fermdays >= self.brand.fermtime:
            self.totalBBLs = self.totalBBLs + self.get_volume() 
            self.num_brews_in_tank = 0
            self.fermdays = 0

class Brand:
    def __init__(self):
        brands = {
            "IPA": {
                "fermtime": 10,
                "bYield": np.random.normal(87.5, 1, 1),
                "cYield": np.random.normal(86, 2, 1),
            },
            "SUM": {
                "fermtime": 9, 
                "bYield": np.random.normal(88.5, 1, 1),
                "cYield": np.random.normal(86, 2, 1),
            },
            "BRO": {
                "fermtime": 12, 
                "bYield": np.random.normal(75, 2, 1),
                "cYield": np.random.normal(75, 2, 1),
            },
        }

        # Set up name, fermtime, bYield, cYield, pYield
        num = random.randrange(1,1000)

        if num < 600:
            brand = brands['IPA']
        if num >= 600:
            brand = brands['SUM'] 
        if num > 900:
            brand = brands['BRO']

        self.fermtime = brand['fermtime']
        self.bYield = brand['bYield']
        self.cYield = brand['cYield']
        self.pYield = np.random.normal(94, 2, 1)

def generate_tanks(count_240, count_90):
    """Given numbers of 240 barrel (3 turn) and 90 barrel (1 turn) tanks, generate em"""
    tanks = []
    for i in range(count_240):
        tanks.append(Tank('(240)FV ' + str(i), 3))
    for i in range(count_90):
        tanks.append(Tank('(90)FV ' + str(i), 1))
    return tanks


def emptyTanks():
    return [tank.name for tank in tanks if not tank.is_filled()]

def simulation(start,end,tanks,maxturns,daysoff):

  d = start
  delta = datetime.timedelta(days=1)
  # first turn -- a turn is a brewhouse unit of work. brewhouses can do some max
  # num of these per day.
  turn = 1

  weekSums = []
  

  f = open('testCSV.csv', 'w+')
  writer = csv.writer(f)
  writer.writerow( ('Tank', 'Brand', 'Date', 'Turn Bucket') )


  while d <= end:

    for tank in tanks:
        
        emptyList = emptyTanks()

        while tank.is_filled() == False and d.weekday() not in daysoff and turn <= maxturns:
            tank.num_brews_in_tank += 1
            if tank.num_brews_in_tank == 1:
                # fill tank with random brand
                tank.update_fill()
                #print "Tank ", tank.name, " filled with ", tank.brand, tank.brand.fermtime

            writer.writerow( (tank.name, tank.brand, d.strftime("%a %Y-%m-%d"), turn) )
            turn += 1
        
        # to prevent loop getting stuck on daysoff
        if len(emptyList) == 0 or d.weekday() in daysoff:
            if turn <= maxturns:
                writer.writerow( ("EMPTY", "NULL", d.strftime("%a %Y-%m-%d"), turn) )
            turn += 1

        # ... 
        if turn > 3:
            turn = 1
            d += delta
            for tank in tanks:
                tank.day_tick()
                tank.reset_tank_if_complete()
        
            # Sunday
            if d.weekday() == 6:
                bblSum = sum([tank.totalBBLs for tank in tanks])
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
daysoff = set([5,6])

for i in range(5):

    simulation(start,end,tanks,maxturns,daysoff)

# add user inputs: max turns per day, brewdays per week, holidays/planned downtime, 
# random unplanned downtime, yield entry, split tanks overnight boolean, ...


