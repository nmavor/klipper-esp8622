from machine import I2C, Pin
import sys
import network
import utime
import urequests
from time import sleep
import ssd1306

# Network settings
wifi_ssid = "*************"
wifi_password = "***********"
host = "http://172.16.0.215:7125"
printer_api = "/api/printer"
status_api = "/printer/objects/query?webhooks&virtual_sdcard&print_stats"

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(wifi_ssid, wifi_password)
sleep(10)
# screen setup
i2c = I2C(scl=Pin(5), sda=Pin(4))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
oled.fill(0)

# Continually try to connect to WiFi access point
while not station.isconnected():
    # Try to connect to WiFi access point
    print("Connecting...")
    station.connect(wifi_ssid, wifi_password)

while station.isconnected():
    response = urequests.get(host+printer_api)
    data = response.json()
    bed_temp = "Bed : " + str(data["temperature"]["bed"]["target"]) + "/" + str(data["temperature"]["bed"]["actual"])
    hotend_temp = "HE : " + str(data["temperature"]["tool0"]["target"]) + "/" + str(
        data["temperature"]["tool0"]["actual"])
    response = urequests.get(host+status_api)
    data = response.json()

    print_progress = data["result"]["status"]["virtual_sdcard"]["progress"] * 100
    if int(print_progress) == 100:
        print_progress   = "DONE"
        progress = "progress: " + str(print_progress)
    else:
        progress = "progress: " + str(int(print_progress)) + "%"
    oled.fill(0)
    oled.text(bed_temp, 0, 0, 1)
    oled.text(hotend_temp, 0, 12, 1)
    oled.text(progress, 0, 24, 1)
    oled.show()
    sleep(5)

# If we lose connection, repeat this main.py and retry for a connection
print("Connection lost. Trying again.")
