# Home Station Project
Project developed with a Raspberry pi to analyze the differences between the exterior and interior temperature of your house on a daily basis. Besides this, if you attached a camera, you can have a record of the people in that room

## Components
  - Raspberry pi: in my case is a Raspberry pi 4 model B.
  - SanDisk Extreme microSDXC 64GB.
  - bme280: temperature, humidity and preasure sensor.
  - Labists Camera 5MP 1080p.
  - Bruphny box for Raspberri pi4 model B.

![raspberry](https://i.ibb.co/QnHLxRJ/raspberry.jpg)

## Preparation
The information extracted with this code will be uploaded to AWS dynamoDB. In order to do that, you must create a free account with AWS and setup the lambdas stored inside the folder ./aws_lambda creating a role for those lambdas as follows: https://aws.amazon.com/es/blogs/security/how-to-create-an-aws-iam-policy-to-grant-aws-lambda-access-to-an-amazon-dynamodb-table/

Once you have created this, you must modify the lines 45 and 59 from the script ./raspberry/collect_and_save_data.py with the proper url to your lambdas. To finish with your AWS preparation you also must modify the lines 20 and 23 from the script ./info_summary/get_summary_pdf.py.

## Running the station
You can launch the script as normal python script calling to ./raspberry/collect_and_save_data.py or setting a cron task to execute the script each hour.

## Extracting the report as pdf
Once you have at least 24 hours of information, you can download a pdf with the report information regarding to:
 - Temperature: plot with the information regarding to the temperature in your house and in your city.
 - Humidity: plot with the information regarding to the relative humidity in your house and in your city.
 - Sky: sky condition of that day in your city (Aemet).
 - Wind: plot with the wind direction in the last 24 hours
 - People: information about the people in that room in the last 24 hours and a picture of the most relevant hour.

An example of this report can be found here: 
https://github.com/Dangaran/home_station_project/blob/main/info_summary/daily_summary_07-01-2021.pdf
