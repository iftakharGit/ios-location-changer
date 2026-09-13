import pytest
import asyncio
from unittest.mock import patch, MagicMock
from backend.device_manager import DeviceManager

@pytest.mark.asyncio
async def test_device_manager_initialization():
    dm = DeviceManager()
    assert dm.connected is False
    assert dm.intent_to_connect is False
    assert dm.command_queue is None
    assert dm.current_lat is None
    assert dm.current_lng is None

@pytest.mark.asyncio
async def test_device_manager_connect():
    dm = DeviceManager()
    
    # Mock the internal background task so we don't start the real infinite loop
    with patch.object(DeviceManager, 'spoofer_loop', new_callable=MagicMock) as mock_loop:
        async def dummy_coro():
            pass
        mock_loop.return_value = dummy_coro()
        
        dm.connect()
        assert dm.intent_to_connect is True
        assert dm.command_queue is not None
        assert dm._task is not None
        assert not dm._task.done()
        
        # Clean up
        dm.intent_to_connect = False
        await dm._task

@pytest.mark.asyncio
async def test_device_manager_disconnect_queues_clear():
    dm = DeviceManager()
    dm.command_queue = asyncio.Queue()
    dm.intent_to_connect = True
    
    dm.disconnect()
    
    assert dm.intent_to_connect is False
    cmd = dm.command_queue.get_nowait()
    assert cmd == ("CLEAR",)

@pytest.mark.asyncio
async def test_device_manager_set_location():
    dm = DeviceManager()
    dm.command_queue = asyncio.Queue()
    
    dm.set_location(35.6895, 139.6917)
    
    assert dm.current_lat == 35.6895
    assert dm.current_lng == 139.6917
    
    cmd = dm.command_queue.get_nowait()
    assert cmd == ("SET", 35.6895, 139.6917)

@pytest.mark.asyncio
async def test_device_manager_clear_location():
    dm = DeviceManager()
    dm.command_queue = asyncio.Queue()
    dm.current_lat = 10.0
    dm.current_lng = 20.0
    
    dm.clear_location()
    
    assert dm.current_lat is None
    assert dm.current_lng is None
    
    cmd = dm.command_queue.get_nowait()
    assert cmd == ("CLEAR",)
