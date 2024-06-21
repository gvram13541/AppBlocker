# import asyncio
# import subprocess
# from asyncio.subprocess import PIPE
# import socket

# async def get_adb_devices():
#     process = await asyncio.create_subprocess_exec(
#         'adb', 'devices',
#         stdout=PIPE, stderr=PIPE
#     )
#     stdout, stderr = await process.communicate()
#     output = stdout.decode('utf-8')
#     devices = []
#     for line in output.split('\n')[1:]:
#         if '\tdevice' in line:
#             devices.append(line.split('\t')[0])
#     return devices

# async def get_foreground_app(device_id):
#     try:
#         process = await asyncio.create_subprocess_exec(
#             'adb', '-s', device_id, 'shell', 'dumpsys', 'activity', 'activities',
#             stdout=PIPE, stderr=PIPE
#         )
#         stdout, stderr = await process.communicate()
#         output = stdout.decode('utf-8')
#         for line in output.split('\n'):
#             if 'mResumedActivity' in line:
#                 package_name = line.split()[3].split('/')[0]
#                 return package_name, line
#         return None, "No foreground app found"
#     except Exception as e:
#         return None, f"Error: {e}"

# async def block_app(device_id, package_name, apps_to_block):
#     if package_name in apps_to_block:
#         try:
#             process = await asyncio.create_subprocess_exec(
#                 'adb', '-s', device_id, 'shell', 'am', 'force-stop', package_name,
#                 stdout=PIPE, stderr=PIPE
#             )
#             stdout, stderr = await process.communicate()
            
#             if process.returncode != 0:
#                 process = await asyncio.create_subprocess_exec(
#                     'adb', '-s', device_id, 'shell', 'pm', 'disable-user', '--user', '0', package_name,
#                     stdout=PIPE, stderr=PIPE
#                 )
#                 stdout, stderr = await process.communicate()
            
#             if process.returncode == 0:
#                 return f"Blocked app: {package_name}"
#             else:
#                 return f"Error blocking {package_name}: {stderr.decode('utf-8')}"
#         except Exception as e:
#             return f"Error blocking {package_name}: {e}"
#     return None

# async def unblock_app(device_id, package_name):
#     try:
#         process = await asyncio.create_subprocess_exec(
#             'adb', '-s', device_id, 'shell', 'pm', 'enable', '--user', '0', package_name,
#             stdout=PIPE, stderr=PIPE
#         )
#         stdout, stderr = await process.communicate()
#         if process.returncode == 0:
#             return f"Unblocked app: {package_name}"
#         else:
#             return f"Error unblocking {package_name}: {stderr.decode('utf-8')}"
#     except Exception as e:
#         return f"Error unblocking {package_name}: {e}"

# async def process_device(device_id, apps_to_block):
#     results = []
#     foreground_app, app_info = await get_foreground_app(device_id)
#     results.append(f"Device {device_id}: {app_info}")
#     if foreground_app:
#         block_result = await block_app(device_id, foreground_app, apps_to_block)
#         if block_result:
#             results.append(block_result)
#     return results

# async def main(apps_to_block, device_ids):
#     if not device_ids:
#         return "No devices selected"

#     tasks = [process_device(device_id, apps_to_block) for device_id in device_ids]
#     results = await asyncio.gather(*tasks)
    
#     flat_results = [item for sublist in results for item in sublist]
#     return "\n".join(flat_results)

# def run_blocking(apps_to_block, device_ids):
#     return asyncio.run(main(apps_to_block, device_ids))

# def get_local_ip():
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     try:
#         s.connect(('10.255.255.255', 1))
#         IP = s.getsockname()[0]
#     except Exception:
#         IP = '127.0.0.1'
#     finally:
#         s.close()
#     return IP


import asyncio
import subprocess
from asyncio.subprocess import PIPE
import socket
from datetime import datetime
import streamlit as st

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

