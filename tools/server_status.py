import platform
import psutil
import mcp.types as types


def info():
    return types.Tool(
        name="System Info",
        description="Retrieve system information (CPU, memory, disk, etc.)",
        inputSchema={},
    )


async def handler() -> types.TextContent:
    try:
        cpu_count = psutil.cpu_count()
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        memory = psutil.virtual_memory()
        system_info = platform.uname()
        disk = psutil.disk_usage('/')
        net_io = psutil.net_io_counters()
        battery = psutil.sensors_battery()
        battery_info = f"Battery status: {battery.percent}%, {'Charging' if battery.power_plugged else 'On battery'}" if battery else "No battery information"

        info = f"""System Information:
                1. Operating System: {system_info.system} {system_info.release}
                2. Device Name: {system_info.node}
                3. CPU Info:
                   - CPU Core Count: {cpu_count}
                   - CPU Usage: {cpu_percent}
                4. Memory Info:
                   - Total Memory: {memory.total / (1024 ** 3):.2f}GB
                   - Used Memory: {memory.used / (1024 ** 3):.2f}GB
                   - Available Memory: {memory.available / (1024 ** 3):.2f}GB
                   - Usage: {memory.percent}%
                5. Disk Info (Root Directory):
                   - Total Space: {disk.total / (1024 ** 3):.2f}GB
                   - Used Space: {disk.used / (1024 ** 3):.2f}GB
                   - Free Space: {disk.free / (1024 ** 3):.2f}GB
                   - Usage: {disk.percent}%
                6. Network Info:
                   - Sent: {net_io.bytes_sent / (1024 ** 2):.2f}MB
                   - Received: {net_io.bytes_recv / (1024 ** 2):.2f}MB
                7. {battery_info}"""

        return types.TextContent(type="text", text=info)
    except Exception as e:
        return types.TextContent(type="text", text=f"Failed to retrieve system info: {str(e)}")
