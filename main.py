import uasyncio as asyncio
from mqtt_as import MQTTClient
from mqtt_as import config


SERVER = '192.168.0.162'  # Change to suit e.g. 'iot.eclipse.org'

def boring(s):
    print("Blowing air!")

mode = None
current = None

def callback(topic, msg, retained):
    print((topic, msg, retained))
    print(str(msg))
    msg = msg.decode("utf-8")
    global BRIGHTNESS
    global mode
    global current

    if msg is "rainbow" or msg is "side_1":
        mode = rainbow
        print("Led switched to rainbow")
    elif msg is "off" or msg is "side_0":
        mode = off
        print("Led switched to off")
    elif msg is "on":
        mode = one_color
        print("Led switched to on")
    elif msg is "kleiderschrank":
        mode = kleiderschrank
        print("Kleiderschrank switched to on")
    elif msg is "film" or msg is "side_2":
        mode = film
        print("Film switched to on")
    elif msg is "platsch":
        mode = platsch 
        print("Platsch switched to on")
    elif msg is "lighter":
        if BRIGHTNESS < 1.0:
            BRIGHTNESS+=0.1
            print("Brightness: ", BRIGHTNESS)

            #logik
            mode = current
            print("current: ", current.__name__)

    elif msg is "dimmer":
        if BRIGHTNESS >0.05:
            BRIGHTNESS-=0.1
            print("Brightness: ", BRIGHTNESS)
            

            #logik
            mode = current
            print("current: ", current.__name__)


async def conn_han(client):
    await client.subscribe('chris/led', 1)




###MAIN
async def main(client, strip):
    
    await client.connect()
    n = 0
    while True:
        global mode
        await asyncio.sleep(.5)
        #print('publish', n)
        ## If WiFi is down the following will pause for the duration.
        #await client.publish('result', '{}'.format(n), qos = 1)
        #n += 1
        #print(mode)
        if mode is not None:
            task = asyncio.create_task(mode(strip))
            await task

            #asyncio.run(mode(strip))
            #print("Trying to run")

##################


config['subs_cb'] = callback
config['connect_coro'] = conn_han
config['server'] = SERVER
print("got here")

MQTTClient.DEBUG = True  # Optional: print diagnostic messages
client = MQTTClient(config)

print("got here")
#LED Init

import neopixel
import machine

NUM_LEDS = 600
DATA_PIN = 5
BRIGHTNESS = 1.0

strip = neopixel.NeoPixel(machine.Pin(DATA_PIN), NUM_LEDS)

async def off(strip):
    global current
    global mode

    current = off
    print("LED is ", current)

    n = int(NUM_LEDS/2)
    r = range(n)
    sw = strip.write

    for i in r:
        strip[i] = (0, 0, 0)
        strip[NUM_LEDS-i-1] = (0, 0, 0)
        sw()

    mode = None

async def one_color(strip, val = (31,36,181)):
    global current
    global mode
    global BRIGHTNESS
    color = val

    color[0] = int(val[0]*BRIGHTNESS)
    color[1] = int(val[0]*BRIGHTNESS)
    color[2] = int(val[0]*BRIGHTNESS)

    current = one_color
    print("LED is ", current)

    n = int(NUM_LEDS/2)
    r = range(n)
    sw = strip.write

    for i in r:
        strip[i] = val
        strip[NUM_LEDS-i-1] = val
        sw()

    #current = None
    mode = None

async def kleiderschrank(strip):
    global current
    global mode

    current = kleiderschrank

    for i in range(0,NUM_LEDS-1):
        strip[i] = (0,0,0)
    print("Strip cleared!")

    strip.write()

    
    print("LED is ", current)

    start = 149
    end = 299
    color = (200,200,200)

    for i in range(end, start, 1):
        strip[i] = color
        strip.write()

    mode = None

async def film(strip):
    global current 
    global mode
    global BRIGHTNESS

    current = film
    color = (int(163 * BRIGHTNESS), int(92 * BRIGHTNESS), int(11 * BRIGHTNESS)) #bedge
    print(color)
    end = 299
    i = 0
    while i <= end:
        for j in range(i, i+10, 1):
            strip[j] = color
            strip.write()
        i = i + 30
        

    mode = None

async def platsch(strip):
    global current 
    global mode

    current = platsch

    #Random werte die sich wiederholen, wir teilen die Anzahl durch 4
    rand = [12,40,149,70,0,3,55,23,120]
    color = (76, 157, 166)
    interval = 50

    while True:
        for r in rand:
            strip[r] = color
            strip.write()
            #check for cancel
            await asyncio.sleep(.5)
            if current is not mode:
                print("Turn off platsch")
                return 0
            print("running platshc blin")
            for i in range(interval):
                for l in range(NUM_LEDS-10):
                    if strip[l+1] == color:
                        strip[l] = (color)
                        if strip[l+6] == color:
                            strip[l+3] = (0, 0, 0)
                strip.write()



async def rainbow(strip):
    print("Im alive")
    global current 
    global mode

    current = rainbow
    print("LED is ", current)

    w = wheel
    rj = range(256)
    ri = range(NUM_LEDS)
    sr = strip.write
    res = 0
    while True:
        for j in rj:

            if current is not mode:
                print("Turn off rainbow")
                return 0
            for i in ri:
                strip[i] = w((i + j) & 255)
            sr()
            await asyncio.sleep(.5)
            print("running")
            
        
       

def wheel(offset = 0):
    # The colours are a transition r - g - b - back to r
    offset = 255 - offset
    if offset < 85:
        return (255 - offset * 3, 0, offset * 3)
    if offset < 170:
        offset -= 85
        return (0, offset * 3, 255 - offset * 3)
    offset -= 170
    return (offset * 3, 255 - offset * 3, 0,)   


#loop

strip[0] = (50,50,50)
strip.write()

try:
    asyncio.run(main(client, strip))
finally:
    client.close()  # Prevent LmacRxBlk:1 errors
