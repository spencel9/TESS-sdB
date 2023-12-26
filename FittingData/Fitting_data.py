import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np
from scipy.optimize import curve_fit
import csv 
import os
import fnmatch
import statistics

from Lightcurve.lightcurve import GatheringData
from Lightcurve.lombScargle import Periodogram

class preAmpCalc:
    def function(self, time, a, p, f):
        return a * np.sin(2*np.pi*(f*time+p))
    
        

class AmpPhaseCalc:
    
    TICNum = GatheringData()
    LSPObj = Periodogram()

    def calc(self, TICNumber, sector, best_freq_1):
        def function(time, a, p):
            return a * np.sin(2*np.pi*(best_freq_1*time+p))
        #f=best_freq_1
        print('Frequency = ' + str(best_freq_1))
        param = [0.472786767, 0.93167]
        with open('originals.csv', 'w') as file:
            pass
        for n in range(50):
            try:
                file_a = './' + str(TICNumber) + '_' + str(sector) + '_'+ str(n) +'.csv'
                result = pd.read_csv(file_a, names=['time','ppt'])
                
                time=result['time']
                #print('Time: ', time)
                
                ppt = result['ppt']
                #print('PPT' , ppt)
                f = best_freq_1
                bounds = ([0.0, 0.0], [100.0, 1.0])
                popt, pcov = curve_fit(function, time, ppt, p0=param, bounds=bounds)
               
                sigma = np.sqrt([pcov[0,0], pcov[1,1]])

                print(n)
                a = popt[0]
                print(a)
                a_err = sigma[0]
                print(a_err)
                p = popt[1]
                print(p)
                p_err = sigma[1]
                print(p_err)
                print()

                t = np.mean(time)
                add = np.array ([n, t, f, a, a_err, p, p_err]).reshape(1,7)
                df = pd.DataFrame(add, columns=['n', 'time', 'frequency', 'amp', 'amp_err', 'phase', 'phase_err'])
                with open ('./originals.csv', 'a') as file:
                    writer = csv.writer (file, lineterminator='\n')
                    for ary in df.values:
                        writer.writerow(ary)
            except ValueError:
                print(n)
                print('Error occured, no data at this point.')
                print()
                

                        
class plotting:    
    def gettingPlots(self, a, TICNumber, sector):
        result = pd.read_csv('originals.csv', names=['n', 'time', 'frequency', 'amp', 'amp_err', 'phase', 'phase_err'])

        result['phase'] = pd.to_numeric(result['phase'], errors='coerce')
        result['frequency'] = pd.to_numeric(result['frequency'], errors='coerce')


        result['time0']= result['time']-result['time'][0]
        result['O']= 86400*result['phase']/result['frequency']
        result['C']=np.mean(result['O'])
        result['OC']=result['O']-result['C']
        result['OC_err']=86400*result['phase_err']/result['frequency']

        plot = plt.figure(figsize=(15,8))
        plt.errorbar(x=result['time0'], y=result['OC'], yerr=result['OC_err'], fmt='bo')
        #filtered_x = [x for x, y in zip(result['time0'], result['OC']) if y !=0]
        #filtered_y = [y for y in result['OC'] if y != 0]
        plt.scatter(x=result['time0'], y=result['OC'], facecolor='peachpuff')
        #plt.plot(result['time0'],result['OC'], linestyle='-', color='blue')
        plt.ylim(np.min(result['OC'])-30,np.max(result['OC'])+30)
        plt.tick_params(axis='both', which='major', labelsize=20)
        plt.title('O-C result',fontsize=20)
        plt.xlabel("time(days)",fontsize=20)
        plt.ylabel("O-C(s)",fontsize=20)
        #result = pd.read_csv('./originals.csv', names=['n', 't', 'f', 'a', 'a_err', 'p', 'p_err']) 
        plt.show()
        plot.savefig('./SavedFigs/' + 'O-C Results_' + str(TICNumber) + '_sec_' + str(sector))
        print("Program complete")