async def get_foreground_app(device_id):
    try:
        process = await asyncio.create_subprocess_exec(
            'adb', '-s', device_id, 'shell', 'dumpsys', 'activity', 'activities',
            stdout=PIPE, stderr=PIPE
        )
        stdout, stderr = await process.communicate()
        output = stdout.decode('utf-8')
        for line in output.split('\n'):
            if 'mResumedActivity' in line:
                package_name = line.split()[3].split('/')[0]
                return package_name, line
        return None, "No foreground app found"
    except Exception as e:
        return None, f"Error: {e}"

async def block_app(device_id, package_name, apps_to_block):
    if package_name in apps_to_block:
        try:
            process = await asyncio.create_subprocess_exec(
                'adb', '-s', device_id, 'shell', 'am', 'force-stop', package_name,
                stdout=PIPE, stderr=PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                process = await asyncio.create_subprocess_exec(
                    'adb', '-s', device_id, 'shell', 'pm', 'disable-user', '--user', '0', package_name,
                    stdout=PIPE, stderr=PIPE
                )
                stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return f"Blocked app: {package_name}"
            else:
                return f"Error blocking {package_name}: {stderr.decode('utf-8')}"
        except Exception as e:
            return f"Error blocking {package_name}: {e}"
    return None

async def unblock_app(device_id, package_name):
    try:
        process = await asyncio.create_subprocess_exec(
            'adb', '-s', device_id, 'shell', 'pm', 'enable', '--user', '0', package_name,
            stdout=PIPE, stderr=PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode == 0:
            return f"Unblocked app: {package_name}"
        else:
            return f"Error unblocking {package_name}: {stderr.decode('utf-8')}"
    except Exception as e:
        return f"Error unblocking {package_name}: {e}"

async def process_device(device_id, apps_to_block):
    results = []
    foreground_app, app_info = await get_foreground_app(device_id)
    results.append(f"Device {device_id}: {app_info}")
    if foreground_app:
        block_result = await block_app(device_id, foreground_app, apps_to_block)
        if block_result:
            results.append(block_result)
    return results

async def main(apps_to_block, device_ids):
    if not device_ids:
        return "No devices selected"

    tasks = [process_device(device_id, apps_to_block) for device_id in device_ids]
    results = await asyncio.gather(*tasks)
    
    flat_results = [item for sublist in results for item in sublist]
    return "\n".join(flat_results)

def run_blocking(apps_to_block, device_ids):
    result = asyncio.run(main(apps_to_block, device_ids))
    
    # Log the blocking action
    if 'blocking_history' not in st.session_state:
        st.session_state['blocking_history'] = []
    
    st.session_state['blocking_history'].append({
        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'Devices': ', '.join(device_ids),
        'Blocked Apps': ', '.join(apps_to_block),
        'Result': result
    })
    
    return result

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

async def get_installed_apps(device_id):
    try:
        process = await asyncio.create_subprocess_exec(
            'adb', '-s', device_id, 'shell', 'pm', 'list', 'packages',
            stdout=PIPE, stderr=PIPE
        )
        stdout, stderr = await process.communicate()
        output = stdout.decode('utf-8')
        return [line.split(':')[1].strip() for line in output.split('\n') if line]
    except Exception as e:
        print(f"Error getting installed apps: {e}")
        return []

async def get_app_usage_stats(device_id):
    try:
        # Get usage stats for the last 24 hours
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = end_time - (24 * 60 * 60 * 1000)  # 24 hours in milliseconds
        
        process = await asyncio.create_subprocess_exec(
            'adb', '-s', device_id, 'shell', 'dumpsys', 'usagestats', '--hours', '24',
            stdout=PIPE, stderr=PIPE
        )
        stdout, stderr = await process.communicate()
        output = stdout.decode('utf-8')
        
        usage_stats = {}
        current_package = None
        for line in output.split('\n'):
            if line.startswith('    Package:'):
                current_package = line.split()[1]
            elif line.strip().startswith('totalTime'):
                if current_package:
                    time_ms = int(line.split()[-1])
                    usage_stats[current_package] = time_ms
                    current_package = None
        
        return usage_stats
    except Exception as e:
        print(f"Error getting app usage stats: {e}")
        return {}