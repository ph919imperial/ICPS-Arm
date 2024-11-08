/** @file emg-firmware.ino
 * 
 * @brief EMG test firmware.
 * 
 * @author ph919@ic.ac.uk
 */

// Modify this struct to change data sent to PC. remember to change the dtype in the python program as well.
struct data_t {
  float emg1_volt;
  float emg2_volt;
} data;

void setup() {
  Serial.begin(115200);
  while (!Serial)
    ;
}

void loop() {
  // Sample sensor.
  uint16_t emg1_adc = analogRead(A0);
  float emg1_volt = emg1_adc * (5.0 / 1023.0);

  uint16_t emg2_adc = analogRead(A0);
  float emg2_volt = emg2_adc * (2.5 / 1023.0);

  // Populate data structure.
  data.emg1_volt = emg1_volt;
  data.emg2_volt = emg2_volt;

  // Write data to serial.
  Serial.write((uint8_t*)&data, sizeof(data));
  delay(100);
}
