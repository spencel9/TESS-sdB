import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np
from scipy.optimize import curve_fit
import csv 
import os
import fnmatch
import statistics
from astropy.timeseries import LombScargle

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
        for n in range(350):
            try:
                file_a = './' + str(TICNumber) + '_' + str(sector) + '_'+ str(n) +'.csv'
                result = pd.read_csv(file_a, names=['time','ppt'])
                
                time=result['time']
                #print('Time: ', time)
                
                ppt = result['ppt']
                #print('PPT' , ppt)
                f = best_freq_1
                bounds = ([0.0, 0.0], [100.0, 1.0])
                popt, pcov = curve_fit(function, time, ppt, bounds=bounds)
               
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
    
    
    
    def gettingPlots(self, a, TICNumber, sector, best_freq_1):
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
        #plt.ylim(np.min(result['OC'])-30,np.max(result['OC'])+30)
        #plt.tick_params(axis='both', which='major', labelsize=20)
        #plt.title('O-C result',fontsize=20)
        plt.xlabel("time(days)",fontsize=20)
        plt.ylabel("O-C(s)",fontsize=20)
        
        ls1 = LombScargle(result['time'], result['OC'], result['OC_err'])
        #if you receive errors, you can set minimum and maximum frequencies.
        #frequency1, power1 = ls1.autopower(minimum_frequency = 1, maximum_frequency=500)#(nyquist_factor=1)maximum_frequency=500)
        frequency1, power1 = ls1.autopower(nyquist_factor=1)
                                        
        # Get the best frequency from the Lomb-Scargle periodogram
        best_frequency1 = frequency1[np.argmax(power1)]
        ls = LombScargle(result['time0'], result['OC'], result['OC_err'])     
        def sinusoidal_model(t, A, omega, phi):
            return A * np.sin(2 * np.pi * omega * t + phi)
        time2 = np.arange(2700)/100
        initial_guess1 = [np.sqrt(2 * ls.power(frequency=best_frequency1)), best_frequency1, 0]
        from scipy.optimize import curve_fit
        popt, _ = curve_fit(sinusoidal_model, result['time0'], result['OC'], p0=initial_guess1)
        best_amplitude1, best_frequency1, best_phase1 = popt
        best_phase_normalized1 = best_phase1 % (2 * np.pi) / (2 * np.pi)

        best_fit_model1 = sinusoidal_model(time2, best_amplitude1, best_frequency1, best_phase1)
        

        #plt.scatter(x=result['time0'], y=result['OC'],linewidth=5)
        plt.scatter(x=time2, y = best_fit_model1, linewidth=1)
        plt.ylim(np.min(result['OC'])-30,np.max(result['OC'])+30)
        plt.tick_params(axis='both', which='major', labelsize=20)
        plt.title('O-C result with sine curve',fontsize=20)
        #plt.xlabel("time(days)",fontsize=20)
        #plt.ylabel("O-C(s)",fontsize=20)
        plt.show()
        plot.savefig('./SavedFigs/' + 'O-C result with sine curve_' + str(TICNumber) + '_sec_' + str(sector))
        print("Program complete")
