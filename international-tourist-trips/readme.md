# Arrivals of tourists from abroad - Data package

This data package contains the data that powers the chart ["Arrivals of tourists from abroad"](https://ourworldindata.org/grapher/international-tourist-trips?v=1&csvType=full&useColumnShortNames=false) on the Our World in Data website. It was downloaded on June 12, 2026.

### Active Filters

A filtered subset of the full data was downloaded. The following filters were applied:

## CSV Structure

The high level structure of the CSV file is that each row is an observation for an entity (usually a country or region) and a timepoint (usually a year).

The first two columns in the CSV file are "Entity" and "Code". "Entity" is the name of the entity (e.g. "United States"). "Code" is the OWID internal entity code that we use if the entity is a country or region. For most countries, this is the same as the [iso alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) code of the entity (e.g. "USA") - for non-standard countries like historical countries these are custom codes.

The third column is either "Year" or "Day". If the data is annual, this is "Year" and contains only the year as an integer. If the column is "Day", the column contains a date string in the form "YYYY-MM-DD".

The final column is the data column, which is the time series that powers the chart. If the CSV data is downloaded using the "full data" option, then the column corresponds to the time series below. If the CSV data is downloaded using the "only selected data visible in the chart" option then the data column is transformed depending on the chart type and thus the association with the time series might not be as straightforward.


## Metadata.json structure

The .metadata.json file contains metadata about the data package. The "charts" key contains information to recreate the chart, like the title, subtitle etc.. The "columns" key contains information about each of the columns in the csv, like the unit, timespan covered, citation for the data etc..

## About the data

Our World in Data is almost never the original producer of the data - almost all of the data we use has been compiled by others. If you want to re-use data, it is your responsibility to ensure that you adhere to the sources' license and to credit them correctly. Please note that a single time series may have more than one source - e.g. when we stich together data from different time periods by different producers or when we calculate per capita metrics using population data from a second source.

## Detailed information about the data


## Arrivals of tourists from abroad
Number of trips by visitors who arrive from abroad and stay overnight.
Last updated: January 21, 2026  
Next update: January 2027  
Date range: 1995–2024  
Unit: arrivals  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
UN Tourism (2025) – processed by Our World in Data

#### Full citation
UN Tourism (2025) – processed by Our World in Data. “Arrivals of tourists from abroad” [dataset]. UN Tourism, “UN Tourism Statistics Database” [original data].
Source: UN Tourism (2025) – processed by Our World In Data

### What you should know about this data
* Each trip by the same person is counted separately.
* When an individual visits a country multiple times within a year, each visit is counted as a separate arrival.
* Similarly, if a person travels to multiple countries during a single trip, their arrival in each country is recorded individually.
* As a result, the number of arrivals does not necessarily reflect the number of individuals traveling, as one person can generate multiple arrivals.
* Before 2006, the US counted same-day trips from Canada only. After 2006, day trips from Mexico were also included.

### Source

#### UN Tourism – UN Tourism Statistics Database
Retrieved on: 2026-01-21  
Retrieved from: https://www.untourism.int/tourism-statistics/tourism-statistics-database  


    