import { joystickStartAPI, joystickUpdateAPI, joystickStopAPI, fetchStatus } from './api.js';

export class JoystickManager {
    constructor(mapManager) {
        this.mapManager = mapManager;
        this.joyActive = false;
        this.joyLoop = null;
        this.keysPressed = { w: false, a: false, s: false, d: false };

        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
        document.addEventListener('keyup', (e) => this.handleKeyUp(e));
    }

    handleKeyDown(e) {
        const key = e.key.toLowerCase();
        if (this.keysPressed[key] !== undefined && document.activeElement.id !== 'searchInput') {
            this.keysPressed[key] = true;
            document.getElementById('btn-'+key.toUpperCase()).classList.add('active');
            this.updateJoyDirection();
        }
    }

    handleKeyUp(e) {
        const key = e.key.toLowerCase();
        if (this.keysPressed[key] !== undefined) {
            this.keysPressed[key] = false;
            document.getElementById('btn-'+key.toUpperCase()).classList.remove('active');
            this.updateJoyDirection();
        }
    }

    updateJoyDirection() {
        const moveY = (this.keysPressed['w'] ? 1 : 0) + (this.keysPressed['s'] ? -1 : 0);
        const moveX = (this.keysPressed['d'] ? 1 : 0) + (this.keysPressed['a'] ? -1 : 0);

        if (moveX === 0 && moveY === 0) {
            this.stopJoy();
        } else {
            let heading = Math.atan2(moveX, moveY) * (180 / Math.PI);
            if (heading < 0) heading += 360;
            
            if (!this.joyActive) {
                this.startJoy(heading);
            } else {
                joystickUpdateAPI(heading).catch(e => console.warn(e));
            }
        }
    }

    async startJoy(heading) {
        this.joyActive = true;
        await joystickStartAPI(heading).catch(e => console.warn(e));
        
        this.joyLoop = setInterval(async () => {
            try {
                const data = await fetchStatus();
                if (data.lat && data.lng) {
                    this.mapManager.updateSelection(data.lat, data.lng);
                    this.mapManager.map.panTo([data.lat, data.lng]);
                }
            } catch (e) {
                console.warn("Joystick poll error:", e);
            }
        }, 100);
    }

    async stopJoy() {
        if (!this.joyActive) return;
        this.joyActive = false;
        clearInterval(this.joyLoop);
        await joystickStopAPI().catch(e => console.warn(e));
    }
}
