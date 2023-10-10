#ifndef  MULTIBLINKH
#define  MULTIBLINKH

// #define TESTING

#include <stdlib.h>
#include <stdint.h>
#include <iostream>
#include <thread>
#include <fstream>
#include <string>
#include <chrono>
#include <sys/types.h>
#include <sys/stat.h>
#include <signal.h>
#include <unistd.h>
#include <fcntl.h>
#include <chrono>

#ifndef TESTING
#include "mraa/common.hpp"
#include "mraa/gpio.hpp"
#endif

// State values for FSM
#define  MB_NULL  0
#define  MB_LOW   1
#define  MB_HIGH  2
#define  MB_LOOP  3

#define  LOOP_UNDEF  255

typedef struct
{
  uint8_t  activeVal;     // state value for this state to be active (MB_* defines)
  uint16_t activeTime;    // time to stay active in this state stay in milliseconds or loop counter 
  uint8_t  nextState;     // If MB_LOOP this is the state to loop back/forward to 
} stateDef;

typedef struct
{
  uint8_t  ledPin;         // Arduino I/O pin number
  uint8_t  currentState;   // current active state
  uint8_t  currentLoop;    // current position in the cycle
  stateDef state[4];       // the MB_* state definitions. Add more states if required
  uint32_t nextWakeup;     // the 'time' for the next wakeup - saves the millis() value
} ledTable;

// Dummy function to simulate the Arduino digitalWrite() function
void consoleWrite(int pin, int val)
{
	char c = (val) ? '*' : ' ';
	std::cout << ' ' << c << '\r' << std::flush;
}

// Function to simulate millis() function
template <
    class result_t   = std::chrono::milliseconds,
    class clock_t    = std::chrono::steady_clock,
    class duration_t = std::chrono::milliseconds
>
std::chrono::milliseconds millis(std::chrono::time_point<clock_t, duration_t> const& start)
{
    return std::chrono::duration_cast<result_t>(clock_t::now() - start);
}

#endif