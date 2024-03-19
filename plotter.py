# For GUI
import customtkinter as ctk
import tkinter as ogtkinter

# For analysis
import numpy as np
import pandas as pd

# For plotting
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

from datetime import datetime


def exit():
	app.destroy()

def _create_circle(self, x, y, r, **kwargs):
	return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)

ctk.CTkCanvas.create_circle = _create_circle

# Analysis Functions
def movingaverage(interval,window_size):

	# Smooths the data #

	window = np.ones(int(window_size))/float(window_size)
	return np.convolve(interval, window, 'same')

def reverse_well_lookup(wells,labels):

	# Looks up the label for a specific well #

	swapped = dict()
	for k,v in labels.items():
		for vv in v:
			swapped[vv] = k

	return [swapped[well] for well in wells if well in swapped.keys()]

def create_plot(df, labels_to_view, outcome, moving_average_bool, error_bars, included, plot1):

	# Creates a plot based on specified parameters #

	time = app.df['Time']

	legend = labels_to_view.copy()
	if moving_average_bool:
		i = [1,3,5]
		for i_0 in i:
			legend.insert(i_0,'')

	for well in labels_to_view:
		means = []
		meds = []
		stds = []
		lower_qrt = []
		upper_qrt = []
		times = []

		for i in range(0,50):
			values_to_plot = df[df['Label-Cycle']==well+'-'+str(i+1)][outcome]

			time_value = df[df['Label-Cycle']==well+'-'+str(i+1)]['Time']
			date_format = '%H:%M:%S'
			times.append(datetime.strptime(time_value.iloc[0],date_format))

			if len(included) > 0:
				for index in values_to_plot.index:
					if df['Well'][index] not in included:
						values_to_plot = values_to_plot.drop(index=index)


			means.append(values_to_plot.mean())
			meds.append(values_to_plot.median())

			if len(values_to_plot)>1:
				stds.append(values_to_plot.std())
				lower_qrt.append(values_to_plot.quantile(q=0.25))
				upper_qrt.append(values_to_plot.quantile(q=0.75))
			else:
				stds.append(0)
				lower_qrt.append(values_to_plot.median())
				upper_qrt.append(values_to_plot.median())

		y_avg = movingaverage(means,5)
		if moving_average_bool:
			plot1.plot(times[2:-2],y_avg[2:-2], label=well)
		else:
			#plot1.scatter(range(0,50),means,label=well)
			plot1.scatter(times,means,label=well)
		if error_bars:
			if not moving_average_bool:
				plot1.errorbar(times, means, yerr=np.array(stds))
			else:
				lower = movingaverage(np.array(means) - np.array(stds),5)
				upper = movingaverage(np.array(means) + np.array(stds),5)
				plot1.fill_between(times[2:-2], upper[2:-2],lower[2:-2],alpha=0.2)
				#plot1.fill_between(times, upper_qrt,lower_qrt,alpha=0.2)
				
				
		
	plot1.legend(bbox_to_anchor=(1.03, 1), loc='upper left')

def label_all_wells(df,labels):

	# Add Label and Label-Cycle to the dataframe #

	swapped = dict()
	for k,v in labels.items():
		for vv in v:
			swapped[vv] = k
	df['Label'] = df['Well'].map(swapped)
	df['Label-Cycle'] = df['Label']+'-'+df['Cycle'].astype(str)
	return df

# GUI Design Functions
def build_labels_default():

	# Build label dictionary #

    app.label_dict = dict()
    app.label_dict['Control1'] = {'B3','B4','B5','B6'}
    app.label_dict['Control2'] = {'C3','C4','C5','C6'}
    app.label_dict['Control3'] = {'D3','D4','D5','D6'}
    app.label_dict['Control4'] = {'E3','E4','E5','E6'}
    app.label_dict['Control5'] = {'F3','F4','F5','F6'}
    app.label_dict['Control6'] = {'G3','G4','G5','G6'}

    app.label_dict['SLC-OE1'] = {'B7','B8','B9','B10'}
    app.label_dict['SLC-OE2'] = {'C7','C8','C9','C10'}
    app.label_dict['SLC-OE3'] = {'D7','D8','D9','D10'}
    app.label_dict['SLC-OE4'] = {'E7','E8','E9','E10'}
    app.label_dict['SLC-OE5'] = {'F7','F8','F9','F10'}
    app.label_dict['SLC-OE6'] = {'G7','G8','G9','G10'}

    app.label_dict['H20'] = {'B2','C2','D2','B11','C11','D11'}
    app.label_dict['MG132'] = {'E2','F2','G2','E11','F11','G11'}

