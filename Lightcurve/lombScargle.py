import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from astropy.timeseries import LombScargle
import math
import os

from .lightcurve import Combining_1_and_2
from .lightcurve import GatheringData
from .lightcurve import GettingResultTable

class Periodogram:
   
    result12 = Combining_1_and_2()
    TICNum = GatheringData()
    resultObj = GettingResultTable()
   
    def periodogram(self, n, result, TICNumber, sector):
        dy = 0.1
        #result['FLUX_norm'] = result['FLUX_norm'].replace(0, 0.00001)


        fig = plt.figure(figsize=(15,8))
        plt.scatter(result['time'], result['pdcsap_flux']) ##was FLUX_norm for splitting and recombo
        plt.show()
        #plt.savefig('./DetectBinary/Lightcurve/testFig.png')

        # frequency, power = LombScargle(result.time, result.FLUX_norm, dy).autopower(nyquist_factor=1)
        frequency, power = LombScargle(result.time, result.pdcsap_flux, dy).autopower(nyquist_factor=1)

        # Create a new figure for each plot
        plt.figure()  

        # Plotting the periodogram
        plt.plot(frequency, power)
        plt.title('Periodogram 1 from ' + str(TICNumber))
        plt.xlabel('Frequency')
        plt.ylabel('Power')

        save_dir = './SavedFigs'
        fileName = f'Periodogram1_{TICNumber}_sec_{sector}.png'
        plt.savefig(os.path.join(save_dir, fileName))

        #plt.show()

        best_frequency_1 = frequency[np.argmax(power)]

        half_max_power = max(power) / 2.0
        indices = np.where(power > half_max_power)[0]
        left_index = indices[0]
        right_index = indices[-1]
        fwhm = frequency[right_index] - frequency[left_index]
        print(fwhm)

        return best_frequency_1, fwhm

class PeriodogramCertTimeRange:
    
    result12 = Combining_1_and_2()
    TICNum = GatheringData()
    resultObj = GettingResultTable()
    
    def periodogram(self, result, best_frequency_1, bounds, TICNumber, sector):
        DayDivision = 0.1
        # time1 = bounds[0].btjd
        time1 = bounds[0]
        time2 = time1 + DayDivision

        def sinusoidal_model(t, A, omega, phi):
                return A * np.sin(2 * np.pi * omega * t + phi)


        while DayDivision != 10:
            time1=time1
            time2=time1+DayDivision
           
            result_subset = result[(result['time'] >= time1) & (result['time'] <= time2)]
            dy = 0.1  
            # Your list here

            if (len(result_subset.time) & len(result_subset.pdcsap_flux))== 0: ####Was FLUX_norm
                print("The list is empty.")
                time1=time2
                time2=time1+DayDivision
                #DayDivision += 0.5

            else:
                print("The list is not empty.")

                ls2 = LombScargle(result_subset['time'], result_subset['pdcsap_flux']) ######Was FLUX_norm
                frequency2, power2 = ls2.autopower(nyquist_factor=1, samples_per_peak=20)
                                                
                # Get the best frequency from the Lomb-Scargle periodogram
                best_frequency2 = frequency2[np.argmax(power2)]

                # Initial guesses for amplitude and phase
                initial_guess2 = [np.sqrt(2 * ls2.power(frequency=best_frequency2)), best_frequency2, 0]

                # Fit the sinusoidal model to the data using least squares
                from scipy.optimize import curve_fit
                popt, _ = curve_fit(sinusoidal_model, result_subset['time'], result_subset['pdcsap_flux'], p0=initial_guess2, maxfev = 20000)

                # Extract amplitude and phase from the fit
                best_amplitude2, best_frequency2, best_phase2 = popt

                # Normalize the phase to the range [0, 1]
                best_phase_normalized2 = best_phase2 % (2 * np.pi) / (2 * np.pi) 

                # frequency_2, power_2 = LombScargle(result_subset.time, result_subset.pdcsap_flux, dy).autopower(nyquist_factor=1) ##Was FLUX_norm
                
                # Create a new figure for each plot
                plt.figure()  

                # Plotting the periodogram
                plt.plot(frequency2, power2)
                plt.title('Periodogram 2 of ' + str(TICNumber))
                plt.xlabel('Frequency')
                plt.ylabel('Power')

                save_dir = './SavedFigs'
                fileName = f'Periodogram2_{TICNumber}_sec_{sector}_{DayDivision}.png'
                plt.savefig(os.path.join(save_dir, fileName))


  
                if math.isclose(best_frequency2, best_frequency_1, rel_tol=0.005):
                    print('Divide by ' + str(DayDivision) + ' days')
                    break
                else:
                    print('Cannot be divided by ' + str(DayDivision) + ' days (10 is max)')
                    DayDivision += 0.1
            #distance tolerance = propaged uncert of f = 1/p
        
    
              
            
        return DayDivision, best_frequency2, best_amplitude2, best_phase2