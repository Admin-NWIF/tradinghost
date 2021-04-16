import ibapi
import datetime
import threading
import time
import math
import pandas as pd
import numpy as np
import pandas_ta as ta
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from utils import Utils

dict = {
            "Open": [],
            "High": [],
            "Low": [], 
            "Close": [], 
            "Volume": [],
            "Date": []
        }

pivotData = {
            "pivotHigh": [],
            "pivotLow": [],
            "TAPivotHigh": [],
            "TAPivotLow": []
        }

bullishDivPivots = {
            "pricePivotHighs": [],
            "TAPivotLows": []
        }

bearishDivPivots = {
            "pricePivotLows": [],
            "TAPivotHighs": []
        }

TAData = {
            "Value": [],
            "Date": []
        }

rsiData = {
            "RSI": [],
            "Date": []
        }

dataFrame = None

class TestWrapper(EWrapper):
    def historicalData(self, reqId, bar):
        dict["Open"].append(bar.open)
        dict["High"].append(bar.high)
        dict["Low"].append(bar.low)
        dict["Close"].append(bar.close)
        dict["Volume"].append(bar.volume)
        dict["Date"].append(bar.date)

    def historicalDataEnd(self, reqId, start, end):
        super().historicalDataEnd(reqId, start, end)
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)

        # Populate data frame
        dataFrame = pd.DataFrame(dict, columns = ["Open", "High", "Low", "Close", "Volume", "Date"])
        # print(dataFrame)

        # Calculate Returns and append to the df DataFrame
        #df.ta.log_return(cumulative=True, append=True)
        #df.ta.percent_return(cumulative=True, append=True)
        #pd.set_option("display.max_rows", None, "display.max_columns", None)

        # New Columns with results
        #df.columns

        # Take a peek
        #df.tail()
        #print()
        #print(df)

        dpo = ta.dpo(dataFrame.Close, length=20, centered=False, offset=None)
        for idx, val in enumerate(dpo):
            TAData["Value"].append(val)
            TAData["Date"].append(dataFrame.Date[idx])
        TADataFrame = pd.DataFrame(TAData, columns = ["Value", "Date"])

        rsi = ta.rsi(dataFrame.Close, 14)
        for idx, val in enumerate(rsi):
            rsiData["RSI"].append(val)
            rsiData["Date"].append(dataFrame.Date[idx])
        rsiDataFrame = pd.DataFrame(rsiData, columns = ["RSI", "Date"])

        #print(TADataFrame)
        #print(rsiDataFrame)

        util = Utils()
        for idx in range(len(dataFrame.Close)):
            pivotData["pivotHigh"].append(util.pivotHigh(dataFrame, dataFrame.Close, idx, 3, 1))
            pivotData["pivotLow"].append(util.pivotLow(dataFrame, dataFrame.Close, idx, 3, 1))
            pivotData["TAPivotHigh"].append(util.pivotHigh(TADataFrame, TADataFrame.Value, idx, 3, 1))
            pivotData["TAPivotLow"].append(util.pivotLow(TADataFrame, TADataFrame.Value, idx, 3, 1))

        pivotDataFrame = pd.DataFrame(pivotData, columns = ["pivotHigh", "pivotLow", "TAPivotHigh", "TAPivotLow"])
        minutesBack = 3
        pricePivotHighAndTAPivotLow = util.findPricePivotHighAndTAPivotLow(pivotDataFrame.pivotHigh, pivotDataFrame.TAPivotLow, minutesBack)
        pricePivotLowAndTAPivotHigh = util.findPricePivotLowAndTAPivotHigh(pivotDataFrame.pivotLow, pivotDataFrame.TAPivotHigh, minutesBack)

        if pricePivotHighAndTAPivotLow[0]:
            pivotHigh = pricePivotHighAndTAPivotLow[1]
            TAPivotLow = pricePivotHighAndTAPivotLow[2]
            bullishDivPivots["pricePivotHighs"].append(pivotHigh)
            bullishDivPivots["TAPivotLows"].append(TAPivotLow)

            length = len(pivotDataFrame.pivotHigh)-1
            for idx in range(length-minutesBack, 0, -1):
                currentValue = pivotDataFrame.pivotHigh[idx]
                if len(bullishDivPivots["pricePivotHighs"]) <= 30:
                    bullishDivPivots["pricePivotHighs"].append(currentValue)
            length = len(pivotDataFrame.TAPivotLow)-1
            for idx in range(length-minutesBack, 0, -1):
                currentValue = pivotDataFrame.TAPivotLow[idx]
                if len(bullishDivPivots["TAPivotLows"]) <= 30:
                    bullishDivPivots["TAPivotLows"].append(currentValue)

        elif pricePivotLowAndTAPivotHigh[0]:
            pivotLow = pricePivotLowAndTAPivotHigh[1]
            TAPivotHigh = pricePivotLowAndTAPivotHigh[2]
            bearishDivPivots["pricePivotLows"].append(pivotLow)
            bearishDivPivots["TAPivotHighs"].append(TAPivotHigh)

            length = len(pivotDataFrame.pivotLow)-1
            for idx in range(length-minutesBack, 0, -1):
                currentValue = pivotDataFrame.pivotLow[idx]
                if len(bearishDivPivots["pricePivotLows"]) <= 30:
                    bearishDivPivots["pricePivotLows"].append(currentValue)
            length = len(pivotDataFrame.TAPivotHigh)-1
            for idx in range(length-minutesBack, 0, -1):
                currentValue = pivotDataFrame.TAPivotHigh[idx]
                if len(bearishDivPivots["TAPivotHighs"]) <= 30:
                    bearishDivPivots["TAPivotHighs"].append(currentValue)
        
        if pricePivotHighAndTAPivotLow[0]:
            latestPriceIdx = 0
            variablePriceIdx = len(bullishDivPivots["pricePivotHighs"])-1

            tradeSignal = False
            while variablePriceIdx > latestPriceIdx:
                print("here, ", variablePriceIdx, " ", latestPriceIdx)
                isBullishDiv = util.lowerHighsAndHigherLows(bullishDivPivots, variablePriceIdx, latestPriceIdx)
                if not isBullishDiv:
                    print("not a bullish div")
                    variablePriceIdx -= 1
                    continue
                elif isBullishDiv[0]:
                    print("is a bullish div!")
                    tradeSignal = [isBullishDiv[0], isBullishDiv[1]]

                variablePriceIdx -= 1

            rsiDateIdx = rsiData["Date"].index(tradeSignal[1])
            rsiValue = float(rsiData["RSI"][rsiDateIndex])
            print("long rsiValue ", rsiValue)
            if tradeSignal[0] and rsi <= 30:
                print("###################")
                print("Long trade executed")
                print("###################")
            
            if rsiValue <= 100:
                print("###################")
                print("RSI Long trade executed")
                print("###################")

        elif pricePivotLowAndTAPivotHigh[0]:
            latestPriceIdx = 0
            variablePriceIdx = len(bearishDivPivots["pricePivotLows"])-1

            tradeSignal = [False, None]
            while variablePriceIdx > latestPriceIdx:
                print("here, ", variablePriceIdx, " ", latestPriceIdx)
                isBearishDiv = util.higherLowsAndLowerHighs(bearishDivPivots, variablePriceIdx, latestPriceIdx)
                if not isBearishDiv:
                    print("not a bearish div")
                    variablePriceIdx -= 1
                    continue
                elif isBearishDiv[0]:
                    print("is a bearish div!")
                    tradeSignal = [isBearishDiv[0], isBearishDiv[1]]
                
                variablePriceIdx -= 1

            rsiDateIdx = rsiData["Date"].index(tradeSignal[1])
            rsiValue = float(rsiData["RSI"][rsiDateIdx])
            print("short rsiValue ", rsiValue)
            if tradeSignal[0] and rsiValue >= 70:
                print("###################")
                print("Short trade executed")
                print("###################")
            
            if rsiValue >= 0:
                print("###################")
                print("RSI Short trade executed")
                print("###################")

        print("End")

    def historicalDataUpdate(self, reqId, bar):
        print("HistoricalDataUpdate. ReqId:", reqId, "BarData.", bar)

class TestClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self,wrapper)

class TestApp(TestWrapper, TestClient):
    def __init__(self, ipaddress, portid, clientid):
        TestWrapper.__init__(self)
        TestClient.__init__(self, wrapper=self)
        self.connect(ipaddress, portid, clientid)

        # Initialise the threads for various components
        thread = threading.Thread(target=self.run)
        thread.start()
        setattr(self, "_thread", thread)

        # Listen for the IB responses
        # self.init_error()

    def tickPrice(self, reqId, tickType, price, attrib):
        if tickType == 2 and reqId == 1:
            print('The current ask price is: ', price)

    def createContract(self, symbol, secType, currency, exchange):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = secType
        contract.currency = currency
        contract.exchange = exchange
        return contract

if __name__ == '__main__':
    # Application parameters
    host = '127.0.0.1'  # Localhost, but change if TWS is running elsewhere
    port = 4001  # Change to the appropriate IB TWS account port number
    client_id = 99

    print("Launching IB API application...")

    # Instantiate the IB API application
    app = TestApp(host, port, client_id)
    ibkrContract = app.createContract("MSFT", "STK", "USD", "SMART")
    hour = 9
    minute = 30
    while hour != 16:
        queryTime = datetime.datetime(2021, 4, 13, hour, minute, 00).strftime("%Y%m%d %H:%M:%S")
        app.reqHistoricalData(4102, ibkrContract, queryTime ,"1 D", "1 min", "MIDPOINT", 1, 1, False, [])
        if minute == 59:
            hour += 1
            minute = 0
        else:
            minute += 1
        print(datetime.datetime(2021, 4, 13, hour, minute, 00))
        time.sleep(1)
    # app.reqHistoricalData(4103, app.ContractSamples.EuropeanStock(), queryTime, "10 D", "1 min", "TRADES", 1, 1, False, [])
    # app.reqHistoricalData(4104, app.ContractSamples.EurGbpFx(), "", "1 M", "1 day", "MIDPOINT", 1, 1, True, [])

    print("Successfully launched IB API application...")