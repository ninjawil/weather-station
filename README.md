# weather-station
weather station for the raspberry pi

Weather station designed to work from a shed connected via wifi.

Records
  + outside temperature using a water proof DS18B20
  + inside temperature and humidity using a DHT22 sensor
  + door open/close detect
  + rainfall via a rain bucket

Flashes an LED on and OFF every second to indicate operation.

Data recorded is sent to thingspeak. A write api key is requested on first start, this is then recorded to a text file.
