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
from dporsiDiv import DPORSIDiv

dict = {
            "Open": [],
            "High": [],
            "Low": [], 
            "Close": [], 
            "Volume": [],
            "Date": []
        }

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

        # Insert custom strategy class and populate indicators
        dpoRsiDivStrategy = DPORSIDiv(dataFrame)
        dpoRsiDivStrategy.populateDPO()
        dpoRsiDivStrategy.populateRSI()
        dpoRsiDivStrategy.populateHighsAndLows()

        # Generate long or short entry signal
        longEntry = dpoRsiDivStrategy.detectLongEntrySignal()
        shortEntry = dpoRsiDivStrategy.detectShortEntrySignal()

        if longEntry[0]:
            print("Long")
        elif shortEntry[0]:
            print("Short")

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
        app.reqHistoricalData(4102, ibkrContract, queryTime ,"2400 S", "1 min", "MIDPOINT", 1, 1, False, [])
        if minute == 59:
            hour += 1
            minute = 0
        else:
            minute += 1
        print(datetime.datetime(2021, 4, 13, hour, minute, 00))
        time.sleep(1)

    print("Successfully launched IB API application...")