# weather-station
weather station for the raspberry pi

###Operation
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

### Dependencies

#### Python
System needs Python 2.7.9

#### PIGPIO
See http://abyz.co.uk/rpi/pigpio/ for more details.
Install using:
```
wget abyz.co.uk/rpi/pigpio/pigpio.zip
unzip pigpio.zip
cd PIGPIO
make
make install
```



#### Requests
Download and install from http://www.python-requests.org/en/latest/user/install/

####RRDtool
To install:
```
pip install python-rrdtool
```

#### DS18B20
Added to /boot/config.txt:
```
# enable 1-wire GPIO devices
dtoverlay=w1-gpio
```

#### python-crontab
