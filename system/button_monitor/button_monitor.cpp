#include <iostream>
#include <mraa.hpp>
#include <unistd.h>

const int buttonPin = 7; // Replace with the actual GPIO pin where your button is connected
const int shutdownDuration = 3; // Duration in seconds to trigger shutdown

void shutdown() {
    std::cout << "Performing system shutdown..." << std::endl;
    system("/home/rock/OrangeBox/scripts/shutdown.sh");
}

int main() {
    mraa::Result status;
    mraa::Gpio button(buttonPin);
    status = button.dir(mraa::DIR_IN);
    if (status != mraa::SUCCESS) {
        printError(status);
        return 1;
    }

    // Variables to keep track of button state and time
    bool buttonPressed = false;
    time_t buttonPressStartTime = 0;

    while (true) {
        // Read the button state
        int buttonState = button.read();

        if (buttonState == 1) {
            // Button is pressed
            if (!buttonPressed) {
                // Record the time when the button is first pressed
                buttonPressStartTime = time(nullptr);
                buttonPressed = true;
            } else {
                // Check if the button has been pressed for the desired duration
                time_t currentTime = time(nullptr);
                if (currentTime - buttonPressStartTime >= shutdownDuration) {
                    // Button has been pressed for 3 seconds or longer, exit the loop and proceed to shutdown.
                    break;
                }
            }
        } else {
            // Button is not pressed
            buttonPressed = false;
        }

        // Sleep for a short duration to avoid continuous checking
        usleep(100000); // 100 ms
    }

    shutdown();
    
    return 0;
}
