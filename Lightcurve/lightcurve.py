import numpy as np
import lightkurve as lk
import matplotlib.pyplot as plt
import pandas as pd
from scipy import interpolate
from astropy.timeseries import LombScargle
import math
import os
#%matplotlib inline

def main():
    #this file objects
    GettingData = GatheringData()
    GettingNumberOfSectors = NumberOfSector()
    ResultTable = GettingResultTable()
    DivideData = DividingDataInTwo()
    SplittingData = DividingDataInTwo()
    
    from .Results1 import removeLargeStdDev
    from .Results1 import CalcPptFromFlux
    from .Results1 import splineRemoveAndFitting
    from .Results1 import figures

    Stdev1 = removeLargeStdDev()
    calc1 = CalcPptFromFlux()
    splineRemove1 = splineRemoveAndFitting()
    figures1 = figures()
    
    from .Results2 import LargeStdev2
    from .Results2 import RemovingBadPoints
    from .Results2 import CalcPptFromFlux2
    from .Results2 import SplineRemoveAndFitting2
    from .Results2 import figures2
    
    Stdev2 = LargeStdev2()
    BadPoints = RemovingBadPoints()
    Calc2 = CalcPptFromFlux2()
    splineRemove2 = SplineRemoveAndFitting2()
    figures2 = figures2()
    Results1And2 = Combining_1_and_2()
    
    from .lombScargle import Periodogram
    from .lombScargle import PeriodogramCertTimeRange
    
    csvObj = MakingCSVToBeDivided()
    periodObj = Periodogram()
    periodCertTimeObj = PeriodogramCertTimeRange()

    #objects for divide_data
    from DivideData.divide_data import FindingFileAndDivide
    fileAndDivideObj = FindingFileAndDivide()

    #objects for Fitting_data
    from FittingData.Fitting_data import preAmpCalc
    from FittingData.Fitting_data import AmpPhaseCalc
    from FittingData.Fitting_data import plotting
    preCalc = preAmpCalc()
    AmpCalc = AmpPhaseCalc()
    plotsObj = plotting()

    #the running of the code
    Number = int(input('Enter the Target Number only: '))
    TICNumber = 'TIC' + str(Number)
    try:
        specific_sec = int(input('Any sector in specific (just the number)? If not enter n: '))
    except ValueError:
        specific_sec = 'n'
    if(specific_sec == 'n'):
        DownloadableFiles = GettingData.SearchResult(TICNumber, ExposureTime = 20)
        lc_collection = GettingData.DownloadingData(DownloadableFiles)
        SecNum = GettingNumberOfSectors.SectorCalc()
        print('Number of sectors: ' + str(SecNum-1))
    else:
        DownloadableFiles = GettingData.SearchResultSector(TICNumber, ExposureTime = 20, sector = specific_sec)
        lc_collection = GettingData.DownloadingData(DownloadableFiles)
        SecNum = 2
        print('Number of sectors: ' + str(SecNum-1))
        
    
    

    
    result = ResultTable.MakingTable(lc_collection)
    ResultTable.SectorPlot(SecNum, lc_collection)
    for n in range (SecNum-1):
        bounds = DivideData.GettingBounds(n, lc_collection[n]) 
        results = SplittingData.SplittingInHalf(bounds, n, result, lc_collection, TICNumber)
        sector = lc_collection[n].sector
        sectorNumber = lc_collection[0].sector
        result1 = Stdev1.stdevremove(n, results[0], TICNumber, sector)
        result2 = calc1.calc(n, result1, TICNumber, lc_collection)
        fittingAns = input("Do you want spline fitting (Y/N)? ")
        while (fittingAns != 'y' and fittingAns != 'Y' and fittingAns != 'n' and fittingAns != 'N'):
            fittingAns = input('Entered value was incorrect, please try again: ')
        if (fittingAns == 'y'):
            result3 = splineRemove1.removeAndFit(result2, TICNumber, sector)
            figures1.fittingAndPlotting(n,result3, TICNumber, sector)
            result4 = Stdev2.calcstdev(n, results[1], TICNumber, sector)
            result5 = BadPoints.removing(result4)
            result6 = Calc2.calculation(n, result5, TICNumber, sector)
            result7 = splineRemove2.removeAndFit(result6, TICNumber, sector)
            figures2.fittingAndPlotting(n, result7, TICNumber, sector)

        figures1.fittingAndPlotting(n,result2, TICNumber, sector)
        result4 = Stdev2.calcstdev(n, results[1], TICNumber, sector)
        result5 = BadPoints.removing(result4)
        result6 = Calc2.calculation(n, result5, TICNumber, sector)
        figures2.fittingAndPlotting(n, result6, TICNumber, sector)
        combinedResults = Results1And2.combiningResults(result2, result6)
        if (n>0):
            char = input('Would you like to use the frequency from first sector (y/n)?')
            while (char != 'y' and char != 'Y' and char != 'n' and char != 'N'):
                char = input('Entered value was incorrect, please try again: ')
            if(char == 'y' or char == 'Y'):
                file_a = './TIC_' + str(TICNumber) + '_sec' + str(sectorNumber) + '_information' +'.csv'
                result = pd.read_csv(file_a, skiprows=1, names=['Frequency (1/days)', 'Frequency (cycles/day)', 'Frequency error', 'Period (days)', 'Period uncertainty', 'Day Division'])
                best_freq_1=result['Frequency (1/days)'].iloc[0]
                DayDivision = result['Day Division'].iloc[0]
                
                csv_filename = csvObj.makingCSV(n, TICNumber, sector, combinedResults, fittingAns)
                    
                fileAndDivideObj.findfile(csv_filename)
                fileAndDivideObj.DivideWithFile(n, csv_filename, DayDivision, TICNumber, sector, best_freq_1,best_freq_2)
                    
                AmpCalc.calc(TICNumber, sector, best_freq_1)
                    
                plotsObj.gettingPlots(n, TICNumber, sector, best_freq_1, DayDivision)  
            else:
                best_freq_1, fwhm = periodObj.periodogram(n, combinedResults, TICNumber, sector)
                DayDivision, best_freq_2 = periodCertTimeObj.periodogram(combinedResults, best_freq_1, bounds, TICNumber,sector)
                        
                csv_filename = csvObj.makingCSV(n, TICNumber, sector, combinedResults, fittingAns)
                        
                fileAndDivideObj.findfile(csv_filename)
                fileAndDivideObj.DivideWithFile(n, csv_filename, DayDivision, TICNumber, sector, best_freq_1,best_freq_2)
                        
                AmpCalc.calc(TICNumber, sector, best_freq_1)
                        
                plotsObj.gettingPlots(n, TICNumber, sector, best_freq_1, DayDivision)
        else:
            best_freq_1, fwhm = periodObj.periodogram(n, combinedResults, TICNumber, sector)
            DayDivision, best_freq_2 = periodCertTimeObj.periodogram(combinedResults, best_freq_1, bounds, TICNumber,sector)
                        
            csv_filename = csvObj.makingCSV(n, TICNumber, sector, combinedResults, fittingAns)
                        
            fileAndDivideObj.findfile(csv_filename)
            fileAndDivideObj.DivideWithFile(n, csv_filename, DayDivision, TICNumber, sector, best_freq_1,best_freq_2)
                        
            AmpCalc.calc(TICNumber, sector, best_freq_1)
                        
            plotsObj.gettingPlots(n, TICNumber, sector, best_freq_1, DayDivision)
    print('Program complete')

