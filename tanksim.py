import datetime
import random
import csv


class Tank:
    def __init__(self, name, turns):
        self.name = name
        self.num_brews_in_tank = 0
        self.maxnum_brews_in_tank = turns
        # The type of brew in the tank
        self.brand = Brand()
        # Counter for days of fermentation -- only increments when tank is filled
        self.ferm_days = 0
        # Total barrels produced from one fill of the tank 
        self.total_bbls = 0

    def is_filled(self):
        return self.num_brews_in_tank >= self.maxnum_brews_in_tank

    def day_tick(self):
        """When tank is full, increment ferm_days by 1"""
        if self.is_filled():
            self.ferm_days += 1

        self.reset_tank_if_complete()

    def add_turn(self):
        self.num_brews_in_tank += 1
        
    def get_volume(self):
        """Factor in brew yield, cellar yield, packaging yield per each brew in tank"""
        return (self.num_brews_in_tank * self.brand.brew_yield * 
                (self.brand.cellar_yield/100) * (self.brand.packaging_yield/100))

    def reset_tank_if_complete(self):
        if self.ferm_days >= self.brand.ferm_time:
            self.total_bbls = self.total_bbls + self.get_volume() 
            self.num_brews_in_tank = 0
            self.ferm_days = 0
            self.brand = Brand()

    def num_turns_left_in_tank(self):
        return self.maxnum_brews_in_tank - self.num_brews_in_tank

class Brand:
    def __init__(self):
        brands = {
            "IPA": {
                "brand" : "IPA",
                "ferm_time": 10,
                "brew_yield": random.normalvariate(87.5, 1),
                "cellar_yield": random.normalvariate(86, 2),
            },
            "SUM": {
                "brand" : "SUM",
                "ferm_time": 9, 
                "brew_yield": random.normalvariate(88.5, 1),
                "cellar_yield": random.normalvariate(86, 2),
            },
            "BRO": {
                "brand" : "BRO",
                "ferm_time": 12, 
                "brew_yield": random.normalvariate(75, 2),
                "cellar_yield": random.normalvariate(75, 2),
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

        self.name = brand['brand']
        self.ferm_time = brand['ferm_time']
        self.brew_yield = brand['brew_yield']
        self.cellar_yield = brand['cellar_yield']
        self.packaging_yield = random.normalvariate(94, 2)

def daterange(start_date, end_date):
    """Iterate through dates between start and end"""
    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)

def generate_tanks(count_240, count_90):
    """Given numbers of 240 barrel (3 turn) and 90 barrel (1 turn) tanks, generate em"""
    return ([Tank('(240)FV ' + str(i), 3) for i in range(count_240)] + 
            [Tank('(90)FV ' + str(i), 1) for i in range(count_90)])

def get_first_unfilled_tank(tanks, turns_per_day, turn):
    for tank in tanks:
        if not tank.is_filled():
            if tank.num_turns_left_in_tank() <= turns_per_day - turn:
                return tank

    return None

def simulation(start_date, end_date, tanks, turns_per_day, days_off):
    # aggregates
    week_sums = []

    f = open('testCSV.csv', 'w+')
    writer = csv.writer(f)
    writer.writerow( ('Tank', 'Brand', 'Date', 'Turn Bucket') )

    # for each day
    for day in daterange(start_date, end_date):

        # tick the day on each tank based on what was there at the start of
        # the day. this will empty the tank if it is complete and set a new
        # brand for the tank.
        for tank in tanks:
            tank.day_tick()

        # if sunday, aggregate some data for the week
        if day.weekday() == 6:
            bbl_sum = sum([tank.total_bbls for tank in tanks])
            week_sums.append(bbl_sum) 
            #print "total BBLs at end of week: ", bbl_sum 
            #print week_sums

        # for each brewhouse turn
        for turn in range(turns_per_day):

            # find the first tank that is not filled 
            first_unfilled_tank = get_first_unfilled_tank(tanks, turns_per_day, turn)

            # if there is one, and it is a legit day to be filling tanks,
            if (first_unfilled_tank and day.weekday() not in days_off):
                # put this turn into that tank
                first_unfilled_tank.add_turn()

                writer.writerow( (first_unfilled_tank.name, first_unfilled_tank.brand.name, day, turn+1) )

            if day.weekday() in days_off:
                writer.writerow( ('NULL', 'Day Off', day, turn+1) )

            if first_unfilled_tank == None and day.weekday() not in days_off:
                writer.writerow( ('NULL', 'No Tank', day, turn+1) )
                
        week_totals = [t - s for s, t in zip(week_sums, week_sums[1:])]

    #print week_sums
    print "Average Weekly Simulated BBLs: ", round(sum(week_totals)/len(week_totals), 2)
    #print "total bbls for period:  ", bbl_sum
    f.close()

# RUN SIMULATION!!
if __name__ == '__main__':
    start_date = datetime.date(2016, 1, 1)
    end_date = datetime.date(2016, 2, 1)
    turns_per_day = 4
    days_off = set([5, 6])

    for i in range(5):
        tanks = generate_tanks(5, 7) 
        simulation(start_date, end_date, tanks, turns_per_day, days_off)

    # add user inputs: max turns per day, brewdays per week, holidays/planned downtime, 
    # random unplanned downtime, yield entry, split tanks overnight boolean, ...