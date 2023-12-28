import pandas as pd
import numpy as np
import csv 
import fnmatch #this is for reading file from directory
import os #this is for reading file from directory
import matplotlib.pyplot as plt
import math

class FindingFileAndDivide:
    def findfile(self, csv_filename):
        for file in os.listdir('./MainSectors'):
            if fnmatch.fnmatch(file, csv_filename):
                print(file)
                csv_filename = file
    
    def DivideWithFile(self, a, csv_filename, DayDivision, TICNumber, sector, best_freq_1, best_freq_2):
        result = pd.read_csv(csv_filename, names=['BJD','FLUX_norm']) 
        BJD0 = result.BJD.min()

        n = 0
        for n in range(150):
            
            width = DayDivision #days

            BJD1 = BJD0+width*n
            BJD2 = BJD1+width
            result_f1 = result[result['BJD']>=BJD1] 
            result_f2 = result_f1[result_f1['BJD']<=BJD2] 
            result_f3 = pd.DataFrame({'BJD':result_f2.BJD, 'FLUX':result_f2.FLUX_norm}) ### get only the info you want 
            
            save_dir = './SavedData/'
            os.makedirs(save_dir, exist_ok=True)
            csv_filename_f = (str(TICNumber) + '_'+ str(sector) + '_'+ str(n) +'.csv')
            

            save_dir = './SavedData/'
            text_filename_f = (str(TICNumber) + '_'+ str(sector) + '_'+ str(n) +'.txt')
            

            
            result_f3.to_csv(csv_filename_f, index = False, header = False)
            with open(csv_filename_f, 'r') as inp, open(text_filename_f, 'w') as out:
                for line in inp:
                    line = line.replace(',', '\t')
                    out.write(line)

            BJD = np.mean(result_f3['BJD'])+2457000
            

            add = np.array ([sector, n, BJD]).reshape(1,3)
            df = pd.DataFrame(add, columns=['sec', 'number', 'BJD'])
            with open ('./bjd.csv', 'a') as f:
                writer = csv.writer (f, lineterminator='\n')
                for ary in df.values:
                    writer.writerow(ary)
            n=+1