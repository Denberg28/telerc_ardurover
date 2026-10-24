# TeleRC ArduRover firmware

Current development baseline: **1.1.0rc1**, combining scalable LoRa **0.4.0rc1**
and ESP32-S3 four-BTS7960 PWM converter **1.0.5**. See [baseline setup and limits](docs/BASELINE.md).
The same LoRa sketch set supports manual and PC MAVLink mission sessions.
Public LoRa examples are RF-OFF; generate a matching private network before use.
The private 20-rover bundle remains separate and must never be committed here.

This is a candidate baseline; physical combined-system qualification is pending.
[Download the combined baseline](https://github.com/Denberg28/telerc_ardurover/releases/tag/firmware-baseline-v1.1.0rc1).

## Historical source sets


Latest sketch sources transferred on 21 October 2026. Required headers are included. No historical releases or compiled binaries are included.

| Folder | Firmware | Source |
| --- | --- | --- |
| `TeleRC_4x_BTS7960_PWM_GlitchFilter` | ESP32-S3 four-driver PWM converter 1.0.5 | PC TeleRC 0.1.5rc3 source package |
| `lora/manual/TeleRCLoRa_BASE` | Current manual-control BASE | PC TeleRC 0.1.5rc3 source package |
| `lora/manual/TeleRCLoRa_ROVER` | Current manual-control ROVER | Same matching source set |
| `lora/manual/TeleRCLoRa_NODE` | Current manual-control relay NODE | Same matching source set |
| `lora/mission/sketches` | Mission 0.2.0rc1 BASE, ROVER_001, NODE_1 and NODE_2 | Latest PC TeleRC Mission 0.1.5rc3 package |

The manual and mission folders are distinct protocols; use one matching complete set. Mission is for the PC Mission workflow, not joystick driving. Public mission examples are deliberately unprovisioned (RF disabled). Generate private matching sketches with `python lora/mission/tools/provision.py --out ../TeleRC-private --rovers 1 --relays 0`. Never commit generated keys.

Open the .ino matching its enclosing folder in Arduino IDE. Use Arduino-ESP32 3.3.2 and RadioLib 7.2.1 for LilyGO T3-S3 SX1262. Preserve matching relay settings across BASE, ROVER and NODE. For the manual set, set TELERC_RELAY_COUNT consistently (0, 1 or 2), and NODE_INDEX per relay. Default examples use 915 MHz, 2 dBm; use settings permitted for your location and hardware.

This is a source migration with no control-logic changes. Source bytes and local includes were checked. Prior build evidence is retained by the source packages; no new hardware validation or stable promotion is claimed. SOURCE_MANIFEST.json records byte identity and origins. Existing source history is preserved in the original repositories and archives.
