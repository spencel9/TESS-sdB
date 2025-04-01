import numpy as np
import math
import matplotlib.pyplot as plt
import lightkurve as lk
import pandas as pd
import csv
from scipy.optimize import curve_fit
import os

#Uncomment following code block to create new csv for specific target
####################################################################################
#Target = 'TIC 220573709' 

# ExposureTime = 20
# DownloadableFiles = lk.search_lightcurve(target = Target, exptime = ExposureTime)
# lc_collection = DownloadableFiles.download_all()

# Lc_all = lc_collection.stitch()
# Result = Lc_all.to_pandas()
# Result = Result.reset_index()
# Result.to_csv('TESS_data.csv')
# print(Result)
####################################################################################

#This csv was made for TIC 220573709
##########Mass comment out with cmd+/
# ExposureTime = 20
# DownloadableFiles = lk.search_lightcurve(target = Target, exptime = ExposureTime)
# #print(DownloadableFiles)
# lc_collection = DownloadableFiles.download_all()
# #print(type(lc_collection))
# Lc_all = lc_collection.stitch()
# fileView = Lc_all.to_pandas()
# fileView.to_csv('./TESS_data2.csv')

delta_f=10
f1=200.0
# #

f2=f1-delta_f*0.01
# f3=f1+delta_f*0.01

print('f2=',f2)
print('f1=',f1)
# print('f3=',f3)

ratio_a = 3
a1=1
# a2=a1
# a3=a1

a2=a1*ratio_a*0.1
# a3=a1*ratio_a*0.1

print('a2=',a2)
print('a1=',a1)
#print('a3=',a3)

delta_ph = 0
ph1=0
ph2=0
# ph3=0

print('ph2=',ph2)
print('ph1=',ph1)
#print('ph3=',ph3)

#step=20/86400=0.0002314814814814815
d=np.linspace(0,60,num=259200)

s1=a1*np.sin(2*np.pi*f1*d+ph1)
s2=a2*np.sin(2*np.pi*f2*d+ph2)
#s3=a3*np.sin(2*np.pi*f3*d+ph3)

s=s1+s2#+s3

print(d)

print()

print(s)

print()

all=np.column_stack((d,s))


np.savetxt('./Lightcurve/test.csv', all, delimiter=',')
Result = pd.read_csv('./Lightcurve/test.csv', names= ['time', 'flux'])

time = Result['time']
flux = Result['flux']

print(time)

print()
print(flux)
# time_min = Result['time'].min()
# time_max = Result['time'].max()
# print("Time min: " + str(time_min))
# print("Time max: " + str(time_max))
# time_change = Result['time'][2] - time_min
# print("Time change for 20s: " + str(time_change))

#Hard coded for TIC 220573709
#freq = 1544.5325347326557
#freq = 1544.5325347326557 ###To create beating freqeuncy

# mean = np.mean(Result['pdcsap_flux'])
# sd = np.std(Result['pdcsap_flux'])
# range = 4 * sd
# a = mean + range
# b = mean - range
# Result = Result[Result['pdcsap_flux'] <= a]
# Result = Result[Result['pdcsap_flux'] >= b]
# #Result.plot.scatter(x = 'time', y = 'pdcsap_flux')
# med1 = np.median(Result.pdcsap_flux)
# Result['FLUX_norm'] = (Result['pdcsap_flux']/med1) - 1
# Result['ppt']=Result['FLUX_norm']*1000
# print("ppt val: " + str(Result['ppt']))
# a = 50
# p = 0
# dayDivision = 0.5 #units of days

#Result.to_csv('Result.csv')

# def waveFunct(time_vals, a, p, freq):
#     return a * np.sin(2*np.pi*(freq*time_vals+p))

#time_vals = np.arange(0.0, 27, 0.00001389)  #Hour worth of data, with 20 second divisions 0.0417, 0.00001389
# y = np.zeros_like(time_vals)  
# y = waveFunct(time_vals, a, p, freq)

# Ensure all values are non-zero by adding a small offset
# offset = 1e-6  # Small positive value to ensure no zeros
# y += offset

# Parameters for the noise
noise_level = 0.1  # Standard deviation of the Gaussian noise

# Add Gaussian noise
noise = np.random.normal(0, noise_level, flux.shape)  # mean=0, std_dev=noise_level, same shape as data
flux_noise = flux + noise

#######################################

# Add noise to the original data
noisy_data = flux_noise ################## might cause issues with y

#new_time_vals = time_vals  + 2460618.5

# plt.scatter(new_time_vals, noisy_data)
# plt.show()
# plt.savefig('FakeDataPlot2.png')
# plt.close()

