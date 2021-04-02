import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

# in future versions converters will require explicit registration to function. this is included to prevent deprecation
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

## for limiting/maximising pd result display
# pd.set_option('display.max_columns', 20)
# pd.set_option('display.width', 400)

# gets data source file
weather = pd.read_csv('fb441e62df2d58994928907a91895ec62c2c42e6cd075c2700843b89.csv')
weather = weather.sort_values('Date', ascending=False)

# separates max and mins into two DFs and drops unnecessary columns
max_decade_df = weather[weather['Element'] == 'TMAX']
max_decade_df = max_decade_df[['Date', 'Data_Value']]
min_decade_df = weather[weather['Element'] == 'TMIN']
min_decade_df = min_decade_df[['Date', 'Data_Value']]

# creates new DFs for max and min records for 2015, then drops 2015 records from the decade DFs
max_2015 = max_decade_df[max_decade_df['Date'].apply(lambda x: x[:4] == '2015')]
min_2015 = min_decade_df[min_decade_df['Date'].apply(lambda x: x[:4] == '2015')]
max_decade_df = max_decade_df[max_decade_df['Date'].apply(lambda x: x[:4] != '2015')]
min_decade_df = min_decade_df[min_decade_df['Date'].apply(lambda x: x[:4] != '2015')]

# converts datetimes to just month and day for easier aggregation
max_decade_df['Date'] = max_decade_df['Date'].apply(lambda x: '1901-' + x[5:])
min_decade_df['Date'] = min_decade_df['Date'].apply(lambda x: '1901-' + x[5:])
max_2015['Date'] = max_2015['Date'].apply(lambda x: '1901-' + x[5:])
min_2015['Date'] = min_2015['Date'].apply(lambda x: '1901-' + x[5:])

# aggregates all DFs by maximum or minimum value on each date
max_decade_df = max_decade_df.groupby('Date').agg('max').reset_index()
min_decade_df = min_decade_df.groupby('Date').agg('min').reset_index()
max_2015 = max_2015.groupby('Date').agg('max').reset_index()
min_2015 = min_2015.groupby('Date').agg('min').reset_index()

# removes leap days from decade DFs
max_decade_df = max_decade_df[~max_decade_df['Date'].str.contains('02-29')].reset_index()
min_decade_df = min_decade_df[~min_decade_df['Date'].str.contains('02-29')].reset_index()

# merges decade and 2015 DFs and compares record for each date to create new DFs containing dates where 2015 was hotter or colder than the min/max from decade
# max
compare_max = pd.merge(max_decade_df, max_2015, how='left', on='Date')[['Date', 'Data_Value_x', 'Data_Value_y']].rename(columns={'Data_Value_x': 'Decade Max', 'Data_Value_y': '2015 Max'})
compare_max['2015 Max Outlier'] = compare_max.apply(lambda row: row['2015 Max'] > row['Decade Max'], axis=1)
outliers_max_2015 = compare_max[compare_max['2015 Max Outlier']][['Date', '2015 Max']]
# min
compare_min = pd.merge(min_decade_df, min_2015, how='left', on='Date')[['Date', 'Data_Value_x', 'Data_Value_y']].rename(columns={'Data_Value_x': 'Decade Min', 'Data_Value_y': '2015 Min'})
compare_min['2015 Min Outlier'] = compare_min.apply(lambda row: row['2015 Min'] < row['Decade Min'], axis=1)
outliers_min_2015 = compare_min[compare_min['2015 Min Outlier']][['Date', '2015 Min']]


# converts each date column to a matplotlib date float
max_decade_df['Date'] = max_decade_df['Date'].apply(lambda x: mdates.datestr2num(x))
min_decade_df['Date'] = min_decade_df['Date'].apply(lambda x: mdates.datestr2num(x))
outliers_max_2015['Date'] = outliers_max_2015['Date'].apply(lambda x: mdates.datestr2num(x))
outliers_min_2015['Date'] = outliers_min_2015['Date'].apply(lambda x: mdates.datestr2num(x))

# creates a list of months to be used on x axis
locator = mdates.MonthLocator()
fmt = mdates.DateFormatter('%b')

# get backend for renderer and set figure size
mpl.get_backend()
plt.figure(figsize=(20,12))

# plots each series - uses plot_date because we have converted our date strings to matplotlib datenums
plt.plot_date(list(max_decade_df['Date']), list(max_decade_df['Data_Value']), '-', c='orange')
plt.plot_date(list(min_decade_df['Date']), list(min_decade_df['Data_Value']), '-', c='green')
plt.plot_date(list(outliers_max_2015['Date']), list(outliers_max_2015['2015 Max']), 'o', c='red')
plt.plot_date(list(outliers_min_2015['Date']), list(outliers_min_2015['2015 Min']), 'o', c='blue')

# shades space between two line plots blue
plt.gca().fill_between(min_decade_df['Date'], min_decade_df['Data_Value'], max_decade_df['Data_Value'], facecolor = 'blue', alpha =.10)

# sets x axis to use formatted months as ticks
X = plt.gca().xaxis
X.set_major_locator(locator)
X.set_major_formatter(fmt)

# creates a minor tick sequence to use for labelling so that x tick labels appear between x ticks
X.set_minor_locator(mdates.MonthLocator(bymonthday=16))
X.set_major_formatter(ticker.NullFormatter())
X.set_minor_formatter(mdates.DateFormatter('%b'))
for tick in X.get_minor_ticks():
    tick.tick1line.set_markersize(0)
    tick.tick2line.set_markersize(0)
    tick.label1.set_horizontalalignment('center')

# chops off whitespace on the x axis before and after our data
plt.gca().set_xlim(mdates.datestr2num('1901-01-01'), mdates.datestr2num('1901-12-31'))

# labels components of graph and creates legend
plt.legend(['Highest Temps 2005-2014', 'Lowest Temps 2005-2014', '2015 Record Higher', '2015 Record Lower'])
plt.xlabel('Month')
plt.ylabel('Temperature in C')
plt.title('Extreme High and Low Temperatures in Ann Arbor, Michigan in 2015 Compared to Records for 2005-2014')

plt.show()