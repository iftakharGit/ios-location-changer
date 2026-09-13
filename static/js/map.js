import { teleportAPI } from './api.js';

export class MapManager {
    constructor() {
        this.map = L.map('map').setView([51.505, -0.09], 13);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(this.map);
        
        this.currentMarker = L.marker([51.505, -0.09]).addTo(this.map);
        this.selectedLat = null;
        this.selectedLng = null;

        this.waypoints = [];
        this.waypointMarkers = [];
        this.polyline = L.polyline([], {color: 'blue'}).addTo(this.map);
        this.routeInterval = null;

        this.map.on('click', (e) => this.updateSelection(e.latlng.lat, e.latlng.lng));
        this.map.on('contextmenu', (e) => this.addWaypoint(e.latlng.lat, e.latlng.lng));
    }

    updateSelection(lat, lng) {
        this.selectedLat = lat;
        this.selectedLng = lng;
        this.currentMarker.setLatLng([lat, lng]);
    }

    addWaypoint(lat, lng) {
        this.waypoints.push([lat, lng]);
        this.polyline.setLatLngs(this.waypoints);
        const m = L.circleMarker([lat, lng], {radius: 5, color: 'red'}).addTo(this.map);
        this.waypointMarkers.push(m);
    }

    clearRoute() {
        this.waypoints = [];
        this.waypointMarkers.forEach(m => this.map.removeLayer(m));
        this.waypointMarkers = [];
        this.polyline.setLatLngs([]);
        clearInterval(this.routeInterval);
    }

    async startRoute(speedMetersPerSecond) {
        if (this.waypoints.length < 2) return (window.showToast || console.log)("Add at least 2 waypoints by right-clicking on the map!");
        let currentWpIndex = 0;
        
        this.updateSelection(this.waypoints[0][0], this.waypoints[0][1]);
        await teleportAPI(this.selectedLat, this.selectedLng);

        let lastFrameTime = Date.now();

        this.routeInterval = setInterval(async () => {
            const target = this.waypoints[currentWpIndex + 1];
            if (!target) {
                clearInterval(this.routeInterval);
                return (window.showToast || console.log)("Route finished!");
            }
            
            // Delta time calculation to completely eliminate Time Drift
            const now = Date.now();
            const deltaTimeSeconds = (now - lastFrameTime) / 1000.0;
            lastFrameTime = now;
            
            const distanceToMove = speedMetersPerSecond * deltaTimeSeconds;
            
            const startObj = L.latLng(this.selectedLat, this.selectedLng);
            const targetObj = L.latLng(target[0], target[1]);
            const distanceToTarget = startObj.distanceTo(targetObj); 
            
            if (distanceToTarget <= distanceToMove) {
                this.updateSelection(target[0], target[1]);
                currentWpIndex++;
            } else {
                const ratio = distanceToMove / distanceToTarget;
                const latDiff = target[0] - this.selectedLat;
                const lngDiff = target[1] - this.selectedLng;
                this.updateSelection(this.selectedLat + (latDiff * ratio), this.selectedLng + (lngDiff * ratio));
            }
            
            await teleportAPI(this.selectedLat, this.selectedLng);
            this.map.panTo([this.selectedLat, this.selectedLng]);
            
        }, 100); // 10 updates a second for butter smooth movement without drift
    }
}
