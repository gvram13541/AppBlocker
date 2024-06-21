import asyncio
from asyncio.subprocess import PIPE
from datetime import datetime
import streamlit as st

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

async def process_device(device_id, apps_to_block, action):
    results = []
    if action == "block":
        foreground_app, app_info = await get_foreground_app(device_id)
        results.append(f"Device {device_id}: {app_info}")
        if foreground_app:
            block_result = await block_app(device_id, foreground_app, apps_to_block)
            if block_result:
                results.append(block_result)
    elif action == "unblock":
        for app in apps_to_block:
            unblock_result = await unblock_app(device_id, app)
            results.append(unblock_result)
    return results

async def main(apps_to_block, device_ids, action):
    if not device_ids:
        return "No devices selected"

    tasks = [process_device(device_id, apps_to_block, action) for device_id in device_ids]
    results = await asyncio.gather(*tasks)
    
    flat_results = [item for sublist in results for item in sublist]
    return "\n".join(flat_results)

def run_blocking(apps_to_block, device_ids):
    result = asyncio.run(main(apps_to_block, device_ids, action="block"))
    
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

def unblock_apps(apps_to_block, device_ids):
    result = asyncio.run(main(apps_to_block, device_ids, action="unblock"))
    return result