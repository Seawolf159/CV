import csv
from datetime import datetime

from matplotlib import pyplot as plt

filename = 'KNMI_2017-01-01__2018-18-06.csv'
with open(filename) as f:
    reader = csv.reader(f)
    header_row = next(reader)

    dates, max_temp, min_temp, rain = [], [], [], []
    for row in reader:
        # Format the max. temperatures to be in celsius.
        formatted_max_temp = float(row[3]) / 10
        max_temp.append(formatted_max_temp)

        # Format the min. temperatures to be in celsius.
        formatted_min_temp = float(row[2]) / 10
        min_temp.append(formatted_min_temp)

        # Format the dates to be more readable
        formatted_dates = datetime.strptime(row[1], "%Y%m%d")
        dates.append(formatted_dates)

        # Format the rainfall to be in mm
        formatted_rain = float(row[4]) / 10
        rain.append(formatted_rain)

# Create Rotterdam weather data plot
fig = plt.figure(dpi=128, figsize=(10, 6))
plt.subplot(211)
plt.plot(dates, min_temp, c='blue')
plt.plot(dates, max_temp, c='red')
plt.fill_between(dates, max_temp, min_temp, facecolor='blue', alpha=.15)

# Format plot.
plt.title("Min and Max temp. Rotterdam 2017-2018")
fig.autofmt_xdate()
plt.ylabel("Temperature (°C)")

# Create rainfall plot
plt.subplot(212)
plt.plot(dates, rain, c='blue', alpha=0.5)
plt.fill_between(dates, rain, facecolor='blue', alpha=.15)

# Format plot
plt.title("Rainfall Rotterdam 2017-2018")
fig.autofmt_xdate()
plt.ylabel("Rainfall (mm)")

plt.show()
