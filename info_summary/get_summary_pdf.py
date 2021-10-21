import requests
import pandas as pd
from plotnine import *
import json
import time
from fpdf import FPDF
from datetime import datetime


# change pandas display options
pd.options.display.max_columns = 101
pd.options.display.max_rows = 200
pd.options.display.precision = 7

# get aemet and home information
last_day = {
    'date_start': int(time.time()) - 86400,
    'date_end': int(time.time())
}
response_aemet = requests.post('url_to_aws_lambda/get-aemet-data', json=last_day)
aemet_info = json.loads(response_aemet.text)

response_home = requests.post('url_to_aws_lambda/get-home-data', json=last_day)
home_info = json.loads(response_home.text)


# merge dataframes
aemet_info_df = pd.DataFrame(aemet_info)
aemet_info_df.sort_values(by="timestamp", inplace=True)

home_info_df = pd.DataFrame(home_info)
home_info_df.sort_values(by="timestamp", inplace=True)

last_day_info = pd.merge(aemet_info_df, home_info_df, on='timestamp', suffixes=("_aemet", "_home"))

last_day_info = last_day_info.iloc[100:124, :]



# -----------------------------------------------------------
# 
#                     TEMPERATURE ANALYSIS
#
# -----------------------------------------------------------
# prepare data for plotting
home_temp_threshold = 20
# transform hour column to string and sort them 
last_day_info['hour'] = last_day_info['hour'].astype(str) 
last_day_info['hour'] = pd.Categorical(last_day_info['hour'], categories=last_day_info['hour'])

# melt data to plot temperatures
temp_data_to_plot = last_day_info.melt(id_vars=['hour'], value_vars=['thermal_sensation', 'temperature_aemet', 'temperature_home'], var_name='temp_loc', value_name='temp_value')

# change temp_loc to more readable strings for plotting
temp_data_to_plot['temp_loc'].replace({'thermal_sensation': 'Thermal sensation (outside)', 
                                       'temperature_aemet': 'Temperature (outside)',
                                       'temperature_home': 'Temperature (home)',}, inplace=True)

# get home data
home_temp_plot = temp_data_to_plot.loc[temp_data_to_plot.temp_loc == 'Temperature (home)', :]

# make the plot
temp_plot = ggplot(temp_data_to_plot, aes(x = 'hour', y = 'temp_value', color = 'temp_loc', group = 'temp_loc')) +\
                geom_line() +\
                geom_point(size = .5) +\
                geom_point(aes(x='hour', y='temp_value'), size = .5, color = ['#FF6633' if value <= home_temp_threshold else '#64f564' for value in list(home_temp_plot['temp_value'])], data = home_temp_plot) +\
                geom_hline(aes(yintercept= home_temp_threshold), size = 1, linetype = 'dotted', alpha = .2) +\
                labs(title = 'Differences in temperature between outside and inside your house', x = 'Hour', y = 'Temperature (ºC)', color='') +\
                scale_color_manual(values = ['#64f564', '#e6454a', '#6bb8ff']) +\
                theme_classic() +\
                theme(plot_title=element_text(face='bold', ha= 'center', size = 10))

ggsave(plot=temp_plot, filename='./today_plots/temp_plot.png', dpi=100)




# -----------------------------------------------------------
# 
#                     HUMIDITY ANALYSIS
#
# -----------------------------------------------------------
# prepare plot
hum_data_to_plot = last_day_info.melt(id_vars=['hour'], value_vars=['humidity_home', 'humidity_aemet'], var_name='hum_loc', value_name='hum_value')
hum_data_to_plot.hum_value = pd.to_numeric(hum_data_to_plot.hum_value, errors = 'raise')
hum_data_to_plot['hum_loc'].replace({'humidity_aemet': 'Humidity (outside)',
                                      'humidity_home': 'Humidity (home)',}, inplace=True)


# create the plot
hum_plot = ggplot(hum_data_to_plot, aes(x = 'hour', y = 'hum_value', fill = 'hum_loc')) +\
                geom_bar(stat = 'identity', position='dodge', color = 'grey') +\
                labs(title = 'Differences in humidity between outside and inside your house', x = 'Hour', y = 'Relative humidity (%)', fill='') +\
                scale_fill_manual(values = ['#9da6d4', '#4f66e0']) +\
                theme_classic() +\
                theme(plot_title=element_text(face='bold', ha= 'center', size = 10))

ggsave(plot=hum_plot, filename='./today_plots/hum_plot.png', dpi=100)



# -----------------------------------------------------------
# 
#                     WIND ANALYSIS
#
# -----------------------------------------------------------
# Wind information
# avg and max speed
avg_wind_speed = round(last_day_info.avg_wind_speed.apply(lambda x: int(x)).mean(), 2)
max_wind_speed = round(last_day_info.max_wind_speed.apply(lambda x: int(x)).max(), 2)

