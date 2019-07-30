""" A recordkeeping game, designed to measure the rate of an event.

The initial use case is in a production environment, producing X items every
Y minutes.  Rate display takes the form of a gauge, and total daily production 
up to 999 units can be displayed as coded lights.

Hardware used is an Adafruit Circuit Playground Express.  As configured, we 
utilize an external button and the count event occurs when we supply voltage
to pad A1, though the user can change the pad or find an alternate signaling
method.  A backup/demo mode can be accessed via moving the slider switch on the
CPX toward button A, allowing use of button A to signal a count.  The 
orientation is micro-USB port to the 'bottom' of the gauge.  

Goals can be set via the variables in the main() function.

Original work by R. Pfaff, licensed under the GNU GPLv3.0"""

import time
import board
import digitalio

from adafruit_circuitplayground.express import cpx

""" Set hardware initial state."""
tch_pd = board.A1
io_button = digitalio.DigitalInOut(tch_pd)
io_button.switch_to_input(pull=digitalio.Pull.DOWN)
cpx.red_led = False

def flash_once(color=(0,20,0)):
    """ A single flash of all lights."""
    
    cpx.pixels.fill(color)
    time.sleep(0.1)
    cpx.pixels.fill((0,0,0))

def spin_lights(color=(255,255,255)):
    """ A display of two opposing lights, rotating around the CPX."""
    
    for i in range(10):
        for x in range(5):
            cpx.pixels.fill((0,0,0))
            cpx.pixels[x] = color
            cpx.pixels[x+5] = color
    cpx.pixels.fill((0,0,0))

def strip_old(r_tot, now, record_period):
    """ Remove old timestamps from the rolling total."""

    if len(r_tot) > 0 and r_tot[0] < (now - record_period):
        r_tot.pop(0)
    return r_tot

def set_color(i):
    """ Set a color gradient to illuminate a gauge from red through green.
    
    End user can feel free to adjust color schemes to whatever."""
    
    if i >= 8:
        return (0, 255, 0)
    elif i == 7:
        return (100, 255, 0)
    elif i == 6:
        return (175, 255, 0)
    elif i == 5 or i == 4:
        return (255, 255, 0)
    elif i == 3:
        return (255, 180, 0)
    elif i == 2:
        return (255, 100, 0)
    elif i <= 1:
        return (255, 0, 0)

def show_day_total(total):
    """ Use the neopixels to display a daily total.
    
    As configured, color codes are as follows:
        Hundreds digit: Green
        Tens digit: Yellow
        Ones digit: Red
        Zeros for tens and ones (ie, 100) are represented by
        a placeholder of 3 flashes of the red status LED."""

    # Establish display schemes
    def show_digit(d, color):
        for i in range(d):
            cpx.pixels[i] = color
        time.sleep(3)
        cpx.pixels.fill((0,0,0))
    
    def blink_red():
        for i in range(3):
            cpx.red_led = True
            time.sleep(0.75)
            cpx.red_led = False
            time.sleep(0.75)

    # Blank the display
    cpx.pixels.fill((0,0,0))
    time.sleep(1)
    
    # Find each digit
    d3 = total // 100
    if d3 > 10: d3 = 10
    d2 = (total - (d3 * 100)) // 10
    d1 = total - (d3 * 100) - (d2 * 10)
    
    # Show hundreds
    if d3 > 0:
        show_digit(d3, (0,255,0)) # Edit this for a different color

    # Show tens or placeholder
    if d2 > 0:
        show_digit(d2, (255,255,0)) # Edit this for a different color
    elif d2 == 0 and d3 > 0:
        blink_red()

    # Show ones or placeholder
    if d1 > 0:
        show_digit(d1, (255,0,0)) # Edit this for a different color
    elif d1 == 0:
        blink_red()

def main():
    """ The overall driver for the gauge application."""
    
    # Set initial variables
    t1 = time.monotonic() # Set a baseline time so we can reset daily.
    rolling_total = []
    day_total = 0
    goal_display = False
    
    # These variables will contain option settings for the gauge.
    goal = 120 # Production goal PER RECORD PERIOD, not the daily goal.
    gauge_intensity = 0.20 # Effectively a dimmer for the gauge.
    record_period = (60 * 60) # Number of seconds before data is discarded.

    while True:
        t_now = time.monotonic() # Grab current time.
        pct_achieved = int((sum([1 for e in rolling_total]) / goal) * 10)
        
        # Turn on neopixels based on the value of pct_achieved.
        # We are using a reverse index order, so that the gauge 'fills' clockwise
        # starting at the lower left.
        for i in range(0,10):
            if i < pct_achieved and pct_achieved > 0:
                cpx.pixels[9 - i] = tuple(map(lambda x: round(x * gauge_intensity), set_color(i)))
            else:
                cpx.pixels[9 - i] = (0,0,0)
        
        # Use the slider switch to toggle GPIO or button mode
        if cpx.switch:
            if cpx.button_a: #io_button.value:
                flash_once()
                rolling_total.append(t_now)
                day_total += 1
                time.sleep(0.5)
        else:
            # Reset the digital io pin
            io_button.pull = digitalio.Pull.DOWN
            if io_button.value:
                flash_once()
                rolling_total.append(t_now)
                day_total += 1
                time.sleep(0.5)
                
        # Use B button to display totals
        if cpx.button_b:
            show_day_total(day_total)
        
        # Get rid of values older than than the record period.
        rolling_total = strip_old(rolling_total, t_now, record_period)
        
        # Reset count every 24 hours.
        if t1 > (60 * 60 * 24):
            main()
            
        # Make a celebratory display once when goal is achieved.
        if len(rolling_total) >= goal and goal_display == False:
            spin_lights()
            goal_display = True
        elif len(rolling_total) < goal:
            goal_display = False
            
        time.sleep(0.1)

main()

