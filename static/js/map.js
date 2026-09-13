import { teleportAPI } from './api.js';

export class MapManager {
    constructor() {
        this.map = L.map('map').setView([51.505, -0.09], 13);
        
        const standard = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 });
        const satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { maxZoom: 19, attribution: 'Esri' });
        const terrain = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', { maxZoom: 19, attribution: 'Esri' });
        
        const baseMaps = {
            "Standard": standard,
            "Satellite": satellite,
            "Terrain": terrain
        };
        
        standard.addTo(this.map);
        L.control.layers(baseMaps).addTo(this.map);
        
        this.currentMarker = L.marker([51.505, -0.09]).addTo(this.map);
        this.selectedLat = null;
        this.selectedLng = null;

        this.waypoints = [];
        this.waypointMarkers = [];
        this.polyline = L.polyline([], {color: 'blue'}).addTo(this.map);
        this.routeInterval = null;

        this.map.on('click', (e) => this.updateSelection(e.latlng.lat, e.latlng.lng));
        
        this.map.on('contextmenu', (e) => this.addWaypoint(e.latlng.lat, e.latlng.lng));
        this.setupDragAndDrop();
    }

    setupDragAndDrop() {
        const mapContainer = document.getElementById('map');
        
        mapContainer.addEventListener('dragover', (e) => {
            e.preventDefault();
            mapContainer.style.opacity = '0.7';
        });

        mapContainer.addEventListener('dragleave', (e) => {
            e.preventDefault();
            mapContainer.style.opacity = '1';
        });

        mapContainer.addEventListener('drop', (e) => {
            e.preventDefault();
            mapContainer.style.opacity = '1';
            
            if (e.dataTransfer.files.length > 0) {
                const file = e.dataTransfer.files[0];
                file.text().then(content => {
                    this.parseAndLoadGPX(content);
                }).catch(err => console.error(err));
            }
        });
    }

    parseAndLoadGPX(xmlString) {
        try {
            const parser = new DOMParser();
            const xmlDoc = parser.parseFromString(xmlString, "text/xml");
            const trackPoints = xmlDoc.getElementsByTagName('trkpt');
            
            if (trackPoints.length === 0) {
                return (window.showToast || console.log)("No track points found in GPX file.");
            }
            
            this.clearRoute(); // Reset existing
            
            for (const point of trackPoints) {
                const lat = Number.parseFloat(point.getAttribute('lat'));
                const lon = Number.parseFloat(point.getAttribute('lon'));
                this.addWaypoint(lat, lon);
            }
            
            this.map.fitBounds(this.polyline.getBounds());
            (window.showToast || console.log)(`Loaded ${trackPoints.length} waypoints from GPX!`);
            
        } catch (error) {
            console.error("Error parsing GPX:", error);
            (window.showToast || console.log)("Invalid GPX file format.");
        }
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
