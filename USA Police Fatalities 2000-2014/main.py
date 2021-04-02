import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'  ## turns off a warning that otherwise fires during df work
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

# sets seaborn chart style
sns.set_style('white')
sns.set_context("talk")

# in future versions converters will require explicit registration to function. this is included to prevent deprecation
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# for limiting/maximising pd result display
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 400)

# gets crime data source file
data_crimes = pd.read_excel('1985-2014_LocalCrimeTrendsInOneVar_ALL_Statesv2.xls')

# gets pertinent columns from crime data for 2000-2014
crimes_df = data_crimes[['Year', '# Violent Crimes']]
crimes_df['Year'] = crimes_df['Year'].apply(lambda x: str(x)[:4])
crimes_df = crimes_df.groupby('Year')['# Violent Crimes'].sum().reset_index()
crimes_df = crimes_df[crimes_df['Year'] >= '2000']
crimes_df['Crimes Thousands'] = crimes_df['# Violent Crimes'].apply(lambda x: x/1000)
crimes_df = crimes_df[['Year', 'Crimes Thousands']]

# get police fatalities source file
data_fatalities = pd.read_csv('Police Fatalities.csv', encoding='unicode_escape')

# gets pertinent columns from fatalities data for 2000-2014
fatalities_df = data_fatalities[['UID', 'Date']]
fatalities_df['Count'] = fatalities_df['UID'].apply(lambda x: 1)
fatalities_df['Date'] = data_fatalities['Date'].apply(lambda x: str(x)[-4:])
fatalities_df = fatalities_df.groupby('Date').agg('sum').reset_index()
fatalities_df = fatalities_df[['Date', 'Count']]
fatalities_df = fatalities_df[fatalities_df['Date'] <= '2014']

# get backend for renderer and set figure size
mpl.get_backend()
plt.figure(figsize=(20,12))

plt.bar(crimes_df['Year'], crimes_df['Crimes Thousands'], zorder=1, color='teal')
plt.plot(fatalities_df['Date'], fatalities_df['Count'], '-x', zorder=2, color='midnightblue')
plt.legend(['Police Involved Fatalities', 'Violent Crimes (Thousands)'])
plt.tick_params(top=False, bottom=False, left=True, right=True, labelleft=True, labelright=True, labelbottom=True, colors='dimgrey')
for spine in plt.gca().spines.values():
    spine.set_color('dimgrey')
plt.title('Trends for Violent Crimes and Police Involved Fatalities in USA between 2000 and 2014')

plt.show()