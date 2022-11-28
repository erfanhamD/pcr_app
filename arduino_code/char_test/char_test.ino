float voltage = 1.15;
float tempC = 1.30;
int BT = 10;
char com[50];

void setup() {
  Serial.begin(9600);

}
void loop() {
  sprintf(com, "%f, %f, %d", voltage, tempC, BT);
  Serial.println(com);
  }
