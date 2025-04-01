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

    def calc(self, TICNumber, sector, best_freq_1, result_og, best_freq_2, best_amplitude2, best_phase2, range_max):
        
        result_og['remove'] = 0
        
        best_freq_1 = int(best_freq_1) #######To get correct O-C

        def function(time, a, p):
            return a * np.sin(2*np.pi*(best_freq_1*time+p))
        #f=best_freq_1
        print('Frequency = ' + str(best_freq_1))
        param = [200.0, 1]
        #param = [0.472786767, 0.93167]
        with open('originals.csv', 'w') as file:
            pass
        for n in range(range_max):
            try:
                #(str(TICNumber) + '_'+ str(sector) + '_'+ str(n) +'.csv')
                file_a = './' + str(TICNumber) + '_' + str(sector) + '_'+ str(n) +'.csv'
                result = pd.read_csv(file_a, names=['time','ppt'])
                
                time=result['time']
                ppt = result['ppt']
                f = 200 ###Hard coded
                p0 = [0.0, 0.0]
                popt22, pcov22 = curve_fit(function, time, ppt, p0=p0, bounds=((-np.inf,-2*np.pi), (np.inf,2*np.pi)))
                residuals22 = ppt - function(time, *popt22)
                sigma22 = np.abs(residuals22)/100

                for j in range(0, 10):
                    popt33, pcov33 = curve_fit(function, time, ppt, p0=p0, sigma=sigma22, bounds=((-np.inf,-2*np.pi), (np.inf,2*np.pi)))
                    residuals33 = ppt - function(time, *popt33)
                    sigma33 = np.abs(residuals33)/100
                    #print(sigma)
                    p0 = popt33 # Use current fit as next initial guess
                    j+=1

                #sigma = np.sqrt([pcov[0,0], pcov[1,1]])

                print(n)
                uncertainty33 = np.sqrt([pcov33[0,0], pcov33[1,1]])
                a = popt33[0]
                print(a)
                a_err = uncertainty33[0]
                print(a_err)
                p = popt33[1]
                print(p)
                p_err = uncertainty33[1]
                print(p_err)
                print()

                t = np.mean(time)
                add = np.array ([n, t, f, a, a_err, p, p_err]).reshape(1,7)
                df = pd.DataFrame(add, columns=['n', 'time', 'frequency', 'amp', 'amp_err', 'phase', 'phase_err'])
                with open ('./originals.csv', 'a') as file:
                    writer = csv.writer (file, lineterminator='\n')
                    for ary in df.values:
                        writer.writerow(ary)
                n+=1
            except ValueError:
                print(n)
                print('Error occured, no data at this point.')
                n+=1
                print()
        print(best_freq_1)
        print(best_freq_2)
    # return popt33, pcov33
                


                        
