import math

class Utils(object):
    def __init__(self):
        pass

    # series -> pandas Data Frame
    # seriesClose -> list of close values
    # seriesIdx -> current idx for pivot
    # leftStrength -> bars to check left
    # rightStrength -> bars to check right 
    def pivotHigh(self, series, seriesClose, seriesIdx, leftStrength, rightStrength):
        if seriesIdx - leftStrength < 0:
            return None
        elif seriesIdx + rightStrength > len(seriesClose)-1:
            return None
        
        leftIdx = seriesIdx - leftStrength
        rightIdx = seriesIdx + rightStrength + 1
        pivotCenterValue = seriesClose[seriesIdx]

        isPivot = True
        for idx in range(leftIdx, rightIdx):
            if math.isnan(seriesClose[idx]):
                isPivot = False
            if seriesClose[idx] > pivotCenterValue:
                isPivot = False

        return (seriesClose[seriesIdx], series.Date[seriesIdx]) if isPivot else None
    
    def pivotLow(self, series, seriesClose, seriesIdx, leftStrength, rightStrength):
        if seriesIdx - leftStrength < 0:
            return None
        elif seriesIdx + rightStrength > len(seriesClose)-1:
            return None

        leftIdx = seriesIdx - leftStrength
        rightIdx = seriesIdx + rightStrength + 1
        pivotCenterValue = seriesClose[seriesIdx]

        isPivot = True
        for idx in range(leftIdx, rightIdx):
            if math.isnan(seriesClose[idx]):
                isPivot = False
            if seriesClose[idx] < pivotCenterValue:
                isPivot = False

        return (seriesClose[seriesIdx], series.Date[seriesIdx]) if isPivot else None
    
    # pricePivotHigh -> list from data frame of high pivot prices
    # TAPivotLow -> list from data frame of low pivot TA prices
    # number of minutes back to look for root pivot signal
    def findPricePivotHighAndTAPivotLow(self, pricePivotHigh, TAPivotLow, minutesBack):
        pricePivot = None
        TAPivot = None
        length = len(pricePivotHigh)-1
        for idx in range(length, length-minutesBack, -1):
            if pricePivotHigh[idx] is not None:
                pricePivot = pricePivotHigh[idx]
            if TAPivotLow[idx] is not None:
                TAPivot = TAPivotLow[idx]
        
        return [True, pricePivot, TAPivot] if (pricePivot and TAPivot) else [False, None]
    
    def findPricePivotLowAndTAPivotHigh(self, pricePivotLow, TAPivotHigh, minutesBack):
        pricePivot = None
        TAPivot = None
        length = len(pricePivotLow)-1
        for idx in range(length, length-minutesBack, -1):
            if pricePivotLow[idx] is not None:
                pricePivot = pricePivotLow[idx]
            if TAPivotHigh[idx] is not None:
                TAPivot = TAPivotHigh[idx]
        
        return [True, pricePivot, TAPivot] if (pricePivot and TAPivot) else [False, None]

    def lowerHighsAndHigherLows(self, bullishDivPivots, variablePriceIdx, latestPriceIdx):
        pricePivotHighOne = bullishDivPivots["pricePivotHighs"][variablePriceIdx]
        pricePivotHighTwo = bullishDivPivots["pricePivotHighs"][latestPriceIdx]
        TAPivotLowOne = bullishDivPivots["TAPivotLows"][variablePriceIdx]
        TAPivotLowTwo = bullishDivPivots["TAPivotLows"][latestPriceIdx]
        
        # if there isn't a pivot at this interval, return
        if pricePivotHighOne is None:
            return [False, None]
        
        # if there is a price pivot high, but not a TA pivot low, check back one bar and forward one bar for a TA pivot low
        if TAPivotLowOne is None:
            if variablePriceIdx-1 >= 0 and bullishDivPivots["TAPivotLows"][variablePriceIdx-1] is not None:
                TAPivotLowOne = bullishDivPivots["TAPivotLows"][variablePriceIdx-1]
            elif variablePriceIdx+1 < len(bullishDivPivots["TAPivotLows"]) and bullishDivPivots["TAPivotLows"][variablePriceIdx+1] is not None:
                TAPivotLowOne = bullishDivPivots["TAPivotLows"][variablePriceIdx+1]
        
        # if there wasn't a TA pivot at +1 bar or -1 bar or current bar, then return False
        if TAPivotLowOne is None:
            return [False, None]

        # if pivots occurred within set parameters, check for lower price highs
        if pricePivotHighTwo[0] < pricePivotHighOne[0] and TAPivotLowTwo[0] > TAPivotLowOne[0]:
            return [True, pricePivotHighTwo[1]]
        return [False, None]
    
    def higherLowsAndLowerHighs(self, bearishDivPivots, variablePriceIdx, latestPriceIdx):
        pricePivotLowOne = bearishDivPivots["pricePivotLows"][variablePriceIdx]
        pricePivotLowTwo = bearishDivPivots["pricePivotLows"][latestPriceIdx]
        TAPivotHighOne = bearishDivPivots["TAPivotHighs"][variablePriceIdx]
        TAPivotHighTwo = bearishDivPivots["TAPivotHighs"][latestPriceIdx]

        if pricePivotLowOne is None:
            return [False, None]
        
        if TAPivotHighOne is None:
            if variablePriceIdx-1 >= 0 and bearishDivPivots["TAPivotHighs"][variablePriceIdx-1] is not None:
                TAPivotHighOne = bearishDivPivots["TAPivotHighs"][variablePriceIdx-1]
            elif variablePriceIdx+1 < len(bearishDivPivots["TAPivotHighs"]) and bearishDivPivots["TAPivotHighs"][variablePriceIdx+1] is not None:
                TAPivotHighOne = bearishDivPivots["TAPivotHighs"][variablePriceIdx+1]

        if TAPivotHighOne is None:
            return [False, None]

        if pricePivotLowTwo[0] > pricePivotLowOne[0] and TAPivotHighTwo[0] < TAPivotHighOne[0]:
            return [True, pricePivotLowTwo[1]]
        return [False, None]