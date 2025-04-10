/******************************************************************************
Flex_Sensor_Example.ino - Updated for 3 Flex Sensors on Separate Breadboards
Example sketch for SparkFun's flex sensors
  (https://www.sparkfun.com/products/10264)
Jim Lindblom @ SparkFun Electronics
Updated by [Your Name] - March 2025
******************************************************************************/

const int FLEX_PINS[3] = {A0, A1, A2}; // Pins connected to voltage divider outputs on each breadboard

// Measure the voltage at 5V and the actual resistance of your
// 47k resistor, and enter them below:
const float VCC = 4.98; // Measured voltage of Arduino 5V line
const float R_DIV = 47500.0; // Measured resistance of 3.3k resistor

// Upload the code, then try to adjust these values to more
// accurately calculate bend degree.
const float STRAIGHT_RESISTANCE = 37300.0; // resistance when straight
const float BEND_RESISTANCE = 90000.0; // resistance at 90 deg

void setup() 
{
  Serial.begin(9600);
  for (int i = 0; i < 3; i++) {
    pinMode(FLEX_PINS[i], INPUT);
  }
}

void loop() 
{
  for (int i = 0; i < 3; i++) {
    // Read the ADC, and calculate voltage and resistance from it
    int flexADC = analogRead(FLEX_PINS[i]);
    float flexV = flexADC * VCC / 1023.0;
    float flexR = R_DIV * (VCC / flexV - 1.0);
    Serial.print("Breadboard ");
    Serial.print(i + 1);
    Serial.println(" Resistance: " + String(flexR) + " ohms");

    // Use the calculated resistance to estimate the sensor's bend angle:
    float angle = map(flexR, STRAIGHT_RESISTANCE, BEND_RESISTANCE, 0, 90.0);
    Serial.print("Breadboard ");
    Serial.print(i + 1);
    Serial.println(" Bend: " + String(angle) + " degrees");
    Serial.println();
  }

  delay(500);
}
