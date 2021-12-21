import esp 

#Connect to network
ssid = "Debi lan"
password = "HubbaBubbaGang799"
fische = "fische"

def wlan_conn():
    import network

    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print("Connecting to network...")
        sta_if.active(True)

        sta_if.config(dhcp_hostname="ESP_LED")
        sta_if.connect(ssid, password)
        while not sta_if.isconnected():
            pass

    print("Network configuration: ", sta_if.ifconfig())

#extensions
import gc
import time

#Booting
wlan_conn()
gc.collect()