# prepare plot
# count number of cardinal directions 
cardinal_dir_list = ['N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO']
wind_dir_df = last_day_info.wind_direction.value_counts().to_frame()
wind_dir_df.reset_index(inplace =True)
wind_dir_df.rename(columns = {'index': 'cardinal_direction'}, inplace = True)
wind_dir_df

# complete cardinal column
missing_dir = list(set(cardinal_dir_list) - set(wind_dir_df.cardinal_direction.to_list()))
for direction in missing_dir:
    wind_dir_df = wind_dir_df.append({'cardinal_direction': direction,
                                      'wind_direction': 0}, ignore_index=True)

wind_dir_df
# create column with correct order to plot
wind_dir_df = wind_dir_df.sort_values(by = 'cardinal_direction').reset_index(drop = True)
wind_dir_df['cardinal_order'] = [2, 0, 1, 7, 6, 4, 3, 5]
wind_dir_df = wind_dir_df.sort_values(by = 'cardinal_order')
wind_dir_df.index = wind_dir_df.cardinal_order


# create x and y axis
wind_dir_df['x_axis'] = [0,
                         int(wind_dir_df.loc[wind_dir_df.cardinal_direction == 'NE', 'wind_direction']),
                         int(wind_dir_df.loc[wind_dir_df.cardinal_direction == 'E', 'wind_direction']), 
                         int(wind_dir_df.loc[wind_dir_df.cardinal_direction == 'SE', 'wind_direction']),
                         0,
                         int(-wind_dir_df.loc[wind_dir_df.cardinal_direction == 'SO', 'wind_direction']),
                         int(-wind_dir_df.loc[wind_dir_df.cardinal_direction == 'O', 'wind_direction']),
                         int(-wind_dir_df.loc[wind_dir_df.cardinal_direction == 'NO', 'wind_direction'])] 

wind_dir_df['y_axis'] = [int(wind_dir_df.loc[wind_dir_df.cardinal_direction == 'N', 'wind_direction']),
                         int(wind_dir_df.loc[wind_dir_df.cardinal_direction == 'NE', 'wind_direction']),
                         0,
                         int(-wind_dir_df.loc[wind_dir_df.cardinal_direction == 'SE', 'wind_direction']),
                         int(-wind_dir_df.loc[wind_dir_df.cardinal_direction == 'S', 'wind_direction']),
                         int(-wind_dir_df.loc[wind_dir_df.cardinal_direction == 'SO', 'wind_direction']),
                         0,
                         int(wind_dir_df.loc[wind_dir_df.cardinal_direction == 'NO', 'wind_direction'])] 

# remove 0 columns to plot
wind_dir_df = wind_dir_df.loc[wind_dir_df.wind_direction != 0, :]

# create the plot
wind_plot = ggplot(aes(x = 'x_axis', y = 'y_axis'), wind_dir_df) +\
                geom_point(size = .3, color = 'darkgreen') +\
                geom_polygon(alpha = .2) +\
                xlim(-24, 24) +\
                ylim(-24, 24) +\
                geom_segment(aes(x=0, xend=22, y=0, yend=0), alpha = 0.1, linetype = 'dotted',  arrow = arrow()) +\
                geom_segment(aes(x=0, xend=-22, y=0, yend=0), alpha = 0.1, linetype = 'dotted',  arrow = arrow()) +\
                geom_segment(aes(x=0, xend=0, y=0, yend=22), alpha = 0.1, linetype = 'dotted',  arrow = arrow()) +\
                geom_segment(aes(x=0, xend=0, y=0, yend=-22), alpha = 0.1, linetype = 'dotted',  arrow = arrow()) +\
                annotate('text', x=23, y= 0, label = 'E', color = 'darkgreen') +\
                annotate('text', x=-23.3, y= 0, label = 'O', color = 'darkgreen') +\
                annotate('text', x=0, y= 24, label = 'N', color = 'darkgreen') +\
                annotate('text', x=0, y= -24, label = 'S', color = 'darkgreen') +\
                labs(title = 'Wind direction over the last 24 hours', x = '', y = '') +\
                theme_classic() +\
                theme(plot_title=element_text(face='bold', ha= 'center', size = 15),
                      panel_grid_major = element_blank(), 
                      panel_grid_minor = element_blank(), 
                      panel_background = element_blank(),
                      axis_line = element_blank(),
                      axis_ticks_major = element_blank(),
                      axis_text = element_blank())
    
ggsave(plot=wind_plot, filename='./today_plots/wind_plot.png', dpi=100)




