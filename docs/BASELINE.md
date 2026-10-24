# TeleRC ArduRover baseline 1.1.0rc1

This is the new development baseline: scalable LoRa 0.4.0rc1 plus the unchanged
ESP32-S3 four-BTS7960 PWM converter 1.0.5. PC TeleRC v1.0.1 remains the stable
desktop application. This firmware baseline is a release candidate; combined
physical RF, motor, takeover and failsafe qualification is still required.

## Upload order and board roles

1. Keep the vehicle disarmed and motor power isolated during upload and setup.
2. Upload the matching BASE sketch to a LilyGO T3-S3 SX1262 connected to the PC.
3. Upload the corresponding ROVER sketch to each LilyGO radio on its vehicle.
   Set the flight controller's SYSID_THISMAV to the same rover number, 1–20.
4. Upload distinct matching NODE sketches to optional LilyGO relays.
5. Upload `TeleRC_4x_BTS7960_PWM_GlitchFilter.ino` to the separate ESP32-S3
   motor converter on each rover. The converter is identical across all rovers;
   it has no rover number or pairing key.

The ROVER radio connects to the flight controller by MAVLink UART at 115200:
radio TX43 to FC RX, radio RX44 to FC TX, and common ground. The motor converter
receives the FC's four PWM outputs; it does not receive MAVLink from the radio.

| FC output | Required SERVO function | Converter input | Motor | RPWM / LPWM |
| --- | --- | --- | --- | --- |
| M5 | SERVO5_FUNCTION=73 | GPIO4 | Front left | GPIO8 / GPIO9 |
| M6 | SERVO6_FUNCTION=73 | GPIO5 | Rear left | GPIO10 / GPIO11 |
| M7 | SERVO7_FUNCTION=74 | GPIO6 | Front right | GPIO12 / GPIO13 |
| M8 | SERVO8_FUNCTION=74 | GPIO7 | Rear right | GPIO14 / GPIO15 |

Use 3.3 V compatible signals and common grounds. Never apply 5 V to ESP32 GPIO.
Check BTS7960 enable wiring, power distribution, motor direction, FC output
configuration, receiver priority and the independent physical cutoff before
applying traction power. Uploading these sketches does not configure FC parameters.

## One matching network

The public release contains keyless RF-OFF LoRa examples and a private provisioner.
Generate a network outside this repository with the included setup tool. Keep the
saved `NETWORK.private.json` and generated sketches private. The separate private
20-rover bundle retains the pairing keys from the previously delivered bundle.
Do not replace its project by running a fresh initialization.

Rovers 1–20 are already supported by the BASE key table. Add a new NODE ID 1–200
using the saved private project; existing BASE/ROVER/NODE firmware need not change.
Never run duplicate physical identities. A node number is an identity, not its
position along a route. The maximum active path is two relay hops. Namespace
size does not establish simultaneous RF capacity.

LoRa TU2 cannot communicate with TU1 unified, older manual, TM2-only or TF2 fleets.
Migrate a complete matching network once. Historical `lora/manual` and
`lora/mission` sources remain available in this repository for rollback; they are
not the new baseline and are not mixed into its release archive.

## Operation and limits

The same BASE/ROVER firmware supports PC manual USB and PC mission USB sessions.
PC TeleRC v1.0.1 manual wheel/keyboard control addresses rover 1 only. Mission
planning addresses one selected rover 1–20 at a time. This is not simultaneous
20-rover driving or monitoring. Mission upload/start is commanded from PC TeleRC
over MAVLink; a transmitter mode switch can select an already loaded onboard AUTO
mission according to FC configuration, but does not create/upload a PC mission.
Use one active BASE per network.

Authenticated route discovery does not arm or enable driving. Reconnection
requires the normal fresh neutral input and explicit control-enable/mission
confirmation. The existing 500 ms radio manual watchdog, 150 ms converter input
loss stop and 300 ms converter neutral recovery remain unchanged. FC arming,
receiver takeover and GCS failsafes must be configured independently. The PWM
converter has no separate armed-state input.

## Build and evidence

Pinned Arduino CLI 1.3.1, Arduino-ESP32 3.3.2 and RadioLib 7.2.1.

- LilyGO: `esp32:esp32:lilygo_t3s3:Revision=Radio_SX1262,PSRAM=disabled,USBMode=hwcdc,CDCOnBoot=cdc`
- Converter: `esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=hwcdc,FlashSize=4M,PartitionScheme=default,PSRAM=disabled,FlashMode=dio`

The release workflow runs focused enrollment/routing checks, actual role host
sanitizers, eight converter sanitizer variants, PC v1.0.1 serial-driver handshakes,
ten LilyGO target builds and one ESP32-S3 converter target build. Release assets
are scanned for private profiles and downloaded back for checksum verification.
`BUILD_REPORT.json` records the exact baseline commit and target results. The
private bundle separately preserves all 24 exact-profile LilyGO build records.
Automated checks do not measure physical RF or motor failsafe behavior.

See `lora/scalable/HARDWARE_TEST.md` for the remaining field qualification.
