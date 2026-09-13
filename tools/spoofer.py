import time
import asyncio
from pymobiledevice3.lockdown import create_using_usbmux
from pymobiledevice3.exceptions import NoDeviceConnectedError

async def check_device():
    try:
        # Attempt to connect to the device via USB multiplexer
        lockdown = await create_using_usbmux()
        
        # Successfully connected
        print("\n✅ Success! Connected to iOS Device:")
        print(f"📱 Model:   {lockdown.product_type}")
        print(f"🍏 iOS:     {lockdown.product_version}")
        print(f"🔑 UDID:    {lockdown.udid}")
        
        print("\nNext step: We will configure the location spoofer for this device.")
        return True
        
    except NoDeviceConnectedError:
        print("\n❌ No iOS device detected.")
        print("Please ensure:")
        print("1. Your iPhone is plugged into your Mac via USB.")
        print("2. You have unlocked the phone.")
        print("3. You have tapped 'Trust This Computer' if prompted.")
        return False
    except Exception as e:
        print(f"\n⚠️ An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    print("Searching for connected iOS devices...")
    time.sleep(1)
    asyncio.run(check_device())
