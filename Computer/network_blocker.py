import asyncio
import winrm

async def block_on_remote(ip_addr, username, password, resource_name):
    session = winrm.Session(ip_addr, auth=(username, password))
    try:
        script = f"New-NetFirewallRule -DisplayName '{resource_name}' -Direction Outbound -Action Block -RemoteAddress Any -Program '%ProgramFiles%\{resource_name}\{resource_name}.exe'"
        response = session.run_ps(script)
        return f"Successfully blocked {resource_name} on {ip_addr}"
    except Exception as e:
        return f"Error blocking {resource_name} on {ip_addr}: {str(e)}"

async def unblock_on_remote(ip_addr, username, password, resource_name):
    session = winrm.Session(ip_addr, auth=(username, password))
    try:
        script = f"Remove-NetFirewallRule -DisplayName '{resource_name}'"
        response = session.run_ps(script)
        return f"Successfully unblocked {resource_name} on {ip_addr}"
    except Exception as e:
        return f"Error unblocking {resource_name} on {ip_addr}: {str(e)}"

async def process_computers(computers, username, password, resources, action):
    tasks = []
    for ip_addr in computers:
        for resource in resources:
            if action == "block":
                tasks.append(block_on_remote(ip_addr, username, password, resource))
            else:
                tasks.append(unblock_on_remote(ip_addr, username, password, resource))
    results = await asyncio.gather(*tasks)
    return "\n".join(results)

def run_blocking(computers, username, password, resources):
    result = asyncio.run(process_computers(computers, username, password, resources, action="block"))
    return result

def unblock_resources(computers, username, password, resources):
    result = asyncio.run(process_computers(computers, username, password, resources, action="unblock"))
    return result