def Build96Wells(canvas):

	# Draw the 96 well figure that can select wells #

	y_vals = np.linspace(15,185,8)
	y_alphavals = ['A','B','C','D','E','F','G']
	x_vals = np.linspace(30,270,12)
	canvas.create_rectangle(10,5,300,200)

	app.label_color_dict = dict()
	ref_colors = plt.get_cmap('tab20')

	# Give each label a color
	for i,label in enumerate(app.label_dict.keys()):
		if i <= 10:
			app.label_color_dict[label] = ref_colors(i*2)
		else:
			app.label_color_dict[label] = ref_colors((i - 10)*2-1)

	# Color in a square around each well based on the color
	width = (x_vals[1]-x_vals[0])/2
	height = (y_vals[1]-y_vals[0])/2

	for i,x in enumerate(x_vals):
		for y,alphay in zip(y_vals,y_alphavals):
			label_to_do = reverse_well_lookup([alphay+str(i+1)],app.label_dict)
			if label_to_do:
				color_full = app.label_color_dict[label_to_do[0]]
				
				hexcolor = "#{:02x}{:02x}{:02x}".format(int(255*color_full[0]),int(255*color_full[1]),int(255*color_full[2]))
				canvas.create_rectangle(x-width,y-height, x+width,y+height, fill = hexcolor, outline='')

	# Draw a circle for the well
	for x in x_vals:
		for y in y_vals:
			canvas.create_circle(x,y,5, fill='black',outline='white')

	# Make it react to being clicked
	canvas.bind('<ButtonRelease-1>',LabelWell)

	# Add a Label
	title_label = ctk.CTkLabel(master = image_frame,text='Select Wells to View')
	title_label.configure(font=('Helvetica',20))
	title_label.place(relx=0.4, rely=0.1, anchor='center')

def get_y_axis_options():

	# Add buttons for y-axis data like smoothing and error bars #

	app.viewing = ctk.StringVar(value = '')
	options = [column for column in app.df.columns]
	drop = ctk.CTkOptionMenu(master=plot_frame,variable=app.viewing,values=options)
	drop.configure(width=200)
	drop.place(relx=0.2, rely=0.05, anchor='center')

	smooth_button = ctk.CTkCheckBox(master=plot_frame, text='Moving Average',
		variable=app.smooth_data, onvalue='on', offvalue='off')
	error_bars_button = ctk.CTkCheckBox(master=plot_frame, text='Error Bars',
		variable=app.error_bars, onvalue='on', offvalue='off')

	smooth_button.place(relx=0.5, rely=0.05, anchor='center')
	error_bars_button.place(relx=0.7,rely=0.05,anchor='center')

# GUI Interactive Functions
def LabelWell(event):

	# Turn well on or off #

	y_vals = np.linspace(15,185,8)
	x_vals = np.linspace(30,270,12)
	y_alphavals = 'ABCDEFG'
	index_minx = np.argmin(abs(x_vals - event.x))
	index_miny = np.argmin(abs(y_vals - event.y))

	# Find the well where you clicked
	well = y_alphavals[index_miny]+str(index_minx+1)

	# Change its color to show and add it to the list "visualized wells"
	if well not in app.visualized_wells:
		app.visualized_wells.append(well)
		WellLabeler.create_circle(x_vals[index_minx],y_vals[index_miny],5,fill='white')
	else:
		app.visualized_wells.remove(well)
		WellLabeler.create_circle(x_vals[index_minx],y_vals[index_miny],5,fill='black')

def ChooseGroup():

	# Choose y-axis measurement to plot #

	group = LabelList.get(LabelList.curselection())
	wells = app.label_dict[group]
	y_vals = np.linspace(15,185,8)
	x_vals = np.linspace(30,270,12)
	for well in wells:
		index_x = int(well[1:])-1
		index_y = 'ABCDEFG'.index(well[0])
		if well not in app.visualized_wells:
			app.visualized_wells.append(well)
			WellLabeler.create_circle(x_vals[index_x],y_vals[index_y],5,fill='white')
		else:
			app.visualized_wells.remove(well)
			WellLabeler.create_circle(x_vals[index_x],y_vals[index_y],5,fill='black')

