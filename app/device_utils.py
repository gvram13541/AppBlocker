import asyncio
from asyncio.subprocess import PIPE
import socket

async def get_adb_devices():
    process = await asyncio.create_subprocess_exec(
        'adb', 'devices',
        stdout=PIPE, stderr=PIPE
    )
    stdout, stderr = await process.communicate()
    output = stdout.decode('utf-8')
    devices = []
    for line in output.split('\n')[1:]:
        if '\tdevice' in line:
            devices.append(line.split('\t')[0])
    return devices

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP