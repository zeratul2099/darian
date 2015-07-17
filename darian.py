from datetime import datetime
import time
from math import floor
import argparse




class MartianDate(object):
    
    SECONDS_A_DAY = 86400.0
    E_DAYS_TIL_UNIX = 719527.0
    EPOCH_OFFSET  = 587744.77817
    MARS_TO_EARTH_DAYS = 1.027491251

    SOL_NAMES = {
        'areosynchronous': ['Heliosol', 'Phobosol', 'Deimosol', 'Terrasol', 'Venusol', 'Mercurisol', 'Jovisol'],
        'defrost': ['Axatisol', 'Benasol', 'Ciposol', 'Domesol', 'Erjasol', 'Fulisol', 'Gavisol'],
        'martiana': ['Sol Solis', 'Sol Lunae', 'Sol Martis', 'Sol Mercurii', 'Sol Jovis', 'Sol Veneris', 'Sol Saturni']
    }
    MONTH_NAMES = {
        'defrost': ['Adir', 'Bora', 'Coan', 'Deti', 'Edal', 'Flo', 'Geor', 'Heliba', 'Idanon', 'Jowani', 'Kireal', 'Larno', 'Medior', 'Neturima', 'Ozulikan', 'Pasurabi', 'Rudiakel', 'Safundo', 'Tiunor', 'Ulasja', 'Vadeun', 'Wakumi', 'Xetual', 'Zungo'],
        'hensel': ['Vernalis', 'Duvernalis', 'Trivernalis', 'Quadrivernalis', 'Pentavernalis', 'Hexavernalis', 'Aestas', 'Duestas', 'Triestas', 'Quadrestas', 'Pentestas', 'Hexestas', 'Autumnus', 'Duautumn', 'Triautumn', 'Quadrautumn', 'Pentautumn', 'Hexautumn', 'Unember', 'Duember', 'Triember', 'Quadrember', 'Pentember', 'Hexember'],
        'martiana': ['Sagittarius', 'Dhanus', 'Capricornus', 'Makara', 'Aquarius', 'Kumbha', 'Pisces', 'Mina', 'Aries', 'Mesha', 'Taurus', 'Rishabha', 'Gemini', 'Mithuna', 'Cancer', 'Karka', 'Leo', 'Simha', 'Virgo', 'Kanya', 'Libra', 'Tula', 'Scorpius', 'Vrishika']
    }

    total_sols = None
    year = None
    sol_of_year = None
    season = None
    sol_of_season = None
    month_of_season = None
    month = None
    sol = None
    week_sol = None
    hour = None
    min = None
    sec = None
    type = None
    
    def __init__(self, total_sols, dtype='martiana'):
        assert(dtype in list(self.SOL_NAMES.keys()) + list(self.MONTH_NAMES.keys()) + ['aqua'])
        self.type = dtype
        self.total_sols = total_sols
        self.init_time()
        self.year_and_sol_of_year()
        self.set_season_by_sol_of_year()
        
        self.sol_of_season = self.sol_of_year - 167 * self.season
        self.month_of_season = floor(self.sol_of_season / 28) #  0-5
        self.month = int(self.month_of_season + (6 * self.season) + 1) # 1-24
        self.sol = int(self.sol_of_year - (((self.month - 1) * 28) - self.season) + 1) # 1-28
        self.week_sol = int(((self.sol - 1) % 7) + 1) # 1-7
        
        self.set_week_sol_name_by_week_sol_and_type()
        self.set_month_name_by_month_and_type()

    def init_time(self):
        partial_sol = self.total_sols - floor(self.total_sols)
        hour = partial_sol * 24
        min  = (hour - floor(hour)) * 60

        self.hour = floor(hour)
        self.min  = floor(min)
        self.sec  = floor((min - floor(min)) * 60)

    def __str__(self):
        return '%s, %s. %s %s, %02d:%02d:%02d' % (
            self.week_sol_name,
            self.sol,
            self.month_name,
            self.year,
            self.hour,
            self.min,
            self.sec
            )
            
    @classmethod
    def by_datetime(cls, earth_dt, dtype='martiana'):
        #seconds = earth_dt.timestamp()
        seconds = time.mktime(earth_dt.timetuple())
        days = ((seconds / cls.SECONDS_A_DAY) + cls.E_DAYS_TIL_UNIX)
        sols = (days - cls.EPOCH_OFFSET) / cls.MARS_TO_EARTH_DAYS
        return cls(sols, dtype)
        

    def year_and_sol_of_year(self):
        sD  = floor(self.total_sols / 334296)
        doD = floor(self.total_sols - (sD * 334296))
        sC = 0
        doC = doD
        if doD != 0:
            sC = floor((doD - 1) / 66859)
        if sC != 0:
            doC -= ((sC * 66859) + 1)

        sX = 0
        doX = doC
        if sC != 0: # century that does not begin with leap day
            sX = floor((doC + 1) / 6686)
            if sX != 0:
                doX -= ((sX * 6686) - 1)
        else:
            sX = floor(doC / 6686)
            if sX != 0:
                doX -= (sX * 6686)

        sII = 0
        doII = doX
        if (sC != 0) and (sX == 0): # decade that does not begin with leap day
            sII = floor(doX / 1337)
            if sII != 0:
                doII -= (sII * 1337)
        else: # 1338, 1337, 1337, 1337 ...
            if doX != 0:
                sII = floor((doX - 1) / 1337)
            if sII != 0:
                doII -= ((sII * 1337) + 1)


        sI = 0
        doI = doII
        if (sII == 0) and ((sX != 0) or ((sX == 0) and (sC == 0))):
            sI = floor(doII / 669)
            if sI != 0:
                doI -= 669
        else: # 668, 669
            sI = floor((doII + 1) / 669)
            if sI != 0:
                doI -= 668
                
        self.year = int((500 * sD) + (100 * sC) + (10 * sX) + (2 * sII) + sI)
        self.sol_of_year = int(doI)
        
    def set_season_by_sol_of_year(self):
        if self.sol_of_year < 167: self.season = 0
        elif self.sol_of_year < 334: self.season = 1
        elif self.sol_of_year < 501: self.season = 2
        else: self.season = 3
        
    def set_week_sol_name_by_week_sol_and_type(self):
        if self.type in ['martiana', 'defrost', 'areosynchronous']:
            self.week_sol_name = self.SOL_NAMES[self.type][self.week_sol-1]
        elif self.type == 'hensel':
            self.week_sol_name = self.SOL_NAMES['martiana'][self.week_sol-1]
        elif self.type == 'aqua':
            self.week_sol_name = str(self.week_sol)

    def set_month_name_by_month_and_type(self):
        if self.type in ['martiana', 'defrost', 'hensel']:
            self.month_name = self.MONTH_NAMES[self.type][self.month-1]
        elif self.type == 'areosynchronous':
            self.month_name = self.MONTH_NAMES['defrost'][self.month-1]
        elif self.type == 'aqua':
            self.month_name = str(self.month)
        month_name = self.MONTH_NAMES.get(self.type, range(24))[self.month-1]





if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--date', type=str, help='datetime as YYYYMMDDHHMMSS', default=None)
    args = parser.parse_args()
    if args.date:
        dt = datetime.strptime(args.date, '%Y%m%d%H%M%S')
    else:
        dt = datetime.now()
    md = MartianDate.by_datetime(dt)
    print(dt)
    print(md)