class GatheringData:
    
    IDNumber = 2
    Target = 'TIC' + str(IDNumber)
    TICNumber = 'TIC_' + str(IDNumber)
    ExposureTime = 20
    lc_collection = [0,0,0]

    def SearchResult(self, Target,  ExposureTime):
        ExposureTime = 20
        DownloadableFiles = lk.search_lightcurve(target = Target, exptime = ExposureTime)
        print(DownloadableFiles)
        return DownloadableFiles
    def SearchResultSector(self, Target,  ExposureTime, sector):
        ExposureTime = 20
        DownloadableFiles = lk.search_lightcurve(target = Target, exptime = ExposureTime, sector = sector)
        print(DownloadableFiles)
        return DownloadableFiles

    
    def DownloadingData(self, Downloadablefiles):
        lc_collection = Downloadablefiles.download_all()
        return lc_collection

class NumberOfSector:
    GatheringDataObj = GatheringData()
    def SectorCalc(self):
        NumberOfSec = len(self.GatheringDataObj.lc_collection)
        return NumberOfSec

class GettingResultTable:

    def __init__(self):
        self.DataForSector = GatheringData()

        self.Lc_all = None
        self.Result = None
    
    def MakingTable(self, lc_collection):
        Lc_all = lc_collection.stitch()
        Result = Lc_all.to_pandas()
        Result = Result.reset_index()
        print()
        return Result
    
    def SectorPlot(self, SecNum, lc_collection):
        for n in range ((SecNum - 1)):
            lc_Sector = lc_collection[n]
            lc_Sector.plot()
            save_dir = './SavedFigs'
            os.makedirs(save_dir, exist_ok=True)
            fileName = 'Sec_' + str(lc_collection[n].sector) + '_' + str(self.DataForSector.TICNumber)
            plt.savefig(os.path.join(save_dir, fileName))
        
