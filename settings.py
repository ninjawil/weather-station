#-----------------------------------------------------------------------
#
# Weather station settings
#
#-----------------------------------------------------------------------

#!usr/bin/env python


#=======================================================================
# SETTINGS VARIABLES
#=======================================================================

# --- Set up GPIO referencing----
GLOBAL_BROADCOM_REF     = True

if GLOBAL_BROADCOM_REF:
    GLOBAL_Pin_11   = 17
    GLOBAL_Pin_12   = 18
    GLOBAL_Pin_13   = 27
    GLOBAL_Pin_14   = 27
else:
    GLOBAL_Pin_11   = 11
    GLOBAL_Pin_12   = 12
    GLOBAL_Pin_13   = 13
    GLOBAL_Pin_14   = 14

# --- System set up ---
GLOBAL_update_rate          = 5 # seconds
GLOBAL_w1_device_path       = '/sys/bus/w1/devices/'
GLOBAL_screen_output        = False


# --- Set up thingspeak ----
GLOBAL_thingspeak_enable_update     = True
GLOBAL_thingspeak_host_addr         = 'api.thingspeak.com:80'
GLOBAL_thingspeak_write_api_key     = '30SNTCFLNJEI3937'

GLOBAL_thingspeak_field_1   = 1
GLOBAL_thingspeak_field_2   = 2
GLOBAL_thingspeak_field_3   = 3
GLOBAL_thingspeak_field_4   = 4
GLOBAL_thingspeak_field_5   = 5
GLOBAL_thingspeak_field_6   = 6
GLOBAL_thingspeak_field_7   = 7
GLOBAL_thingspeak_field_8   = 8


# --- Set up sensors ----
GLOBAL_out_sensor_enable    = True
GLOBAL_out_temp_sensor_ref  = '28-0414705bceff'
GLOBAL_out_temp_TS_field    = GLOBAL_thingspeak_field_1

GLOBAL_in_sensor_enable     = True
GLOBAL_in_sensor_ref        = 'DHT22'
GLOBAL_in_sensor_pin        = GLOBAL_Pin_11
GLOBAL_in_temp_TS_field     = GLOBAL_thingspeak_field_2
GLOBAL_in_hum_TS_field      = GLOBAL_thingspeak_field_3

GLOBAL_door_sensor_enable   = True
GLOBAL_door_sensor_pin      = GLOBAL_Pin_14
GLOBAL_door_TS_field        = GLOBAL_thingspeak_field_4

GLOBAL_rain_sensor_enable   = True
GLOBAL_rain_sensor_pin      = GLOBAL_Pin_13
GLOBAL_rain_TS_field        = GLOBAL_thingspeak_field_5
GLOBAL_rain_tick_measure    = 1.5 #millimeters
GLOBAL_rain_tick_meas_time  = 0.5 #minutes
GLOBAL_rain_tick_count      = 0
GLOBAL_rain_task_count      = 0


# --- Set up flashing LED ----
GLOBAL_LED_display_time     = False
GLOBAL_LED_pin              = GLOBAL_Pin_12
GLOBAL_LED_flash_rate       = 1  # seconds
