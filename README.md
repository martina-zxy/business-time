# business-time
A simple package to perform business-hour-aware-calculations on datetime

## Usage
<pre><code>>>> business_cal = EuronextExchangeCalendar()
>>> input = datetime(2020, 5, 17, 23, 36, tzinfo=timezone('UTC'))
>>> subtract_business_interval(input, business_cal,'1 day', 2)
datetime(2020, 5, 14, 0, 0, tzinfo=timezone('UTC'))
>>> subtract_business_interval(input, business_cal, '30 minute', 2)
datetime(2020, 5, 15, 14, 30, tzinfo=timezone('UTC'))</code></pre>

## Features
* Business-hour-aware calculations on datetime detailed to minute granularity 
* A number of useful predicate functions related to business days/hours