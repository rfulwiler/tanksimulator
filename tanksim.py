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
        self.ferm_days = 0
        # Total barrels produced from one fill of the tank 
        self.total_bbls = 0

    def is_filled(self):
        return self.num_brews_in_tank == self.maxnum_brews_in_tank
    
    def update_fill(self):
        """Set a new brand for the tank"""
        self.brand = Brand()

    def day_tick(self):
        """When tank is full, increment ferm_days by 1"""
        if self.is_filled():
            self.ferm_days += 1
    
    def get_volume(self):
        """Factor in brew yield, cellar yield, packaging yield per each brew in tank"""
        return (self.num_brews_in_tank * self.brand.brew_yield * 
                (self.brand.cellar_yield/100) * (self.brand.packaging_yield/100))

    def reset_tank_if_complete(self):
        if self.brand and self.ferm_days >= self.brand.ferm_time:
            self.total_bbls = self.total_bbls + self.get_volume() 
            self.num_brews_in_tank = 0
            self.ferm_days = 0

class Brand:
    def __init__(self):
        brands = {
            "IPA": {
                "ferm_time": 10,
                "brew_yield": np.random.normal(87.5, 1, 1),
                "cellar_yield": np.random.normal(86, 2, 1),
            },
            "SUM": {
                "ferm_time": 9, 
                "brew_yield": np.random.normal(88.5, 1, 1),
                "cellar_yield": np.random.normal(86, 2, 1),
            },
            "BRO": {
                "ferm_time": 12, 
                "brew_yield": np.random.normal(75, 2, 1),
                "cellar_yield": np.random.normal(75, 2, 1),
            },
        }

        # Set up name, ferm_time, brew_yield, cellar_yield, packaging_yield
        num = random.randrange(1,1000)

        if num < 600:
            brand = brands['IPA']
        if num >= 600:
            brand = brands['SUM'] 
        if num > 900:
            brand = brands['BRO']

        self.ferm_time = brand['ferm_time']
        self.brew_yield = brand['brew_yield']
        self.cellar_yield = brand['cellar_yield']
        self.packaging_yield = np.random.normal(94, 2, 1)

def generate_tanks(count_240, count_90):
    """Given numbers of 240 barrel (3 turn) and 90 barrel (1 turn) tanks, generate em"""
    return ([Tank('(240)FV ' + str(i), 3) for i in range(count_240)] + 
            [Tank('(90)FV ' + str(i), 1) for i in range(count_90)])

def simulation(start,end,tanks,maxturns,daysoff):
    d = start
    delta = datetime.timedelta(days=1)
    # first turn -- a turn is a brewhouse unit of work. brewhouses can do some max
    # num of these per day.
    turn = 1
    week_sums = []

    f = open('testCSV.csv', 'w+')
    writer = csv.writer(f)
    writer.writerow( ('Tank', 'Brand', 'Date', 'Turn Bucket') )

    # for each day
    while d <= end:

        # for each tank
        for tank in tanks:
            
            # if a weekday, and tank is not filled, and the turn count is not more than maxturns,
            # increment the brews in the tank and the turn until tank is filled or turn is greater
            # than maxturns
            while tank.is_filled() == False and d.weekday() not in daysoff and turn <= maxturns:
                tank.num_brews_in_tank += 1
                if tank.num_brews_in_tank == 1:
                    # fill tank with random brand
                    tank.update_fill()
                    #print "Tank ", tank.name, " filled with ", tank.brand, tank.brand.ferm_time

                writer.writerow( (tank.name, tank.brand, d.strftime("%a %Y-%m-%d"), turn) )
                turn += 1
            
            # to prevent loop getting stuck on daysoff:
            # if all the tanks are full or it is the weekend, increment the turn.
            if all([tank.is_filled() for tank in tanks]) or d.weekday() in daysoff:
                if turn <= maxturns:
                    writer.writerow( ("EMPTY", "NULL", d.strftime("%a %Y-%m-%d"), turn) )
                turn += 1

            # if we have exceeded maxturns, reset the turn count, increment the day,
            # then for each tank go through and increment its ferm_days if applicable
            # and reset the tank if applicable
            if turn > maxturns:
                turn = 1
                d += delta
                for tank in tanks:
                    tank.day_tick()
                    tank.reset_tank_if_complete()
            
                # if sunday, more like sum-day!, aggregate some data that is
                # reported at the end
                if d.weekday() == 6:
                    bbl_sum = sum([tank.total_bbls for tank in tanks])
                    week_sums.append(bbl_sum) 
                    #print "total BBLs at end of week: ", bbl_sum 
                    #print week_sums

    week_totals = [t - s for s, t in zip(week_sums, week_sums[1:])]
    #print week_sums
    print "Average Weekly Simulated BBLs: ", round(sum(week_totals)/len(week_totals), 2)
    #print "total bbls for period:  ", bbl_sum
    f.close()

# RUN SIMULATION!!
if __name__ == '__main__':
    start = datetime.datetime.strptime('2016-1-1', '%Y-%m-%d')
    end = datetime.datetime.strptime('2016-4-1', '%Y-%m-%d')
    tanks = generate_tanks(5,7) 
    maxturns = 3
    daysoff = set([5,6])

    for i in range(5):
        simulation(start,end,tanks,maxturns,daysoff)

    # add user inputs: max turns per day, brewdays per week, holidays/planned downtime, 
    # random unplanned downtime, yield entry, split tanks overnight boolean, ...
