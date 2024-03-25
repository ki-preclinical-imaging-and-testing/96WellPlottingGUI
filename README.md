# Description
This is a simple python GUI that can be used to interact with csv files to plot 96-well plot data

# Dependencies
This requires a pip install of the following packages:
datetime, pandas, customtkinter, matplotlib

# For a stand alone application
1. Download pyinstaller
```
pip install pyinstaller
```
2. Navigate to the 96WellPlottingGUI folder
3. In the folder, run the following

MacOS:
```
pyinstaller plotter.py --onefile --icon="icon.ico" --name 96WellPlotter
```
Windows:
```
python3 -m PyInstaller plotter.py --onefile --icon="icon.ico" --name 96WellPlotter
```

The application will be located at /dist/96WellPlotter in the 96WellPlottingGUI folder

A screenshot of the window can be seen below:

![image](https://github.com/ki-preclinical-imaging-and-testing/96WellPlottingGUI/assets/159062567/d40a63b6-ca37-4101-886a-a38f49144464)
