# weather-station
weather station for the raspberry pi

###Operation
Weather station designed to work from a shed connected via wifi.

Sensors are read and data written to the Round Robin Database via a script run every 5 minutes via crontab job.

Rain script runs on start up and uses supervisor to guarantee it is running.

Records
  + outside temperature using a water proof DS18B20
  + inside temperature and humidity using a DHT22 sensor
  + door open/close detect
  + Maplins replacement rain gauge is used to capture:
    + precipiation rate
    + accumulated precipitation in 24 hours with at configurable reset time

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
pip install requests

####RRDtool
To install:
```
sudo apt-get install python-rrdtool
```

#### DS18B20
Added to /boot/config.txt:
```
# enable 1-wire GPIO devices
dtoverlay=w1-gpio,gpiopin=19
```


#### Webpage
To install:
```
sudo apt-get install apache2
cd /var/www
sudo ln -s ~/weatherdata weather_data
sudo ln -s ~/weatherlogs weather_logs
```

#### CRONTAB
Add the following line to 'sudo crontab -e'
```
@reboot sleep 60 && python /home/pi/weather/scripts/read_rain_gauge.py & # weather station job
0-55/5 * * * * python /home/pi/weather/scripts/read_sensors.py # weather station job
1-56/5 * * * * python /home/pi/weather/scripts/rrd_switch.py # weather station miplug job
1-56/5 * * * * python /home/pi/weather/scripts/rrd_export.py # weather station xml export job
3-33/30 * * * * python /home/pi/weather/scripts/rrd_ts_sync.py # weather station thingspeak job
4-59/15 * * * * python /home/pi/weather/scripts/watchdog.py # weather station watchdog job
0 9 * * 1 python /home/pi/weather/scripts/weekly_summary.pi # weather station weekly summary
2-57/5 * * * * /usr/bin/rsync -avze "/usr/bin/ssh -i /home/pi/.ssh/id_rsa -o StrictHostKayChecking=no -o UserKnownHostsFile=/dev/null" /home/pi/weather/data username@ip.addr:/home/username/weather/data
```