# -----------------------------------------------------------
# 
#                     SKY ANALYSIS
#
# -----------------------------------------------------------
most_common_sky = last_day_info.sky_condition.value_counts().idxmax()
snow_probability = round(last_day_info.snow_probability.apply(lambda x: int(x)).mean(), 2)
precipitation_probability = round(last_day_info.precipitation_probability.apply(lambda x: int(x)).mean(), 2)
most_common_warning_lvl = last_day_info.warning_level.value_counts().idxmax()
total_precipitation = round(last_day_info.precipitation.apply(lambda x: int(x)).sum(), 2)




# -----------------------------------------------------------
# 
#                     PEOPLE ANALYSIS
#
# -----------------------------------------------------------
# Check number of people
people_df = last_day_info.loc[:, ['hour', 'pic_name']]
people_df.pic_name = people_df.pic_name.fillna('No_0_data')
people_df['people_count'] = people_df.pic_name.apply(lambda x: int(x.split('_')[1]))

hours_with_people_at_home = people_df.loc[people_df.people_count > 0].shape[0]
most_people_in_room = people_df.people_count.value_counts(ascending = True).index[0]

rows_with_most_people = people_df.loc[people_df.people_count == most_people_in_room]
hours_with_most_people = rows_with_most_people.hour.to_list()
pics_names = rows_with_most_people.pic_name.to_list()




# -----------------------------------------------------------
# 
#                     PDF CREATION
#
# -----------------------------------------------------------
# export information in pdf
# extract date
today_timestamp = int(last_day_info.timestamp.reset_index(drop =True)[5])
today_date = datetime.utcfromtimestamp(today_timestamp).strftime('%d/%m/%Y')


# create pdf to export
pdf = FPDF()
pdf.add_page()
pdf.set_xy(0, 5)
pdf.set_font('arial', 'B', 12)
pdf.cell(0, 10, 'Home report from {}'.format(today_date), 0, 2, 'C') # title
pdf.cell(5)
# subtitle
pdf.set_font('arial', '', 10)
pdf.cell(0, 10, 'This report was extracted from the information gathered by the sensors from your Raspberry and Aemet.', 0, 2, 'C')
pdf.set_font('arial', 'B', 12)

# First analysis - Temperature and Humidity
pdf.cell(60, 10, 'Temperature Analysis:', 0, 0, 'R')
pdf.cell(85, 10, 'Humidity Analysis:', 0, 2, 'R')

pdf.image('./today_plots/temp_plot.png', x = 3, y = 35, w = 110, h = 70, type = '', link = '')
pdf.image('./today_plots/hum_plot.png', x = 110, y = 35, w = 100, h = 70, type = '', link = '')

# second analysis - Sky and wind
pdf.set_x(60)
pdf.set_y(110)

pdf.cell(0, 10, 'Sky Analysis:', 0, 2, 'L')

pdf.set_font('arial', '', 10)
pdf.cell(0, 7, 'Most common sky in 24 hours: {}'.format(most_common_sky), 0, 2, 'L')
pdf.cell(0, 7, 'Most common warning level in 24 hours: {}'.format(most_common_warning_lvl), 0, 2, 'L')
pdf.cell(0, 7, 'Probability of Precipitation in 24 hours: {} %'.format(precipitation_probability), 0, 2, 'L')
pdf.cell(0, 7, 'Probability of Snow in 24 hours: {} %'.format(snow_probability), 0, 2, 'L')
pdf.cell(0, 7, 'Total Precipitation in 24 hours: {} mm'.format(total_precipitation), 0, 2, 'L')

pdf.image('./today_plots/wind_plot.png', x = 110, y = 112, w = 70, h = 60, type = '', link = '')

# third analysis - Pictures from people
pdf.set_y(170)

pdf.set_font('arial', 'B', 12)
pdf.cell(0, 10, 'Camera Analysis:', 0, 2, 'L')

pdf.set_font('arial', '', 10)
pdf.cell(0, 7, 'Number of hours with people at home: {}'.format(hours_with_people_at_home), 0, 2, 'L')
pdf.cell(0, 7, 'How many people were in the room at the time of maximum capacity?: {}'.format(most_people_in_room), 0, 2, 'L')
pdf.cell(0, 7, 'How many hours was the house with the maximum number of people?: {}'.format(rows_with_most_people.shape[0]), 0, 2, 'L')
pdf.cell(0, 7, 'What were the hours when the house had the maximum number of people?: {}'.format(', '.join(hours_with_most_people)), 0, 2, 'L')
pdf.cell(0, 7, 'What are the pictura names that correspond to those hours?: {}'.format(', '.join(pics_names)), 0, 2, 'L')

pdf.image('../rapsberry/camera/images/{}'.format(pics_names[0]), x = 15, y = 200, w = 70, h = 60, type = '', link = '')

# save output
pdf.output('test.pdf', 'F')


