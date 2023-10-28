# downslope-windstorms
Code to perform a climatology of chinooks, i.e. downslope windstorms in the Front Range of Colorado using data from NREL Flatirons Campus (M2)

Data from: https://midcdmz.nrel.gov/apps/daily.pl?site=NWTC&start=20010824
Designed to work with 10m wind speed (m/s) and wind direction (deg) data at 1-minute frequency.

Reads in time series data and identifies (1) how many windstorms occurred within that data set depending on required speed and duration of winds and (2) properties of windstorm events within the specified dataset.

Windstorm trends are assessed daily, monthly and annually. 
