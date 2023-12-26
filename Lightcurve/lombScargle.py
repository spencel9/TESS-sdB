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
        
        frequency, power = LombScargle(result.time, result.FLUX_norm, dy).autopower(nyquist_factor=1)
        # Create a new figure for each plot
        plt.figure()  

        # Plotting the periodogram
        plt.plot(frequency, power)
        plt.title('Periodogram 1')
        plt.xlabel('Frequency')
        plt.ylabel('Power')

        save_dir = './SavedFigs'
        fileName = f'Periodogram1_{TICNumber}_sec_{sector}.png'
        plt.savefig(os.path.join(save_dir, fileName))

        #plt.show()

        best_frequency_1 = frequency[np.argmax(power)]
        return best_frequency_1

class PeriodogramCertTimeRange:
    
    result12 = Combining_1_and_2()
    TICNum = GatheringData()
    resultObj = GettingResultTable()
    
    def periodogram(self, result, best_frequency_1, bounds, TICNumber, sector):
        DayDivision = 0.1
        while DayDivision != 10:
            time1 = bounds[0].btjd
            time2 = time1 + DayDivision
           
            result_subset = result[(result['time'] >= time1) & (result['time'] <= time2)]
            dy = 0.1  
            # Your list here

            if (len(result_subset.time) & len(result_subset.FLUX_norm)) == 0:
                print("The list is empty.")
                DayDivision += 0.5

            else:
                print("The list is not empty.")
                frequency_2, power_2 = LombScargle(result_subset.time, result_subset.FLUX_norm, dy).autopower(nyquist_factor=1)
                
                # Create a new figure for each plot
                plt.figure()  

                # Plotting the periodogram
                plt.plot(frequency_2, power_2)
                plt.title('Periodogram 2')
                plt.xlabel('Frequency')
                plt.ylabel('Power')

                save_dir = './SavedFigs'
                fileName = f'Periodogram2_{TICNumber}_sec_{sector}_{DayDivision}.png'
                plt.savefig(os.path.join(save_dir, fileName))

                #plt.show()
                best_frequency_2 = frequency_2[np.argmax(power_2)]    
                if math.isclose(best_frequency_2, best_frequency_1, rel_tol=1):
                    print('Divide by ' + str(DayDivision) + ' days')
                    break
                else:
                    print('Cannot be divided by ' + str(DayDivision) + ' days (10 is max)')
                    DayDivision += 0.5

            
        return DayDivision, best_frequency_2

            