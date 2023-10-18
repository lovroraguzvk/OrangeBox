#include <iostream>
#include <mraa.hpp>
#include <unistd.h>

const int buttonPin = 7; // Replace with the actual GPIO pin where your button is connected
const int shutdownDuration = 3; // Duration in seconds to trigger shutdown

void shutdown() {
    std::cout << "Performing system shutdown..." << std::endl;
    // Replace with the command to execute your custom shutdown script
    system("/path/to/your-custom-shutdown-script.sh");
}

int main() {
    mraa::Result initResult = mraa::Result::SUCCESS;
    mraa::Gpio button;

    // Initialize MRAA
    mraa::Result mraaInitResult = mraa::init();
    if (mraaInitResult != mraa::Result::SUCCESS) {
        std::cerr << "MRAA initialization failed. Error: " << mraaInitResult << std::endl;
        return 1;
    }

    // Initialize the button GPIO pin
    button = mraa::Gpio(buttonPin);
    initResult = button.dir(mraa::DIR_IN);
    if (initResult != mraa::Result::SUCCESS) {
        std::cerr << "Failed to initialize the button GPIO. Error: " << initResult << std::endl;
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

    // Clean up MRAA
    mraa::deinit();

    shutdown();
    
    return 0;
}
