/******************************************************************************
Flex_Sensor_Example.ino - Calibrated for 4 Flex Sensors
******************************************************************************/

const int FLEX_PINS[4] = {A0, A1, A2, A3};
const char* DIRECTIONS[4] = {"North", "East", "South", "West"};

const float VCC = 4.98;
const float R_DIV = 47500.0;

const float STRAIGHT_RESISTANCE = 37300.0;
const float BEND_RESISTANCE = 90000.0;

// Array to store the baseline resistance for each sensor
float baselineResistance[4];

void setup() 
{
  Serial.begin(9600);
  for (int i = 0; i < 4; i++) {
    pinMode(FLEX_PINS[i], INPUT);
  }

  // Take initial readings for calibration
  Serial.println("Calibrating sensors...");
  delay(1000); // Let things stabilize
  for (int i = 0; i < 4; i++) {
    int flexADC = analogRead(FLEX_PINS[i]);
    float flexV = flexADC * VCC / 1023.0;
    baselineResistance[i] = R_DIV * (VCC / flexV - 1.0);
    Serial.print("Sensor ");
    Serial.print(i + 1);
    Serial.print(" ");
    Serial.print(DIRECTIONS[i]);
    Serial.print(" Baseline: ");
    Serial.println(baselineResistance[i]);
  }
  Serial.println("Calibration complete.\n");
}

void loop() 
{
  for (int i = 0; i < 4; i++) {
    int flexADC = analogRead(FLEX_PINS[i]);
    float flexV = flexADC * VCC / 1023.0;
    float flexR = R_DIV * (VCC / flexV - 1.0);

    float calibratedR = flexR - baselineResistance[i];

    float angle = map(flexR, STRAIGHT_RESISTANCE, BEND_RESISTANCE, 0, 90.0);
    float calibratedAngle = map(calibratedR, 0, BEND_RESISTANCE - STRAIGHT_RESISTANCE, 0, 90.0);

    Serial.print("Sensor ");
    Serial.print(i + 1);
    Serial.print(" ");
    Serial.print(DIRECTIONS[i]);
    Serial.print(" | Raw Angle: ");
    Serial.print(angle);
    Serial.print("°, Calibrated Angle: ");
    Serial.print(calibratedAngle);
    Serial.println("°");

    delay(100);
  }

  Serial.println();
  delay(500);
}
