# CPX-Rate-Timer
A recordkeeping game, designed to measure the rate of an event.

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
