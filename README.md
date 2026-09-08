# Spatial Wheat analysis
## Summary
I developed a model intended to investigate patterns in spatial disequilibrium of wheat prices. In doing so, I discovered clear patterns in the disequilibrium which hold prediction power for next months prices, where adding it to a naive model increased its predictive power in terms of RMSE by 7%, which corresponds to having a prediction of 1 Euro/Tonn closer to actual price than a naive model. I quantified this pattern into a variable which I named the spatial disequilibrium index (SDI).
The predictive power from the SDI appears to come from local "overshoots" once a shock in price has occurred. Where an unforeseeable local event occurs, which sends price out of its spatial equilibrium. When this occurs, markets need time to adjust which oftentime results in overshoot where the correction of said price deviation is overcorrected before finally settling down. This pattern does however not give much predictive power when the shock which occurs is global, such as the war in Ukraine. 

## Introduction
I intend on creating a spatial wheat analysis, where I analyse spatial autocorrelation across Europe in order to identify possible interesting patterns.

The idea is to estimate spatial equilibriums between countries in wheat prices, and then identify unusual deviations from those equilibriums. This could create a tool to identify interesting events and shocks in the wheat market. Which can be built upon to estimate the type of shock and how often the deviation returns to the equilibrium. 

I will start off by doing this with a baseline spatial lag model, where I identify unusually large error terms in either direction in order to see where prices have deviated unusually. After this I can also make the model autoregressive in order to study how previous months events may linger in certain places. 

## Problem
The reason for studying spatial disequilibriums in wheat markets are two-fold. Firstly in order to get a better sense of when local disequilibrium occurs, which may be hard to spot by just investigating the price of wheat, since you must measure it in comparison to other places weighted by their connection. Secondly, the patterns of disequilibrium can have predictive power, if there for example are clear trends of "overshoot" after a disequilibrium has been found, this disequilibrium could then be a great signal for future price changes.
But why would predicting next month's wheat price be of interest intuitively? Well, it can solve many transport and storing decisions for starters. Once in a disequilibrium, such a model would give farmers and companies guidance of how to act in relation to harvest that should be realised by next month. Since one could for example more easily value the carrying costs of wheat in the current climate. It would also help manage for example mill input costs. 

## Data
So for this analysis, Wheat is used for every month of  19 different European countries, spanning from January 2014 until July 2026. This data was retrieved from the FAO's Food Price Monitoring and Analysis tool, which can be found at this URL: https://fpma.fao.org/giews/fpmat4/global/#/dashboard/tool/international. On this tool, there are even more countries but a lot of them have a lot of missing data, which is why I settled for using 19 out of them.

## Method
DISCLAIMER: The purpose of this method is not to produce causal results, since this is not the aim of the project. But rather to find out how deviation from spatial equilibriums usually behave, and if there are any good indicators of overshoot. Therefore, I will not address endogeneity problems related to the model, since this has little relevance for my specific purpose. 
I tried 2 different spatial weight matrixes in order to construct a spatial lag model in panel data form. Where the first weight is pure inverted row standardized distance between countries, and the other one also includes diesel prices multiplied in as a vector, in order to incorporate changes in transportation costs throughout the region. Both types of spatial weight matrixes produced similar results, where RMSE performed around 2% better in the predictive model when diesel prices were incorporated. 

The equation for my panel data model therefore looks like this:

$$
Y_{i,t} = \beta_0 + \beta_1 WY_{i,t} + \beta_2 WY_{i,t-1} + \beta_3 Y_{i,t-1} +\gamma_t + \eta_i+ \epsilon_{i,t}
$$

Where gamma is the month fixed effect, and eta is the country fixed effect.
Then I study the error term, which can be viewed as the part of the price of wheat today which cannot be explained by last month's price, the price of the neighbours, or last month's price of the neighbours. As well as from the fixed effects.
Furthermore I study how this error term differs between countries, and from the average error term for a country for a certain month. This is done in order to examine spatial price equilibriums, how they behave and how local disequilibriums are corrected.

So, first of all, to distinguish between local and more "global" disturbances which can potentially be classified as disequilibriums I have to compare global and local error terms. Where I define the global error term as the average error term of a certain time period for all countries, and the local error term as the error term for a specific country and a specific time period. Both these error terms compared make a new variable called the spatial disequilibrium index (SDI). Meaning how far a countries price moves away for spatial equilibrium uniquely, formally defined as below:

$$
SDI_{i,t} = \bar{\epsilon_{t}} - \epsilon_{i,t}
$$

## Presentation
This SDI can then be mapped and tracked, in order to understand how they behave. Below I show the 3 countries with the highest overall SDI and the lowest.

<img width="1500" height="400" alt="highest_local_resid" src=highest_resid.png/>


<img width="1500" height="400" alt="lowest_local_resid" src=lowest_resid.png />

In accordance with spatial economic theory, it appears that when spatial disequilibrium occurs in a country, there is always a bounce back. Meaning that the error term sticks out unusually in one direction, oftentime shortly after followed by it going in the opposite direction, always orbiting 0. This mean reversion of the error term also indicate stationarity.

This very direct trend gave me an idea to use the SDI in a model designed to predict how a country would deviate from its spatial equilibrium next month, since there is such a clear pattern in how it behaves.

# Prediction model

So, the whole model is a residual based forecast model. Where I saved a lagged version of the SDI. It is constructed as a panel data model with time and individual fixed effects as well. I used a regression model for this purpose, but also tried similar ML models such as gradient boosting with little improvements. 
It basically just predicts the current wheat price of a country at a certain time based on lags of SDI spanning 1-3 months, as well as lags of the dependent variable spanning the same number of months. 
Such a model compared to a baseline model, which only uses last month's price to predict today's price, performs on average 7% more accurately, or is on average 1 EURO per tonne closer in price, compared to a naive model. Strongly indicating that a SDI does contain some predicting power, the coefficient of it is also of negative sign, which is what was suspected, since a high SDI should be followed by a correction in the opposite direction (a drop in price) the next month. 

An example of the prediction and the actual value can be found below
<img width="1920" height="959" alt="model_predict_wheat" src=model_predict_wheat.png/>

What is interesting about this model is however that it is quite bad at predicting prices during more global events, such as for example the war in Ukraine, but is excellent at predicting local price disequilibriums, such as how Italy bounced back from its drought in 2025. 

## Further projects
Based on my analysis and model, it would be interesting to continue developing the analysis, by building a model focused on long run price forecasts in the region and combine with this model in a forecast reconciliation. 
My next project will therefore be focused on long run forecasts of price in the region, in order to combine output to be able to forecast more complex scenarios. 

This model can also very easily be translated into a spread forecast model. Where prices between 2 specific countries are estimated.






