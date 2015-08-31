# weather-station
weather station for the raspberry pi

Weather station designed to work from a shed connected via wifi.

Records
  + outside temperature using a water proof DS18B20
  + inside temperature and humidity using a DHT22 sensor
  + door open/close detect
  + Maplins replacement rain gauge is used to capture:
    + precipiation rate
    + accumulated precipitation in 24 hours with at configurable reset time

Flashes an LED on and OFF every second to indicate operation.

Data recorded is sent to thingspeak.
 + need to set up a crontab job to loop sync the rrd file with thingspeak

Dependencies:
 + PIGPIO - http://abyz.co.uk/rpi/pigpio/
 + needs requests python library - http://www.python-requests.org/en/latest/user/install/
