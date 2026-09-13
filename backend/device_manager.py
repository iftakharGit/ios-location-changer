import asyncio
from pymobiledevice3.services.dvt.instruments.process_control import ProcessControl
import logging
from pymobiledevice3.services.dvt.instruments.dvt_provider import DvtProvider
from pymobiledevice3.services.dvt.instruments.location_simulation import LocationSimulation
from pymobiledevice3.remote import userspace_tunnel

class DeviceManager:
    def __init__(self):
        self.bundle_id = None
        self.connected = False
        self.intent_to_connect = False
        self.current_lat = None
        self.current_lng = None
        self.command_queue = None
        self.last_error = None
        self._task = None

    def connect(self, bundle_id=None):
        self.bundle_id = bundle_id
        self.intent_to_connect = True
        self.last_error = None
        if self.command_queue is None:
            self.command_queue = asyncio.Queue()
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self.spoofer_loop())

    def disconnect(self):
        self.intent_to_connect = False
        if self.command_queue:
            self.command_queue.put_nowait(("CLEAR",))

    def set_location(self, lat: float, lng: float):
        self.current_lat = lat
        self.current_lng = lng
        if self.command_queue:
            self.command_queue.put_nowait(("SET", lat, lng))
        
    def clear_location(self):
        self.current_lat = None
        self.current_lng = None
        if self.command_queue:
            self.command_queue.put_nowait(("CLEAR",))

    async def spoofer_loop(self):
        while self.intent_to_connect:
            await self._run_single_connection()

    async def _run_single_connection(self):
        try:
            self.connected = False
            logging.info("Establishing userspace DVT tunnel to iPhone...")
            rsd = await userspace_tunnel.establish_userspace_rsd(remotepairing_fallback=False)
            async with DvtProvider(rsd) as dvt, LocationSimulation(dvt) as location:
                await self._manage_location_session(location, dvt)
        except Exception as e:
            self.connected = False
            self.last_error = str(e)
            logging.exception(f"Spoofer loop disconnected: {e}")
            if self.intent_to_connect:
                logging.info("Retrying connection in 3 seconds...")
                await asyncio.sleep(3)

    async def _manage_location_session(self, location, dvt):
        logging.info("Spoofer tunnel ready and maintained!")
        self.connected = True
        self.last_error = None
        
        if self.bundle_id:
            try:
                async with ProcessControl(dvt) as pc:
                    await pc.launch(self.bundle_id)
                    logging.info(f"Auto-launched app: {self.bundle_id}")
            except Exception as e:
                logging.exception(f"Failed to auto-launch {self.bundle_id}: {e}")
                
        if self.current_lat is not None and self.current_lng is not None:
            await location.set(self.current_lat, self.current_lng)
        
        while self.intent_to_connect:
            try:
                cmd = await asyncio.wait_for(self.command_queue.get(), timeout=1.0)
                if cmd[0] == "CLEAR":
                    logging.info("Restoring real GPS...")
                    await location.clear()
                elif cmd[0] == "SET":
                    await location.set(cmd[1], cmd[2])
                self.command_queue.task_done()
            except asyncio.TimeoutError:
                pass
                
        logging.info("Disconnecting, restoring real GPS before exit...")
        await location.clear()
        self.connected = False

device_manager = DeviceManager()
