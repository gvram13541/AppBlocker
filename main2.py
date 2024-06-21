import asyncio
import subprocess
from asyncio.subprocess import PIPE

# List of devices (IP addresses and ports)
DEVICES = [
    # "192.168.1.100:5555",
    # "192.168.1.101:5555",
    # Add more devices as needed
    "10.20.1.18:41355"
]

async def get_foreground_app(device):
    try:
        process = await asyncio.create_subprocess_exec(
            'adb', '-s', device, 'shell', 'dumpsys', 'activity', 'activities',
            stdout=PIPE, stderr=PIPE
        )
        stdout, stderr = await process.communicate()
        output = stdout.decode('utf-8')
        
        for line in output.split('\n'):
            if 'mResumedActivity' in line:
                print(line)
                package_name = line.split()[3].split('/')[0]
                return package_name
    except Exception as e:
        print(f"Error: {e}")
    return None

async def block_app(device, package_name):
    if package_name in ['com.whatsapp', 'com.google.android.youtube']:
        try:
            process = await asyncio.create_subprocess_exec(
                'adb', '-s', device, 'shell', 'am', 'force-stop', package_name,
                stdout=PIPE, stderr=PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode == 0:
                print(f"Blocked app: {package_name} on device {device}")
            else:
                print(f"Error: {stderr.decode('utf-8')}")
        except Exception as e:
            print(f"Error: {e}")

async def main():
    while True:
        tasks = []
        for device in DEVICES:
            foreground_app = await get_foreground_app(device)
            print(f"The foreground app for device {device} is: {foreground_app}")
            if foreground_app:
                tasks.append(block_app(device, foreground_app))
        
        await asyncio.gather(*tasks)
        await asyncio.sleep(5)  # Wait for 5 seconds before checking again

if __name__ == "__main__":
    asyncio.run(main())