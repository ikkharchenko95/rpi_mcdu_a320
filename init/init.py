import os
import glob
from serial.tools import list_ports
from pick import pick
from dotenv import set_key


def get_serial_devices():
    """Finds all serial devices and matches themd with paths /dev/serial-by-id."""
    ports = list_ports.comports()
    by_id_path = "/dev/serial/by-id/*"
    by_id_links = glob.glob(by_id_path)

    devices = []

    for port in ports:
        # Skip inner Raspberry Pi (Bluetooth and GPIO)
        if "AMA" in port.device or "ttyS" in port.device:
            continue

        # Try to find good stable path by-id for this device
        persistent_path = port.device
        for link in by_id_links:
            if os.path.realpath(link) == os.path.realpath(port.device):
                persistent_path = link
                break

        # Build clear description for output to menu
        label = (
            f"🔌 {port.device} | {port.manufacturer or 'Unknown'} "
            f"- {port.description or 'No description'} "
            f"[SN: {port.serial_number or 'N/A'}]"
        )

        devices.append({
            "label": label,
            "path": persistent_path
        })

    return devices


def main():
    devices = get_serial_devices()

    if not devices:
        print("❌ Error: USB-Serial devices (Arduino) not found!")
        return

    # Custom style settings for menu
    title = (
        "==================================================\n"
        " Setting up Arduino for Raspberry Pi \n"
        " Choose Arduino device for keep its serial number in .env\n"
        "=================================================="
    )

    options = [d["label"] for d in devices]

    # Output interactive menu in console
    option, index = pick(
        options,
        title,
        indicator="=>",
        default_index=0
    )

    selected_device = devices[index]
    target_path = selected_device["path"]

    # Path to env file in cwd
    env_path = os.path.join(os.getcwd(), ".env")

    # Set env var
    set_key(env_path, "ARDUINO_PORT", target_path)

    print("\n" + "=" * 50)
    print("✅ Set up successfully!")
    print(f"Choosed: {option}")
    print(f"Stable /dev/serial-by-id path: {target_path}")
    print(f"Path saved in env file: {env_path}")
    print("=" * 50)


if __name__ == "__main__":
    main()