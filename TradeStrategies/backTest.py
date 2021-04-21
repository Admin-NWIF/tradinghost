from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas_ta as ta

from backtesting.test import SMA, GOOG
from dporsiDiv import DPORSIDiv


# class SmaCross(Strategy):
#     def init(self):
#         price = self.data.Close
#         self.ma1 = self.I(SMA, price, 10)
#         self.ma2 = self.I(SMA, price, 20)

#     def next(self):
#         if crossover(self.ma1, self.ma2):
#             self.buy()
#         elif crossover(self.ma2, self.ma1):
#             self.sell()


# bt = Backtest(GOOG, SmaCross, commission=.002,
#               exclusive_orders=True)
# stats = bt.run()
# bt.plot()
# print(stats)

class DivStrategy(Strategy):
    def init(self):
        print(self.data.df)
        print(type(self.data.df))

    def next(self):
        # Insert custom strategy class and populate indicators
        if len(self.data.df.Close) <= 20:
            pass
        else:
            dpoRsiDivStrategy = DPORSIDiv(self.data.df)
            dpoRsiDivStrategy.populateDPO()
            dpoRsiDivStrategy.populateRSI()
            dpoRsiDivStrategy.populateHighsAndLows()

            # Generate long or short entry signal
            longEntry = dpoRsiDivStrategy.detectLongEntrySignal()
            shortEntry = dpoRsiDivStrategy.detectShortEntrySignal()

            if longEntry:
                self.buy()
            elif shortEntry:
                self.sell()
            
            print("currentRow: ", len(self.data.df.Close))

