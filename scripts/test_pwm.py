"""Focused converter regression checks against the released sketch."""
from pathlib import Path
import os
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as temp:
    for api in (2, 3):
        for name in ('test_converter', 'test_power', 'test_dropouts', 'test_noise_recovery'):
            binary = Path(temp) / (name + str(api))
            subprocess.run(['g++', '-std=c++17', '-Wall', '-Wextra', '-Werror',
                '-fsanitize=address,undefined', '-fno-pie', '-no-pie',
                '-DARDUINO_USB_CDC_ON_BOOT=1', f'-DESP_ARDUINO_VERSION_MAJOR={api}',
                '-I' + str(ROOT/'tests/pwm'), str(ROOT/'tests/pwm'/f'{name}.cpp'),
                '-o', str(binary)], check=True)
            subprocess.run([str(binary)], check=True,
                env={**os.environ, 'ASAN_OPTIONS': 'detect_leaks=0'})
            print('PASS', name, 'ESP32 API', api, flush=True)