class DividingDataInTwo:

    def __init__(self):
        self.DataObj = GettingResultTable()
        self.DataObj2 = GatheringData()

        self.Start = None
        self.Finish = None
        self.TimeWithoutFlux = None
        self.Times = []
        self.result1 = []
        self.result2 = []

    def GettingBounds(self, n, lc_collection):
        
        Start = lc_collection.time[0]
        Finish = lc_collection.time[-1]

        TimeWithoutFlux = ((Finish - Start)/2) + Start
        
        Times = [Start,TimeWithoutFlux,Finish]
        
        return Times

    def SplittingInHalf(self, bounds, n, result, lc_collection, TICNumber):
        self.resultObj = GettingResultTable()
        self.TICObj = GatheringData()
        
        a = bounds[0].btjd
        b = bounds[1].btjd
        c = bounds[2].btjd
        
        result1 = result[(result['time']>=a) & (result['time']<=b)] 
        result1.plot.scatter(x='time', y = 'pdcsap_flux', title = TICNumber + 'raw result 1 (first half)')
        save_dir = './SavedFigs'
        fileName = str(TICNumber) +'_'+ str(lc_collection[n].sector) + 'raw_results_first_half'
        plt.savefig(os.path.join(save_dir, fileName))
       
        result2 = result[(result['time']>= b) & (result['time']<= c)]
        result2.plot.scatter(x='time', y = 'pdcsap_flux', title = TICNumber + 'raw result 2 (second half)')
        fileName = str(TICNumber) +'_'+ str(lc_collection[n].sector) + 'raw_results_second_half'
        plt.savefig(os.path.join(save_dir, fileName))
        
        results = [result1, result2]
        return results

# add frequency table into new file
class Combining_1_and_2:
    def combiningResults(self, result1, result2):
        frames = [result1, result2]
        result =  pd.concat(frames)
        results = result
        return results

class MakingCSVToBeDivided:
    TICNum = GatheringData()
    resultObj = GettingResultTable()
    result12 = Combining_1_and_2()

    def makingCSV(self, n, TICNumber, sector, result, fittingAns):
        save_dir = './MainSectors/'
        os.makedirs(save_dir, exist_ok=True)
        csv_filename = './MainSectors/' + str(TICNumber)+'_'+str(sector)+'.csv'
        txt_filename = './MainSectors/' + str(TICNumber)+'_'+str(sector) +'.txt'
        print(csv_filename)
        print(txt_filename)
        if (fittingAns == 'Y'):
            result.to_csv(csv_filename, index = False, header = False, columns = ['time','FLUX_ppt_fit_removed'])
            with open(csv_filename, 'r') as inp, open(txt_filename, 'w') as out:
                for line in inp:
                    line = line.replace(',', '\t')
                    out.write(line)
            return csv_filename
        else:
            result.to_csv(csv_filename, index = False, header = False, columns = ['time','ppt'])
            with open(csv_filename, 'r') as inp, open(txt_filename, 'w') as out:
                for line in inp:
                    line = line.replace(',', '\t')
                    out.write(line)
            return csv_filename

        

        



    