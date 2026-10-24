"""Build the combined public baseline without distributing private test material."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

from release_safety import check_directory

ROOT = Path(__file__).resolve().parents[1]
NAME = 'TeleRC-ArduRover-Baseline-v1.1.0rc1'
PWM = 'TeleRC_4x_BTS7960_PWM_GlitchFilter'
FQBN = 'esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=hwcdc,FlashSize=4M,PartitionScheme=default,PSRAM=disabled,FlashMode=dio'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    provenance = json.loads((ROOT/'BASELINE_MANIFEST.json').read_text())
    for record in provenance['files']:
        if sha(ROOT/record['path']) != record['sha256']:
            raise ValueError('Pinned component changed: ' + record['path'])
    subprocess.run([sys.executable, str(ROOT/'lora/scalable/tools/build_candidate.py')], check=True)
    out = ROOT/'baseline-dist'
    out.mkdir()
    stage = out/NAME
    stage.mkdir()
    old_stage = ROOT/'scalable-dist/TeleRC-Scalable-LoRa-v0.4.0rc1'
    lora = stage/'lora/scalable'
    shutil.copytree(old_stage, lora)
    # These helpers publish the standalone PC-repository release, not this baseline.
    for name in ('build_candidate.py', 'publish.py'):
        (lora/'tools'/name).unlink()
    (lora/'SHA256SUMS.txt').unlink()
    shutil.copytree(ROOT/PWM, stage/PWM)
    shutil.copyfile(ROOT/'docs/BASELINE.md', stage/'START-HERE.md')
    shutil.copyfile(ROOT/'BASELINE_MANIFEST.json', stage/'BASELINE_MANIFEST.json')
    report = json.loads((lora/'BUILD_REPORT.json').read_text())
    for record in report['builds']:
        for image in record.get('images', []):
            image['file'] = 'lora/scalable/' + image['file']
    report.update(baseline_version='1.1.0rc1', source_commit=os.environ['GITHUB_SHA'],
        lora_version='0.4.0rc1', converter_version='1.0.5',
        status='RELEASE CANDIDATE', hardware_validation='NOT TESTED',
        focused_checks={'converter_sanitizer_variants': 8, 'role_native_profiles': 10,
            'pc_driver_source_commit': '07ddf07b5d465619123e69977d737b6420f56801',
            'pc_compatibility_tests': 3, 'enrollment_and_network_tests': 6,
            'public_package_boundary_tests': 14})
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(['arduino-cli', 'compile', '--fqbn', FQBN,
            '--output-dir', tmp, str(ROOT/PWM)], check=True)
        dest = stage/'binaries'/PWM
        dest.mkdir(parents=True)
        images = []
        for suffix, offset in (('.ino.bootloader.bin','0x0'),('.ino.partitions.bin','0x8000'),('.ino.bin','0x10000')):
            path = dest/(PWM+suffix)
            shutil.copyfile(Path(tmp)/path.name, path)
            images.append(dict(file=path.relative_to(stage).as_posix(), offset=offset,
                bytes=path.stat().st_size, sha256=sha(path)))
        boot = dest/'boot_app0.bin'
        shutil.copyfile(Path.home()/'.arduino15/packages/esp32/hardware/esp32/3.3.2/tools/partitions/boot_app0.bin', boot)
        images.append(dict(file=boot.relative_to(stage).as_posix(), offset='0xe000',
            bytes=boot.stat().st_size, sha256=sha(boot)))
        report['builds'].append(dict(role=PWM, profile='public', fqbn=FQBN, result='PASS', images=images))
    # LoRa image paths in the component report are relative to that component.
    report['component_reports'] = {'lora/scalable/BUILD_REPORT.json': 'LoRa image paths relative to lora/scalable'}
    (stage/'BUILD_REPORT.json').write_text(json.dumps(report, indent=2)+'\n')
    (stage/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.relative_to(stage).as_posix()+'\n'
        for p in sorted(stage.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.txt'))
    check_directory(stage)
    with zipfile.ZipFile(out/(NAME+'.zip'), 'w', zipfile.ZIP_DEFLATED) as writer:
        for p in sorted(stage.rglob('*')):
            if p.is_file(): writer.write(p, NAME+'/'+p.relative_to(stage).as_posix())
    shutil.copyfile(stage/'BUILD_REPORT.json', out/'BUILD_REPORT.json')
    shutil.copyfile(ROOT/'docs/BASELINE.md', out/'README.md')
    (out/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.name+'\n'
        for p in sorted(out.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt'))
    check_directory(out)
    print('PASS combined baseline: 10 LilyGO profiles and 1 ESP32-S3 converter')

if __name__ == '__main__':
    main()