def GetDataPath():

	# Upload CSV file #

	path = ctk.filedialog.askopenfilename()
	app.df = pd.read_csv(path)
	app.df = label_all_wells(app.df,app.label_dict)
	get_y_axis_options()

def DisplayPlot():

	# Redraw the plot with current selections #

	fig = Figure(figsize=(7,5),dpi=100)
	plt.style.use('dark_background')
	plot1 = fig.add_subplot(111)

	if hasattr(app,'df'):

		labels_to_view = reverse_well_lookup(app.visualized_wells,app.label_dict)
		labels_to_view = list(set(labels_to_view))
		outcome = app.viewing.get()
		moving_average_bool = (app.smooth_data.get() == 'on')
		error_bars = (app.error_bars.get() == 'on')
		included = app.visualized_wells
		y_lims = [np.round(app.df[outcome].min()*0.95,2),np.round(app.df[outcome].max()*1.05,2)]
		myFmt = mdates.DateFormatter('%H:%M')

		create_plot(app.df,labels_to_view,outcome,moving_average_bool,error_bars,included,plot1)

		plot1.xaxis.set_major_formatter(myFmt)
		plot1.set_title(outcome)
		plot1.set_xlabel('Time (Hours:Min)')
		plot1.set_ylim(y_lims)

		fig.tight_layout()
	else:
		outcome = 'Random Plot'
		y = [0,4,5,3,7,6,8,1,2,3,4,2,1]
		plot1.scatter(range(0,len(y)),y)
		plot1.set_title(outcome)

	canvas = FigureCanvasTkAgg(fig, master = plot_frame)
	canvas.draw()
	canvas.get_tk_widget().place(relx = 0.5, rely = 0.5, anchor='center')

app = ctk.CTk()
ctk.set_appearance_mode("dark")

app.title('Data Visualizer')
app.geometry('1200x900')

app.visualized_wells = []
app.excluded = []
app.smooth_data = ctk.StringVar(value='off')
app.error_bars = ctk.StringVar(value='off')

#advanced settings:
#	y limits
#	dark-mode/light-mode
#	x axis time
#	error bar std
#	median [IQR]

top_frame = ctk.CTkFrame(app, height=50)
plot_frame = ctk.CTkFrame(app, height=800,width=800)
well_frame = ctk.CTkFrame(app, height=350,width=400)
image_frame = ctk.CTkFrame(app, height=450,width=400)

top_frame.grid(row=0,sticky='nsew')
image_frame.grid(row=1, column=0, rowspan=3, columnspan=3,sticky='news')
well_frame.grid(row=4, column=0, rowspan=2, columnspan=3,sticky='news')
plot_frame.grid(row=1, column=3, rowspan=5, columnspan=2, sticky='news')

build_labels_default()

# Build the 96 well interactive canvas
WellLabeler = ctk.CTkCanvas(image_frame,width=300,height=200, bg='gray2',relief = 'ridge')
Build96Wells(WellLabeler)
WellLabeler.place(relx=0.4, rely = 0.5, anchor='center')

# This lets you select a label from the list to visualize
LabelList = ogtkinter.Listbox(image_frame,width=20, font=('Helvetica',15))
LabelList.place(relx=0.8,rely = 0.5,anchor='w')
for label in app.label_dict.keys():
	LabelList.insert(ogtkinter.END,label)
WellPickerGroupButton = ctk.CTkButton(image_frame,width=30,text='Select',command = ChooseGroup)
WellPickerGroupButton.place(relx=0.8, rely=0.8, anchor='w')

# Adding basic functionality buttons
upload_button = ctk.CTkButton(top_frame,text = 'Upload csv file', command=GetDataPath)
upload_button.grid(row=1, column=1)

display_button = ctk.CTkButton(plot_frame,text = 'Display plot', command = DisplayPlot)
display_button.place(relx=0.4,rely=0.85)

exit_button = ctk.CTkButton(top_frame,text = 'Close', command = exit)
exit_button.grid(row=1,column=5,sticky='e')

app.mainloop()

