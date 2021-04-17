import pandas as pd
import numpy as np
import pandas_ta as ta
from utils import Utils

class DPORSIDiv(object):
    def __init__(self, priceData):
        self.priceData = priceData
        self.dpoData = {
            "Value": [],
            "Date": []
        }
        self.rsiData = {
            "RSI": [],
            "Date": []
        }

        self.pivotData = {
            "pivotHigh": [],
            "pivotLow": [],
            "TAPivotHigh": [],
            "TAPivotLow": []
        }

        self.bullishDivPivots = {
            "pricePivotHighs": [],
            "TAPivotLows": []
        }

        self.bearishDivPivots = {
            "pricePivotLows": [],
            "TAPivotHighs": []
        }

        self.pivotDataFrame = None
        self.dpoDataFrame = None
        self.rsiDataFrame = None
        self.minutesBack = 3

        self.pricePivotHighAndTAPivotLow = None
        self.pricePivotLowAndTAPivotHigh = None
        self.util = Utils()

    def populateDPO(self):
        dpo = ta.dpo(self.priceData.Close, length=20, centered=False, offset=None)
        for idx, val in enumerate(dpo):
            self.dpoData["Value"].append(val)
            self.dpoData["Date"].append(self.priceData.Date[idx])
        self.dpoDataFrame = pd.DataFrame(self.dpoData, columns = ["Value", "Date"])

    def populateRSI(self):
        rsi = ta.rsi(self.priceData.Close, 14)
        for idx, val in enumerate(rsi):
            self.rsiData["RSI"].append(val)
            self.rsiData["Date"].append(self.priceData.Date[idx])
        self.rsiDataFrame = pd.DataFrame(self.rsiData, columns = ["RSI", "Date"])
    
    def populateHighsAndLows(self):
        for idx in range(len(self.priceData.Close)):
            self.pivotData["pivotHigh"].append(self.util.pivotHigh(self.priceData, self.priceData.High, idx, 3, 1))
            self.pivotData["pivotLow"].append(self.util.pivotLow(self.priceData, self.priceData.Low, idx, 3, 1))
            self.pivotData["TAPivotHigh"].append(self.util.pivotHigh(self.dpoDataFrame, self.dpoDataFrame.Value, idx, 3, 1))
            self.pivotData["TAPivotLow"].append(self.util.pivotLow(self.dpoDataFrame, self.dpoDataFrame.Value, idx, 3, 1))
        self.pivotDataFrame = pd.DataFrame(self.pivotData, columns = ["pivotHigh", "pivotLow", "TAPivotHigh", "TAPivotLow"])
        self.pricePivotHighAndTAPivotLow = self.util.findPricePivotHighAndTAPivotLow(self.pivotDataFrame.pivotHigh, self.pivotDataFrame.TAPivotLow, self.minutesBack)
        self.pricePivotLowAndTAPivotHigh = self.util.findPricePivotLowAndTAPivotHigh(self.pivotDataFrame.pivotLow, self.pivotDataFrame.TAPivotHigh, self.minutesBack)
    
    def detectLongEntrySignal(self):
        tradeSignal = [False, None]
        if self.pricePivotHighAndTAPivotLow[0]:
            pivotHigh = self.pricePivotHighAndTAPivotLow[1]
            TAPivotLow = self.pricePivotHighAndTAPivotLow[2]
            self.bullishDivPivots["pricePivotHighs"].append(pivotHigh)
            self.bullishDivPivots["TAPivotLows"].append(TAPivotLow)

            length = len(self.pivotDataFrame.pivotHigh)-1
            for idx in range(length-self.minutesBack, 0, -1):
                currentValue = self.pivotDataFrame.pivotHigh[idx]
                if len(self.bullishDivPivots["pricePivotHighs"]) <= 30:
                    self.bullishDivPivots["pricePivotHighs"].append(currentValue)
            length = len(self.pivotDataFrame.TAPivotLow)-1
            for idx in range(length-self.minutesBack, 0, -1):
                currentValue = self.pivotDataFrame.TAPivotLow[idx]
                if len(self.bullishDivPivots["TAPivotLows"]) <= 30:
                    self.bullishDivPivots["TAPivotLows"].append(currentValue)

            latestPriceIdx = 0
            variablePriceIdx = len(self.bullishDivPivots["pricePivotHighs"])-1

            while variablePriceIdx > latestPriceIdx:
                print("here, ", variablePriceIdx, " ", latestPriceIdx)
                isBullishDiv = self.util.lowerHighsAndHigherLows(self.bullishDivPivots, variablePriceIdx, latestPriceIdx)
                if not isBullishDiv:
                    print("not a bullish div")
                    variablePriceIdx -= 1
                    continue
                elif isBullishDiv[0]:
                    print("is a bullish div!")
                    tradeSignal = [isBullishDiv[0], isBullishDiv[1]]

                variablePriceIdx -= 1

            if tradeSignal[0]:
                rsiDateIdx = self.rsiData["Date"].index(tradeSignal[1])
                rsiValue = float(self.rsiData["RSI"][rsiDateIdx])
                print("long rsiValue ", rsiValue)
                if tradeSignal[0] and rsiValue <= 30:
                    print("###################")
                    print("Long trade executed")
                    print("###################")
                
                if rsiValue <= 100:
                    print("###################")
                    print("RSI Long trade executed")
                    print("###################")
        return tradeSignal

    def detectShortEntrySignal(self):
        tradeSignal = [False, None]
        if self.pricePivotLowAndTAPivotHigh[0]:
            pivotLow = self.pricePivotLowAndTAPivotHigh[1]
            TAPivotHigh = self.pricePivotLowAndTAPivotHigh[2]
            self.bearishDivPivots["pricePivotLows"].append(pivotLow)
            self.bearishDivPivots["TAPivotHighs"].append(TAPivotHigh)

            length = len(self.pivotDataFrame.pivotLow)-1
            for idx in range(length-self.minutesBack, 0, -1):
                currentValue = self.pivotDataFrame.pivotLow[idx]
                if len(self.bearishDivPivots["pricePivotLows"]) <= 30:
                    self.bearishDivPivots["pricePivotLows"].append(currentValue)
            length = len(self.pivotDataFrame.TAPivotHigh)-1
            for idx in range(length-self.minutesBack, 0, -1):
                currentValue = self.pivotDataFrame.TAPivotHigh[idx]
                if len(self.bearishDivPivots["TAPivotHighs"]) <= 30:
                    self.bearishDivPivots["TAPivotHighs"].append(currentValue)
            
            latestPriceIdx = 0
            variablePriceIdx = len(self.bearishDivPivots["pricePivotLows"])-1

            while variablePriceIdx > latestPriceIdx:
                print("here, ", variablePriceIdx, " ", latestPriceIdx)
                isBearishDiv = self.util.higherLowsAndLowerHighs(self.bearishDivPivots, variablePriceIdx, latestPriceIdx)
                if not isBearishDiv:
                    print("not a bearish div")
                    variablePriceIdx -= 1
                    continue
                elif isBearishDiv[0]:
                    print("is a bearish div!")
                    tradeSignal = [isBearishDiv[0], isBearishDiv[1]]
                
                variablePriceIdx -= 1

            if tradeSignal[0]:
                rsiDateIdx = self.rsiData["Date"].index(tradeSignal[1])
                rsiValue = float(self.rsiData["RSI"][rsiDateIdx])
                print("short rsiValue ", rsiValue)
                if tradeSignal[0] and rsiValue >= 70:
                    print("###################")
                    print("Short trade executed")
                    print("###################")
                
                if rsiValue >= 0:
                    print("###################")
                    print("RSI Short trade executed")
                    print("###################")
        return tradeSignal