import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np
from scipy.optimize import curve_fit
import csv 
import os
import fnmatch
import statistics
from astropy.timeseries import LombScargle
from scipy.optimize import curve_fit

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
    
    
    
    def gettingPlots(self, a, TICNumber, sector, best_freq_1, DayDivision):
        sine_curve_input = input('Would you like a reference sine curve on the O-C Diagram (y/n)? ')
        while(sine_curve_input != 'n' and sine_curve_input != 'y' and sine_curve_input != 'N' and sine_curve_input != 'Y'):
            sine_curve_input = input('Entered value for the sine curve was not n or y, please try again. ')
        linear_fit = input('Would you like a linear fit removal (y/n)?')
        while(linear_fit != 'n' and linear_fit != 'y' and linear_fit != 'N' and linear_fit != 'Y'):
            linear_fit = input('Entered value for linear fit removal was not n or y, please try again. ')
        
        if((linear_fit == 'y' or linear_fit == 'Y') and (sine_curve_input == 'y' or sine_curve_input == 'y')):
            result = pd.read_csv('originals.csv', names=['n', 'time', 'frequency', 'amp', 'amp_err', 'phase', 'phase_err'])

            result['phase'] = pd.to_numeric(result['phase'], errors='coerce')
            result['frequency'] = pd.to_numeric(result['frequency'], errors='coerce')


            result['time0']= result['time']-result['time'][0]
            result['O']= 86400*result['phase']/result['frequency']
            result['C']=np.mean(result['O'])
            result['OC']=result['C']-result['O']
            result['OC_err']=86400*result['phase_err']/result['frequency']
            
            plot = plt.figure(figsize=(15,8))
            #plt.errorbar(x=result['time0'], y=result['OC'], yerr=result['OC_err'], fmt='bo')
            #filtered_x = [x for x, y in zip(result['time0'], result['OC']) if y !=0]
            #filtered_y = [y for y in result['OC'] if y != 0]
            #plt.scatter(x=result['time0'], y=result['OC'], facecolor='peachpuff')
            #plt.plot(result['time0'],result['OC'], linestyle='-', color='blue')
            #plt.ylim(np.min(result['OC'])-30,np.max(result['OC'])+30)
            #plt.tick_params(axis='both', which='major', labelsize=20)
            #plt.title('O-C result',fontsize=20)
            plt.xlabel("time(days)",fontsize=20)
            plt.ylabel("O-C(s)",fontsize=20)



            def fit_funct(a, x, b):
                return a*x+b
            from scipy.optimize import curve_fit
            params = curve_fit(fit_funct, result['time0'], result['OC'])
            [a,b] = params[0]
            fit_remove = fit_funct(a, result['time0'], b)
            new_result = result['OC'] - fit_remove



            ls = LombScargle(result['time0'], new_result, result['OC_err']) 
            def sinusoidal_model(t, A, omega, phi):
                return A * np.sin(2 * np.pi * omega * t + phi)
            ls1 = LombScargle(result['time'], new_result, result['OC_err'])
            frequency1, power1 = ls1.autopower(nyquist_factor=1)
                                            
            # Get the best frequency from the Lomb-Scargle periodogram
            best_frequency1 = frequency1[np.argmax(power1)]
            last_index = len(result) - 1 
            time2 = np.arange(result['time'][last_index])/100
            
            initial_guess1 = [np.sqrt(2 * ls.power(frequency=best_frequency1)), best_frequency1, 0]
            popt144, _ = curve_fit(sinusoidal_model, result['time0'], new_result, p0=initial_guess1)
            best_amplitude1, best_frequency1, best_phase1 = popt144
            best_fit_model1 = sinusoidal_model(time2, best_amplitude1, best_frequency1, best_phase1)
            #ls1 = LombScargle(result['time'], new_result, result['OC_err'])
            #if you receive errors, you can set minimum and maximum frequencies.
            #frequency1, power1 = ls1.autopower(minimum_frequency = 1, maximum_frequency=500)#(nyquist_factor=1)maximum_frequency=500)
               
            best_phase_normalized1 = best_phase1 % (2 * np.pi) / (2 * np.pi)

            
            popt255, pcov = curve_fit(sinusoidal_model, result['time'], new_result, p0=initial_guess1)
            sigma24 = np.sqrt([pcov[0,0], pcov[1,1], pcov[2,2]])
            
            # Extract amplitude and phase from the fit
            best_amplitude1, best_frequency1, best_phase1 = popt255
            best_amplitude1_err, best_frequency1_err, best_phase1_err = sigma24
            print('Frequency (1/days): ' + str(best_freq_1))
            print('Frequency (cycles/day): ' + str(best_frequency1))
            print('Frequency error: ' + str(best_frequency1_err))
            period = 1/best_frequency1
            print('Period (days): ' + str(period))
            period_uncertainty = period*(best_frequency1_err/best_frequency1)
            print('Period uncertainty: ' + str(period_uncertainty))
            print('Day Division: ' + str(DayDivision))
            
            add = np.array ([best_freq_1, best_frequency1, best_frequency1_err, period, period_uncertainty, DayDivision]).reshape(1,6)
            df = pd.DataFrame(add, columns=['Frequency (1/days)', 'Frequency (cycles/day)', 'Frequency error', 'Period (days)', 'Period uncertainty', 'Day Division'])
            with open ('./TIC_' + str(TICNumber) + '_sec' + str(sector) + '_information.csv', 'w') as file:
                writer = csv.writer (file, lineterminator='\n')
                writer.writerow(df.columns)
                for ary in df.values:
                    writer.writerow(ary)
            
            plt.scatter(x=result['time0'], y=new_result,linewidth=5)
            plt.errorbar(x=result['time0'], y=new_result, yerr=result['OC_err'], fmt='bo')
            plt.scatter(x=time2, y = best_fit_model1, linewidth=1)
            plt.ylim(np.min(new_result)-30,np.max(new_result)+30)

            
            plt.xlim(result['time0'][0], result['time0'][last_index])
            plt.tick_params(axis='both', which='major', labelsize=20)
            plt.title('O-C result with sine curve',fontsize=20)
            #plt.xlabel("time(days)",fontsize=20)
            #plt.ylabel("O-C(s)",fontsize=20)
            plt.show()
            plot.savefig('./SavedFigs/' + 'O-C result_' + str(TICNumber) + '_sec_' + str(sector))
        
        elif((sine_curve_input == 'y' or sine_curve_input == 'Y') and (linear_fit == 'n' or linear_fit == 'N')):
            result = pd.read_csv('originals.csv', names=['n', 'time', 'frequency', 'amp', 'amp_err', 'phase', 'phase_err'])

            result['phase'] = pd.to_numeric(result['phase'], errors='coerce')
            result['frequency'] = pd.to_numeric(result['frequency'], errors='coerce')


            result['time0']= result['time']-result['time'][0]
            result['O']= 86400*result['phase']/result['frequency']
            result['C']=np.mean(result['O'])
            result['OC']=result['C']-result['O']
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
            last_index = len(result) - 1 
            time2 = np.arange(result['time'][last_index])/100
            initial_guess1 = [np.sqrt(2 * ls.power(frequency=best_frequency1)), best_frequency1, 0]
            from scipy.optimize import curve_fit
            popt, _ = curve_fit(sinusoidal_model, result['time0'], result['OC'], p0=initial_guess1)
            best_amplitude1, best_frequency1, best_phase1 = popt
            best_phase_normalized1 = best_phase1 % (2 * np.pi) / (2 * np.pi)

            best_fit_model1 = sinusoidal_model(time2, best_amplitude1, best_frequency1, best_phase1)
            
            popt, pcov = curve_fit(sinusoidal_model, result['time'], result['OC'], p0=initial_guess1)
            sigma = np.sqrt([pcov[0,0], pcov[1,1], pcov[2,2]])
            
            # Extract amplitude and phase from the fit
            best_amplitude1, best_frequency1, best_phase1 = popt
            best_amplitude1_err, best_frequency1_err, best_phase1_err = sigma
            print('Frequency (1/days): ' + str(best_freq_1))
            print('Frequency (cycles/day): ' + str(best_frequency1))
            print('Frequency error: ' + str(best_frequency1_err))
            period = 1/best_frequency1
            print('Period (days): ' + str(period))
            period_uncertainty = period*(best_frequency1_err/best_frequency1)
            print('Period uncertainty: ' + str(period_uncertainty))
            print('Day Division: ' + str(DayDivision))
            add = np.array ([best_freq_1, best_frequency1, best_frequency1_err, period, period_uncertainty, DayDivision]).reshape(1,6)
            df = pd.DataFrame(add, columns=['Frequency (1/days)', 'Frequency (cycles/day)', 'Frequency error', 'Period (days)', 'Period uncertainty', 'Day Division'])
            with open ('./TIC_' + str(TICNumber) + '_sec' + str(sector) + '_information.csv', 'w') as file:
                writer = csv.writer (file, lineterminator='\n')
                writer.writerow(df.columns)
                for ary in df.values:
                    writer.writerow(ary)
            def fit_funct(a, x, b):
                return a*x+b
            popt, _ = curve_fit(fit_funct, result['time0'], result['OC'])
            #plt.scatter(x=result['time0'], y=result['OC'],linewidth=5)
            plt.scatter(x=time2, y = best_fit_model1, linewidth=1)
            plt.ylim(np.min(result['OC'])-30,np.max(result['OC'])+30)
            plt.tick_params(axis='both', which='major', labelsize=20)
            plt.title('O-C result with sine curve',fontsize=20)
            #plt.xlabel("time(days)",fontsize=20)
            #plt.ylabel("O-C(s)",fontsize=20)
            plt.show()
            plot.savefig('./SavedFigs/' + 'O-C result with sine curve_' + str(TICNumber) + '_sec_' + str(sector))
        elif((linear_fit == 'y' or linear_fit == 'Y') and (sine_curve_input == 'n' or sine_curve_input == 'N')):
            result = pd.read_csv('originals.csv', names=['n', 'time', 'frequency', 'amp', 'amp_err', 'phase', 'phase_err'])

            result['phase'] = pd.to_numeric(result['phase'], errors='coerce')
            result['frequency'] = pd.to_numeric(result['frequency'], errors='coerce')


            result['time0']= result['time']-result['time'][0]
            result['O']= 86400*result['phase']/result['frequency']
            result['C']=np.mean(result['O'])
            result['OC']=result['C']-result['O']
            result['OC_err']=86400*result['phase_err']/result['frequency']
            
            plot = plt.figure(figsize=(15,8))
            #plt.errorbar(x=result['time0'], y=result['OC'], yerr=result['OC_err'], fmt='bo')
            #filtered_x = [x for x, y in zip(result['time0'], result['OC']) if y !=0]
            #filtered_y = [y for y in result['OC'] if y != 0]
            #plt.scatter(x=result['time0'], y=result['OC'], facecolor='peachpuff')
            #plt.plot(result['time0'],result['OC'], linestyle='-', color='blue')
            #plt.ylim(np.min(result['OC'])-30,np.max(result['OC'])+30)
            #plt.tick_params(axis='both', which='major', labelsize=20)
            #plt.title('O-C result',fontsize=20)
            plt.xlabel("time(days)",fontsize=20)
            plt.ylabel("O-C(s)",fontsize=20)



            def fit_funct(a, x, b):
                return a*x+b
            from scipy.optimize import curve_fit
            params = curve_fit(fit_funct, result['time0'], result['OC'])
            [a,b] = params[0]
            fit_remove = fit_funct(a, result['time0'], b)
            new_result = result['OC'] - fit_remove



            ls = LombScargle(result['time0'], new_result, result['OC_err']) 
            def sinusoidal_model(t, A, omega, phi):
                return A * np.sin(2 * np.pi * omega * t + phi)
            ls1 = LombScargle(result['time'], new_result, result['OC_err'])
            frequency1, power1 = ls1.autopower(nyquist_factor=1)
                                            
            # Get the best frequency from the Lomb-Scargle periodogram
            best_frequency1 = frequency1[np.argmax(power1)]
            last_index = len(result) - 1 
            time2 = np.arange(result['time'][last_index])/100
            
            initial_guess1 = [np.sqrt(2 * ls.power(frequency=best_frequency1)), best_frequency1, 0]
            popt144, _ = curve_fit(sinusoidal_model, result['time0'], new_result, p0=initial_guess1)
            best_amplitude1, best_frequency1, best_phase1 = popt144
            best_fit_model1 = sinusoidal_model(time2, best_amplitude1, best_frequency1, best_phase1)
            #ls1 = LombScargle(result['time'], new_result, result['OC_err'])
            #if you receive errors, you can set minimum and maximum frequencies.
            #frequency1, power1 = ls1.autopower(minimum_frequency = 1, maximum_frequency=500)#(nyquist_factor=1)maximum_frequency=500)
               
            best_phase_normalized1 = best_phase1 % (2 * np.pi) / (2 * np.pi)

            
            popt255, pcov = curve_fit(sinusoidal_model, result['time'], new_result, p0=initial_guess1)
            sigma24 = np.sqrt([pcov[0,0], pcov[1,1], pcov[2,2]])
            
            # Extract amplitude and phase from the fit
            best_amplitude1, best_frequency1, best_phase1 = popt255
            best_amplitude1_err, best_frequency1_err, best_phase1_err = sigma24
            print('Frequency (1/days): ' + str(best_freq_1))
            print('Frequency (cycles/day): ' + str(best_frequency1))
            print('Frequency error: ' + str(best_frequency1_err))
            period = 1/best_frequency1
            print('Period (days): ' + str(period))
            period_uncertainty = period*(best_frequency1_err/best_frequency1)
            print('Period uncertainty: ' + str(period_uncertainty))
            print('Day Division: ' + str(DayDivision))
            
            add = np.array ([best_freq_1, best_frequency1, best_frequency1_err, period, period_uncertainty, DayDivision]).reshape(1,6)
            df = pd.DataFrame(add, columns=['Frequency (1/days)', 'Frequency (cycles/day)', 'Frequency error', 'Period (days)', 'Period uncertainty', 'Day Division'])
            with open ('./TIC_' + str(TICNumber) + '_sec' + str(sector) + '_information.csv', 'w') as file:
                writer = csv.writer (file, lineterminator='\n')
                writer.writerow(df.columns)
                for ary in df.values:
                    writer.writerow(ary)
            
            plt.scatter(x=result['time0'], y=new_result,linewidth=5)
            plt.errorbar(x=result['time0'], y=new_result, yerr=result['OC_err'], fmt='bo')
            #plt.scatter(x=time2, y = best_fit_model1, linewidth=1)
            plt.ylim(np.min(new_result)-30,np.max(new_result)+30)

            
            plt.xlim(result['time0'][0], result['time0'][last_index])
            plt.tick_params(axis='both', which='major', labelsize=20)
            plt.title('O-C result with sine curve',fontsize=20)
            #plt.xlabel("time(days)",fontsize=20)
            #plt.ylabel("O-C(s)",fontsize=20)
            plt.show()
            plot.savefig('./SavedFigs/' + 'O-C result_' + str(TICNumber) + '_sec_' + str(sector))
        else:
            result = pd.read_csv('originals.csv', names=['n', 'time', 'frequency', 'amp', 'amp_err', 'phase', 'phase_err'])

            result['phase'] = pd.to_numeric(result['phase'], errors='coerce')
            result['frequency'] = pd.to_numeric(result['frequency'], errors='coerce')


            result['time0']= result['time']-result['time'][0]
            result['O']= 86400*result['phase']/result['frequency']
            result['C']=np.mean(result['O'])
            result['OC']=result['C']-result['O']
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
            last_index = len(result) - 1 
            time2 = np.arange(result['time'][last_index])/100
            initial_guess1 = [np.sqrt(2 * ls.power(frequency=best_frequency1)), best_frequency1, 0]
            from scipy.optimize import curve_fit
            popt, _ = curve_fit(sinusoidal_model, result['time0'], result['OC'], p0=initial_guess1)
            best_amplitude1, best_frequency1, best_phase1 = popt
            best_phase_normalized1 = best_phase1 % (2 * np.pi) / (2 * np.pi)

            best_fit_model1 = sinusoidal_model(time2, best_amplitude1, best_frequency1, best_phase1)
            
            popt, pcov = curve_fit(sinusoidal_model, result['time'], result['OC'], p0=initial_guess1)
            sigma = np.sqrt([pcov[0,0], pcov[1,1], pcov[2,2]])
            
            # Extract amplitude and phase from the fit
            best_amplitude1, best_frequency1, best_phase1 = popt
            best_amplitude1_err, best_frequency1_err, best_phase1_err = sigma
            print('Frequency (1/days): ' + str(best_freq_1))
            print('Frequency (cycles/day): ' + str(best_frequency1))
            print('Frequency error: ' + str(best_frequency1_err))
            period = 1/best_frequency1
            print('Period (days): ' + str(period))
            period_uncertainty = period*(best_frequency1_err/best_frequency1)
            print('Period uncertainty: ' + str(period_uncertainty))
            print('Day Division: ' + str(DayDivision))
            add = np.array ([best_freq_1, best_frequency1, best_frequency1_err, period, period_uncertainty, DayDivision]).reshape(1,6)
            df = pd.DataFrame(add, columns=['Frequency (1/days)', 'Frequency (cycles/day)', 'Frequency error', 'Period (days)', 'Period uncertainty', 'Day Division'])
            with open ('./TIC_' + str(TICNumber) + '_sec' + str(sector) + '_information.csv', 'w') as file:
                writer = csv.writer (file, lineterminator='\n')
                writer.writerow(df.columns)
                for ary in df.values:
                    writer.writerow(ary)
            def fit_funct(a, x, b):
                return a*x+b
            popt, _ = curve_fit(fit_funct, result['time0'], result['OC'])
            plt.scatter(x=result['time0'], y=result['OC'],linewidth=5)
            #plt.scatter(x=time2, y = best_fit_model1, linewidth=1)
            plt.ylim(np.min(result['OC'])-30,np.max(result['OC'])+30)
            plt.tick_params(axis='both', which='major', labelsize=20)
            plt.title('O-C result with sine curve',fontsize=20)
            #plt.xlabel("time(days)",fontsize=20)
            #plt.ylabel("O-C(s)",fontsize=20)
            plt.show()
            plot.savefig('./SavedFigs/' + 'O-C result with sine curve_' + str(TICNumber) + '_sec_' + str(sector))