// api.js
export async function toggleConnection(isIntent) {
    if (isIntent) {
        await fetch('/api/disconnect', {method: 'POST'});
        return false;
    } else {
        await fetch('/api/connect', {method: 'POST'});
        return true;
    }
}

export async function fetchStatus() {
    const res = await fetch('/api/status');
    return await res.json();
}

export async function searchLocationAPI(query) {
    const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}`);
    return await res.json();
}

export async function teleportAPI(lat, lng) {
    await fetch('/api/set_location', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lat, lng })
    });
}

export async function stopTeleportAPI() {
    await fetch('/api/stop', { method: 'POST' });
}

export async function setSpeedAPI(speed) {
    await fetch('/api/speed', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ speed })
    });
}

export async function joystickStartAPI(heading) {
    await fetch('/api/joystick', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: "start", heading })
    });
}

export async function joystickUpdateAPI(heading) {
    const res = await fetch('/api/joystick', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: "update", heading })
    });
    return await res.json();
}

export async function joystickStopAPI() {
    await fetch('/api/joystick', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: "stop" })
    });
}
