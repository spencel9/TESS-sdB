# Welcome to the README for a Python program designed to output observed minus calculated (O-C) figures using Transiting Exoplanet Survery Satellite (TESS) data.

## Purpose

The purpose of this program is to retrieve TESS FITS lightcurves from the [MAST StSci Website](https://mast.stsci.edu/portal/Mashup/Clients/Mast/Portal.html) for the main purpose of creating O-C figures to aid in determining the possibility of a target being a binary system. This technique is not widely used due to the increased chance of false positives, which is why there is an auxiliary branch called "Artificial Data" (this will be discussed in  the How to Use section).

## Version History

The most recent version is v2.0

### What's New in This Version

This version has updated some repetition bugs in the main branch as well as updated the plotted figures to increase readability. This version also has the inclusion of false positive identification, to greatly reduce a major issue with the pulsation timing detection method (This feature has not been extensively tested, so misidentification can occur). Additionally, a new branch has been created for the use of artificial data. This functionality was created so users of this program can upload a file of artificial data to test theories about binary system detection through pulsation timing methods.


## Installation

This program works on both Windows and Mac OS systems.

### Download Requirements

-Python (v3.11 or higher)
-All required packages (use requirements file that is avaliable for download on this GitHub repo)
-All files from this repository
-Optional: Code Editor (like VS Code, Spyder, etc.)

### How to Use Requirements File

For MacOS and Windows:

1. Open Terminal and navigate to the directory that all files from this repository was downloaded in
2. Run the following command in the terminal

'''
pip install -r requirements.txt
'''

3. Celebrate!


## How to Use

### Main Branch

1. Once you are sure that all required files are downloaded and located in the same directory, run the program either through the Terminal/Command Prompt or through a Code Editor.
2. If you have everthing in the correct place, you will be prompted in the command line to enter the TESS target designation.
   - Note: Only enter the number, NOT the TIC before the number
   - If the target cannot be found, you will be told so by the program
   - Ex: If my target was BPM 37093, I would find the TESS designation which is TIC 160522890. In the program I would only enter 160522890
3. You will then be prompted if you would like one specific sector.
   - If you only want one sector, enter the sector number
   - If you want all sectors for the target, enter 'N'
4. The terminal will then print out all sectors it found for the entered target.
5. Throughout the data analysis process, you will be prompted with other data processing questions. Most of them are fairly straightforward 
   

### Artificial Data Branch


## Additional Comments

If you have any issues with this program, please either submit an issue for this repository or contact Dr. Otani at Embry-Riddle Aeronautical University - Daytona Beach Campus.