bananas = pd.DataFrame({'pdcsap_flux':noisy_data, 'time':time})
#Result['y'] = y
#Result['time_range'] = time_vals

bananas.to_csv('./Lightcurve/trial200_new.csv')

# fig = plt.figure(figsize=(15,8))
# plt.scatter(bananas['time'], bananas['pdcsap_flux'])
# plt.show()

# freq = 1544.6325347326557 ###To create beating freqeuncy

# mean = np.mean(Result['pdcsap_flux'])
# sd = np.std(Result['pdcsap_flux'])
# range = 4 * sd
# a = mean + range
# b = mean - range
# Result = Result[Result['pdcsap_flux'] <= a]
# Result = Result[Result['pdcsap_flux'] >= b]
# #Result.plot.scatter(x = 'time', y = 'pdcsap_flux')
# med1 = np.median(Result.pdcsap_flux)
# Result['FLUX_norm'] = (Result['pdcsap_flux']/med1) - 1
# Result['ppt']=Result['FLUX_norm']*1000
# print("ppt val: " + str(Result['ppt']))
# a = 200
# p = 0
# dayDivision = 0.5 #units of days

# def waveFunct(time_vals, a, p, freq):
#     return a * np.sin(2*np.pi*(freq*time_vals+p))

# time_vals = np.arange(0.0, 27, 0.00001389)  #Hour worth of data, with 20 second divisions 0.0417, 0.00001389
# y = np.zeros_like(time_vals)  
# y = waveFunct(time_vals, a, p, freq)

# # offset = 1e-6  # Small positive value to ensure no zeros
# # y += offset

# noise_level = 5 * y.max()
# noise = noise_level * np.random.uniform(low=0.1, high=1, size=len(y))
# noise[noise == 0] = 1e-6

# # Add noise to the original data
# noisy_data = y + noise

# new_time_vals = time_vals  + 2460618.5

# plt.scatter(new_time_vals, noisy_data)
# plt.show()
# plt.savefig('FakeDataPlot.png')
# plt.close()

# apples = pd.DataFrame({'pdcsap_flux':noisy_data, 'time':new_time_vals})
# apples.to_csv('./trial.csv')

# oranges = pd.DataFrame(columns = ['time', 'pdcsap_flux'])
# oranges['time'] = apples['time'] 
# oranges['pdcsap_flux'] = apples['pdcsap_flux'] + bananas['pdcsap_flux']

# oranges.to_csv('trial33.csv')
# oranges.to_csv('trial33.txt', sep='\t', index=False)
""" z = np.int64(0)

Result['BJD'] = Result['time']
BJD0 = Result['BJD'].min() #Results does not have BJD attribute lol
del range
for z in range(0, 50, 1):
    width = dayDivision #days
    BJD1 = BJD0+width*z
    BJD2 = BJD1+width
    result_f1 = Result[Result['BJD']>=BJD1] 
    result_f2 = result_f1[result_f1['BJD']<=BJD2] 
    result_f3 = pd.DataFrame({'BJD':result_f2['BJD'], 'FLUX':result_f2['FLUX_norm']}) ### get only the info you want 

    BJD = np.mean(result_f3['BJD'])+2457000
# Fill y values using the function

plt.scatter(Result['time'], BJD)
plt.show()
plt.savefig('AfterBJD.png')
plt.close() """



# param = [0.472786767, 0.93167]
# with open('originals.csv', 'w') as file:
#     pass
# for n in range(len(Result)):
#     try:
        
#         time=Result['time']
#         #print('Time: ', time)
        
#         ppt = Result['ppt']
#         #print('PPT' , ppt)
#         f = freq
#         bounds = ([0.0, 0.0], [100.0, 1.0])
#         popt, pcov = curve_fit(function, time, ppt, bounds=bounds)
        
#         sigma = np.sqrt([pcov[0,0], pcov[1,1]])

#         print(n)
#         a = popt[0]
#         print(a)
#         a_err = sigma[0]
#         print(a_err)
#         p = popt[1]
#         print(p)
#         p_err = sigma[1]
#         print(p_err)
#         print()

#         t = np.mean(time)
#         add = np.array ([n, t, f, a, a_err, p, p_err]).reshape(1,7)
#         df = pd.DataFrame(add, columns=['n', 'time', 'frequency', 'amp', 'amp_err', 'phase', 'phase_err'])
#         with open ('./originals.csv', 'a') as file:
#             writer = csv.writer (file, lineterminator='\n')
#             for ary in df.values:
#                 writer.writerow(ary)
#     except ValueError:
#         print(n)
#         print('Error occured, no data at this point.')
#         print()
