import numpy as np
import matplotlib.pyplot as plt
import os
from scipy import interpolate
import pandas as pd

from .lightcurve import DividingDataInTwo
from .lightcurve import GatheringData
from .lightcurve import GettingResultTable

class LargeStdev2:
    
    result2Data = DividingDataInTwo()
    TICNumber = GatheringData()
    resultObj = GettingResultTable()
    
    def calcstdev(self, n, result2, TICNumber, sector):
        mean = np.mean(result2['pdcsap_flux'])
        sd = np.std(result2['pdcsap_flux'])
        range = 4 * sd
        a = mean + range
        b = mean - range
        result2 = result2[result2['pdcsap_flux'] <= a]
        result2 = result2[result2['pdcsap_flux'] >= b]
        result2.plot.scatter(x = 'time', y = 'pdcsap_flux')

        save_dir = './SavedFigs'
        os.makedirs(save_dir, exist_ok=True)
        fileName = str(TICNumber) + '_'+str(sector) + 'result2'
        plt.savefig(os.path.join(save_dir, fileName))
        return result2

class RemovingBadPoints:
    
    result2Data = DividingDataInTwo()
    TICNumber = GatheringData()
    resultObj = GettingResultTable()

    def removing(self, result2):
        
        minBJD2 = result2.time.min()
        maxBJD2 = result2.time.max()
        minFLUX2 = result2.pdcsap_flux.min()
        maxFLUX2  = result2.pdcsap_flux.max()

        result2 = result2[result2['time']>=minBJD2]      
        result2 = result2[result2['time']<=maxBJD2] 
        result2 = result2[result2['pdcsap_flux']>=minFLUX2] 
        result2 = result2[result2['pdcsap_flux']<=maxFLUX2] 

        return result2

class CalcPptFromFlux2:
    
    result2Data = DividingDataInTwo()
    TICNumber = GatheringData()
    resultObj = GettingResultTable()
    
    def calculation(self, n, result2, TICNumber, sector):
        
        med1 = np.median(result2.pdcsap_flux)
        result2['FLUX_norm'] = (result2['pdcsap_flux']/med1) - 1
        result2['ppt']=result2['FLUX_norm']*1000
        result2.plot.scatter(x='time', y='ppt')

        save_dir = './SavedFigs'
        os.makedirs(save_dir, exist_ok=True)
        fileName = str(TICNumber) +'_'+ str(sector) + 'result 2 normalized_ppt'
        plt.savefig(os.path.join(save_dir, fileName))
        return result2

class SplineRemoveAndFitting2:
    
    result2Data = DividingDataInTwo()
    TICNumber = GatheringData()
    resultObj = GettingResultTable()
    
    def removeAndFit(self, result2, TICNumber, sector):
       
        knot_numbers = input("What do you want the knot number to be? ")
        x_new = np.linspace(0,1,int(knot_numbers) +2)[1:-1]
        q_knots = np.quantile(result2.time, x_new) 

        t,c,k = interpolate.splrep(result2.time, result2.ppt, t=q_knots, s=1)
        yfit = interpolate.BSpline(t,c,k)(result2.time) 
        result2['FLUX_fit'] = pd.DataFrame(yfit)

        ax = plt.axes()
        ax.scatter(result2.time, result2.ppt)
        ax.plot(result2.time, result2.FLUX_fit, 'yo')
        ax.set_xlabel('BJD')
        ax.set_ylabel('ppt')
        ax.set_title( str(TICNumber) + str(sector) + ' result 2 normalized_ppt + fitting')
        #plt.show()
        
        save_dir = './SavedFigs'
        os.makedirs(save_dir, exist_ok=True)
        fileName =  str(TICNumber) +'_'+ str(sector) + ' result 2 normalized_ppt + fitting'
        plt.savefig(os.path.join(save_dir, fileName))

        #fitting removal
        result2['FLUX_ppt_fit_removed']= result2['ppt'] - result2['FLUX_fit']
          
        return result2


class figures2:
    
    result2Data = DividingDataInTwo()
    TICNumber = GatheringData()
    resultObj = GettingResultTable()
    
    def fittingAndPlotting(self, n, result2, TICNumber, sector):
       
        #plot
        result2.plot.scatter(x='time', y='FLUX_norm',title= TICNumber+' result 2 ppt:fitting removed')
        save_dir = './SavedFigs'
        os.makedirs(save_dir, exist_ok=True)
        fileName = str(TICNumber) +'_'+ str(sector) + 'result 2 ppt:fitting removed'
        plt.savefig(os.path.join(save_dir, fileName))

