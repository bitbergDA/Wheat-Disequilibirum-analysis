# Spatial Wheat analysis
I intend on creating a spatial wheat analysis for basis where I analyise spatial autocorrelation across Europe in order to indentify possible trading strategies.

The idea is to estimate long run spatial equilibriums between countries in wheat prices, and then identify unusal deviations from thouse equilibriums. This could create a tool to identify intersting events and shocks in the wheat market. Which can be built upon to estimate the type of shock and how often the deviation returns to the long run equilibrium. 

I will start of by doing this with a baseline spatial lag model, where i identify unusally large error terms in either direction in order to see where prices have deviated unusually. After this I can also make the model autoregressive in order to study how previous months event may linger in certain places. 

## Data
So for this analysis, Wheat is used for every month of  19 different European countries. This data was retrived from the FAO's Food Price Monitoring and Analysis tool, which can be found at this URL: https://fpma.fao.org/giews/fpmat4/global/#/dashboard/tool/international. On this tool, there are even more countries but a lot of them have alot of missing data.

## Method
I tried 2 different spatial weight matrixes in order to construct a spatial lag model in panel data form. Where the first weight is pure inversed row standardized distance between countries, and the other one also includes gas prices, such that scaling becomes more important. Including Diesel prices in the weight matrix did however increase precision slightly which is why this is the spatial weight matrix I used.

The equation for my panel data model therefore looks like this:

$$
Y_{i,t} = \beta_0 + \beta_1 WY_{i,t} + \beta_2 WY_{i,t-1} + \beta_3 Y_{i,t-1} +\gamma_t + \eta_i+ \epsilon_{i,t}
$$

Where gamma is the month fixed effect, and eta is the country fixed effect.
Then i study the error term, which can be viewed as the part of the price of wheat which cannot be explained by last months price, the price of the neighbours, or last months price of the neighbours. As well as the usualy price at that month and for that country. 
Furtermore I study how this error term differese between countries, and from the average error term for a country for a certain month. This is done in order to examining spatial price equilibriums, how they behave and how local disequilibirums are corrected.

So, first of all, to distinguish between local and more "global" distrubances which can potentially be classified as disquilibiriums I have to compare global and local error terms. Where i define the global error term as the average error term of a certain time period for all countries, and the local error term as the error term for a specific country and a specific time period. Both these error term compared then make up my spatial disequilibirum index (SDI). Meaning how far a countries price moves away for spatial equilibirum uniquelly, formally defined as below:

$$
SDI_{i,t} = \bar{\epsilon_{t}} - \epsilon_{i,t}
$$

## Presentation
This SDI can then be mapped and tracked, in order to understand how they behave. Below I show the 3 countries with the highest overal SDI and the lowest.

<img width="1500" height="400" alt="highest_local_resid" src="https://github.com/user-attachments/assets/1bf4333b-0c52-4626-bc7f-a62710e66950" />


<img width="1500" height="400" alt="lowest_local_resid" src="https://github.com/user-attachments/assets/f8be5a15-555b-4ab7-84c5-743c10df7fc3" />

In accordance with spatial economic theory, it appears that when spatial disqeuilibirums occur in a country, there is always a bounce back. Meaning that the error term sticks out unusually in one direction, oftentime shortly after followed by it going in the opposite direction, alway orbiting 0. 

This very direct trend gave me an idea, to use the SDI in a model designed to predict how a country would deviate from its spatial equilibrium next month, since there is such a clear pattern in how it behaves.

# Prediction model

So, the whole model is a residual based forecast model. Where I saved a lagged version of the SDI. It is constructed as a panel data model with time and individual fixed effects as well. I used a regression model for this purpose, but also tried similar ML models such as gradieent boosting with little improvements. 
It basically just predicts the current wheat price of a country at a certain time based on lags of SDI spanning 1-3 months, as well as lags of the dependent variable spanning the same number of months. 
Such a model compared to a baseline model, which only uses last months price to predict todays price, performs on average 7% more accuratly, or is on average 1 EURO per tonn closer in price guessing than such a naive model. Strongly indicating that a SDI does contain some predicting power, the coefficient of it is also of negative sign, which is what was suspected, since a high SDI should be followed by a correction in the opposite direction (a drop in price) the next month. But the average RMSE is around 12.5, so there is still some margin of error, even though it outperforms a naive model. 

An example of the prediciton and the actual value can be found below
<img width="1920" height="959" alt="model_predict_wheat" src="https://github.com/user-attachments/assets/dd4c5f3f-baeb-4b82-a0d1-79699e978f0b" />

What is interesting about this model is however that it is quite bad at predicting prices during more global events, such as for example the war in Ukraine, but is excellent to predict local price disequilibirums, such as how Italy bounced back from its drought 2025. 






