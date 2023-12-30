import numpy as np
import matplotlib.pyplot as plt
import os
from scipy import interpolate
import pandas as pd

from .lightcurve import GatheringData
from .lightcurve import DividingDataInTwo
from .lightcurve import GettingResultTable

class removeLargeStdDev:
    def stdevremove(self, n, result1, TICNumber, sector):
        mean = np.mean(result1['pdcsap_flux'])
        sd = np.std(result1['pdcsap_flux'])
        range = 4 * sd
        a = mean + range
        b = mean - range
        result1 = result1[result1['pdcsap_flux'] <= a]
        result1 = result1[result1['pdcsap_flux'] >= b]
        result1.plot.scatter(x = 'time', y = 'pdcsap_flux')

        save_dir = './SavedFigs'
        os.makedirs(save_dir, exist_ok=True)
        fileName = str(TICNumber) +'_'+ str(sector) +'_'+ 'result1'
        plt.savefig(os.path.join(save_dir, fileName))
        return result1

class CalcPptFromFlux:
    def calc(self, n, result1, TICNumber, lc_collection):
        med1 = np.median(result1.pdcsap_flux)
        result1['FLUX_norm'] = (result1['pdcsap_flux']/med1) - 1
        result1['ppt']=result1['FLUX_norm']*1000
        result1.plot.scatter(x='time', y='ppt')

        save_dir = './SavedFigs'
        os.makedirs(save_dir, exist_ok=True)
        fileName = str(TICNumber) + '_'+str(lc_collection[n].sector) +'_'+ 'result 1 normalized_ppt'
        plt.savefig(os.path.join(save_dir, fileName))
        return result1


class splineRemoveAndFitting:
    def removeAndFit(self, result1, TICNumber, sector):
        #spline remove and fitting
        knot_numbers = input("What do you want the knot number to be? ")
        x_new = np.linspace(0,1,int(knot_numbers) +2)[1:-1]
        q_knots = np.quantile(result1.time, x_new) 
        
        t,c,k = interpolate.splrep(result1.time, result1.ppt, t=q_knots, s=1)
        yfit = interpolate.BSpline(t,c,k)(result1.time) 
        result1['FLUX_fit'] = pd.DataFrame(yfit)

        figure = plt.figure()
        ax = plt.axes()
        ax.scatter(result1.time, result1.ppt)
        ax.plot(result1.time, result1.FLUX_fit, 'yo')
        ax.set_xlabel('BJD')
        ax.set_ylabel('ppt')
        ax.set_title(TICNumber+' normalized_ppt + fitting')
        ax.set_title( str(TICNumber) + str(sector) + ' result 1 normalized_ppt + fitting')
        #plt.show()
        
        save_dir = './SavedFigs'
        os.makedirs(save_dir, exist_ok=True)
        fileName =  str(TICNumber) +'_'+ str(sector) + ' result 1 normalized_ppt + fitting'
        plt.savefig(os.path.join(save_dir, fileName))

        #fitting removal
        result1['FLUX_ppt_fit_removed']= result1['ppt'] - result1['FLUX_fit']
        
          
        return result1 

class figures:
    def fittingAndPlotting(self, n, result, TICNumber, sector):

        ax = plt.axes()
        ax.scatter(result.time, result.ppt)
        

        #plot
        result.plot.scatter(x='time', y='FLUX_norm',title= TICNumber+' result 1 ppt:fitting removed')
        save_dir = './SavedFigs'
        os.makedirs(save_dir, exist_ok=True)
        fileName = str(TICNumber) +'_'+ str(sector) + 'result 1 ppt:fitting removed'
        plt.savefig(os.path.join(save_dir, fileName))