class plotting:    
    def gettingPlots(self, a, TICNumber, sector, best_freq_1, DayDivision, result_og, best_freq_2, best_amplitude2, best_phase2):
        

        sine_curve_input = input('Would you like a reference sine curve on the O-C Diagram (y/n)? ')
        while(sine_curve_input != 'n' and sine_curve_input != 'y' and sine_curve_input != 'N' and sine_curve_input != 'Y'):
            sine_curve_input = input('Entered value for the sine curve was not n or y, please try again. ')
        
        linear_fit = input('Would you like a linear fit removal (y/n)?')
        while(linear_fit != 'n' and linear_fit != 'y' and linear_fit != 'N' and linear_fit != 'Y'):
            linear_fit = input('Entered value for linear fit removal was not n or y, please try again. ')
       
        result = pd.read_csv('originals.csv', names=['n', 'time', 'frequency', 'amp', 'amp_err', 'phase', 'phase_err'])
       

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
            params = curve_fit(fit_funct, result['time0'], result['OC'], absolute_sigma=True)
            [a,b] = params[0]
            fit_remove = fit_funct(a, result['time0'], b)
            new_result = result['OC'] - fit_remove



            ls = LombScargle(result['time0'], new_result, result['OC_err']) 
            def sinusoidal_model(t, A, omega, phi):
                return A * np.sin(2 * np.pi * omega * t + phi)
            ls1 = LombScargle(result['time'], new_result, result['OC_err'])
            frequency1, power1 = ls1.autopower(nyquist_factor=1)
                                            
            # Get the best frequency from the Lomb-Scargle periodogram
            time = result['time']
            #ppt =
            # popt, pcov = curve_fit(function, time, ppt, p0=p0, bounds=((-np.inf,-2*np.pi), (np.inf,2*np.pi)))
            # residuals = ppt - function(time, *popt)
            # sigma = np.abs(residuals)/100
                
            
            # for i in range(10):  # Iterate a few times
            #     popt, pcov = curve_fit(function, time, ppt, p0=p0, sigma=sigma, bounds=((-np.inf,-2*np.pi), (np.inf,2*np.pi)))
            #     residuals = ppt - function(time, *popt)
            #     sigma = np.abs(residuals)/100
            #     #print(sigma)
            #     p0 = popt # Use current fit as next initial guess
            #     #print(p0)


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
            print('Amplitude: ' + str(best_amplitude1))
            print('Amplitude Error: ' + str(best_amplitude1_err))
            
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
            
            print('Ha')

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
            
            popt, pcov = curve_fit(sinusoidal_model, result['time'], result['OC'], p0=initial_guess1, absolute_sigma=True)
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
            print('Amplitude: ' + str(best_amplitude1))
            print('Amplitude Error: ' + str(best_amplitude1_err))

            add = np.array ([best_freq_1, best_frequency1, best_frequency1_err, period, period_uncertainty, DayDivision]).reshape(1,6)
            df = pd.DataFrame(add, columns=['Frequency (1/days)', 'Frequency (cycles/day)', 'Frequency error', 'Period (days)', 'Period uncertainty', 'Day Division'])
            with open ('./TIC_' + str(TICNumber) + '_sec' + str(sector) + '_information.csv', 'w') as file:
                writer = csv.writer (file, lineterminator='\n')
                writer.writerow(df.columns)
                for ary in df.values:
                    writer.writerow(ary)
            def fit_funct(a, x, b):
                return a*x+b
            popt188, _ = curve_fit(fit_funct, result['time0'], result['OC'])
            #plt.scatter(x=result['time0'], y=result['OC'],linewidth=5)
            plt.scatter(x=time2, y = best_fit_model1, linewidth=1)
            plt.ylim(np.min(result['OC'])-30,np.max(result['OC'])+30)
            plt.tick_params(axis='both', which='major', labelsize=20)
            plt.title('O-C result with sine curve',fontsize=20)
            #plt.xlabel("time(days)",fontsize=20)
            #plt.ylabel("O-C(s)",fontsize=20)
            #plt.scatter(x=result['time0'], y = result['amp'], linewidth = 5)
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

            
            popt255, pcov = curve_fit(sinusoidal_model, result['time'], new_result, p0=initial_guess1, absolute_sigma=True)
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
            print('Amplitude: ' + str(best_amplitude1))
            print('Amplitude Error: ' + str(best_amplitude1_err))
            
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
            #plt.scatter(x=result['time0'], y = result['amp'], linewidth = 5)
            plt.show()
            plot.savefig('./SavedFigs/' + 'O-C result_' + str(TICNumber) + '_sec_' + str(sector))
        else: #No sine curve and no line


            result_noAdd = pd.read_csv('originals.csv', names=['n', 'time', 'frequency', 'amp', 'amp_err', 'phase', 'phase_err'])  
            
            result_noAdd['time0']= result_noAdd['time']-result_noAdd['time'][0]
            result_noAdd['O']= 86400*result_noAdd['phase']/result_noAdd['frequency']
            result_noAdd['C']=np.mean(result_noAdd['O'])
            result_noAdd['OC']=result_noAdd['O']-result_noAdd['C']
            result_noAdd['OC_err']=86400*result_noAdd['phase_err']/result_noAdd['frequency']

            plot = plt.figure(figsize=(15,5))
            plt.errorbar(x=result_noAdd['time0'], y=result_noAdd['OC'], yerr=result_noAdd['OC_err'], fmt='bo')
            plt.scatter(x=result_noAdd['time0'], y=result_noAdd['OC'])
            #plt.ylim(np.min(result['OC'])-20,np.max(result['OC'])+20)
            plt.tick_params(axis='both', which='major', labelsize=20)
            plt.title('O-C result',fontsize=20)
            plt.xlabel("time(days)",fontsize=20)
            plt.ylabel("O-C(s)",fontsize=20)
            plt.axhline(y = 0.0, color = 'k', linestyle = '-')
            plt.ylim(-30,30)
            plt.show()
            plot.savefig('./SavedFigs/' + 'ATEST O-C result with sine curve_' + str(TICNumber) + '_sec_' + str(sector))

    


            # result = pd.read_csv('originals.csv', names=['n', 'time', 'frequency', 'amp', 'amp_err', 'phase', 'phase_err'])

            # result['phase'] = pd.to_numeric(result['phase'], errors='coerce')
            # result['frequency'] = pd.to_numeric(result['frequency'], errors='coerce')


            # result['time0']= result['time']-result['time'][0]
            # result['O']= 86400*result['phase']/result['frequency']
            # result['C']=np.mean(result['O'])
            # result['OC']=result['C']-result['O']
            # result['OC_err']=86400*result['phase_err']/result['frequency']
            
            # plot = plt.figure(figsize=(15,8))
            # plt.errorbar(x=result['time0'], y=result['OC'], yerr=result['OC_err'], fmt='bo')
            # #filtered_x = [x for x, y in zip(result['time0'], result['OC']) if y !=0]
            # #filtered_y = [y for y in result['OC'] if y != 0]
            # plt.scatter(x=result['time0'], y=result['OC'], facecolor='peachpuff')
            # #plt.plot(result['time0'],result['OC'], linestyle='-', color='blue')
            # #plt.ylim(np.min(result['OC'])-30,np.max(result['OC'])+30)
            # #plt.tick_params(axis='both', which='major', labelsize=20)
            # #plt.title('O-C result',fontsize=20)
            # plt.xlabel("time(days)",fontsize=20)
            # plt.ylabel("O-C(s)",fontsize=20)
            
            # ls1 = LombScargle(result['time'], result['OC'], result['OC_err'])
            # #if you receive errors, you can set minimum and maximum frequencies.
            # #frequency1, power1 = ls1.autopower(minimum_frequency = 1, maximum_frequency=500)#(nyquist_factor=1)maximum_frequency=500)
            # frequency1, power1 = ls1.autopower(nyquist_factor=1)
                                            
            # # Get the best frequency from the Lomb-Scargle periodogram
            # best_frequency1 = frequency1[np.argmax(power1)]
            # # ls = LombScargle(result['time0'], result['OC'], result['OC_err'])     
            # # def sinusoidal_model(t, A, omega, phi):
            # #     return A * np.sin(2 * np.pi * omega * t + phi)
            # # last_index = len(result) - 1 
            # # time2 = np.arange(result['time'][last_index])/100
            # #initial_guess1 = [np.sqrt(2 * ls.power(frequency=best_frequency1)), best_frequency1, 0]



            # # from scipy.optimize import curve_fit
            # # popt, _ = curve_fit(sinusoidal_model, result['time0'], result['OC'], p0=initial_guess1)
            # # best_amplitude1, best_frequency1, best_phase1 = popt
            # # best_phase_normalized1 = best_phase1 % (2 * np.pi) / (2 * np.pi)

            # # best_fit_model1 = sinusoidal_model(time2, best_amplitude1, best_frequency1, best_phase1)
            
            # # popt, pcov = curve_fit(sinusoidal_model, result['time'], result['OC'], p0=initial_guess1, absolute_sigma=True)
            # # sigma = np.sqrt([pcov[0,0], pcov[1,1], pcov[2,2]])

            # def function_fit(time, a, p):
            #     return a*np.sin(2*np.pi*best_frequency1*time+p) ######## can sub for just frequency1

            # med1 = np.median(result_og.pdcsap_flux)
            # result_og['FLUX_norm'] = (result_og['pdcsap_flux']/med1) - 1
            # ppt=result_og['FLUX_norm']*1000

            # time = result_og['time']
            # p0 = [0.0,0.0]

            # from scipy.optimize import curve_fit
            # popt77, pcov = curve_fit(function_fit, time, ppt, p0=p0, bounds=((-np.inf,-2*np.pi), (np.inf,2*np.pi)))
            # residuals77 = ppt - function_fit(time, *popt77)
            # sigma77 = np.abs(residuals77)/100
                
            
            # for i in range(10):  # Iterate a few times
            #     from scipy.optimize import curve_fit
            #     popt66, pcov66 = curve_fit(function_fit, time, ppt, p0=p0, sigma=sigma77, bounds=((-np.inf,-2*np.pi), (np.inf,2*np.pi)))
            #     residuals66 = ppt - function_fit(time, *popt66)
            #     sigma66 = np.abs(residuals66)/100
            #     #print(sigma)
            #     p0 = popt66 # Use current fit as next initial guess
            #     #print(p0)

            # popt255, pcov = curve_fit(sinusoidal_model, result['time'], new_result, p0=initial_guess1)
            # sigma24 = np.sqrt([pcov[0,0], pcov[1,1], pcov[2,2]])

            # # # Extract amplitude and phase from the fit
            # best_amplitude1_err = np.min(result_noAdd['amp_err'])
            # best_frequency1_err = np.min(result_noAdd['amp_err'])
            # best_freq_1 = np.argmax(result_noAdd['frequency']) #This should be correct???
            # print('Frequency (1/days): ' + str(best_freq_1))
            # #print('Frequency (cycles/day): ' + str(best_frequency1))
            # #print('Frequency error: ' + str(best_frequency1_err))
            # period = 1/best_freq_1
            # print('Period (days): ' + str(period))
            # #period_uncertainty = period*(best_frequency1_err/best_frequency1)
            # #print('Period uncertainty: ' + str(period_uncertainty))
            # best_amplitude1 = np.argmax(result_noAdd['amp'])
            # best_amplitude1_err = np.argmax(result_noAdd['amp_err'])
            # print('Amplitude: ' + str(best_amplitude1))
            # print('Amplitude Error: ' + str(best_amplitude1_err))

            # best_phase_noAdd = np.argmax(result_noAdd['phase'])
            # best_phase_noAdd_err = np.argmax(result_noAdd['phase_err'])
            # print('Phase: ' + str(best_phase_noAdd))
            # print('Phase Error: ' + str(best_phase_noAdd_err))
            
            # add = np.array ([best_freq_1, best_frequency1, best_frequency1_err, period, period_uncertainty, DayDivision]).reshape(1,6)
            # df = pd.DataFrame(add, columns=['Frequency (1/days)', 'Frequency (cycles/day)', 'Frequency error', 'Period (days)', 'Period uncertainty', 'Day Division'])
            # with open ('./TIC_' + str(TICNumber) + '_sec' + str(sector) + '_information.csv', 'w') as file:
            #     writer = csv.writer (file, lineterminator='\n')
            #     writer.writerow(df.columns)
            #     for ary in df.values:
            #         writer.writerow(ary)
            # # def fit_funct(a, x, b):
            # #     return a*x+b
            # # popt, _ = curve_fit(fit_funct, result['time0'], result['OC'])
            # plt.scatter(x=result['time0'], y=result['OC'],linewidth=5)
            # #plt.scatter(x=time2, y = best_fit_model1, linewidth=1)
            # plt.ylim(np.min(result['OC'])-30,np.max(result['OC'])+30)
            # plt.tick_params(axis='both', which='major', labelsize=20)
            # plt.title('O-C result with sine curve',fontsize=20)
            # #plt.xlabel("time(days)",fontsize=20)
            # #plt.ylabel("O-C(s)",fontsize=20)
            # #plt.scatter(x=result['time0'], y = result['amp'], linewidth = 5)


            # plt.show()
            # plot.savefig('./SavedFigs/' + 'O-C result with sine curve_' + str(TICNumber) + '_sec_' + str(sector))

