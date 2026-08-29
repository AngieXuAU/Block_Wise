import React, { useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// --- Fix Leaflet Marker Icon Asset Resolution for Vite ---
import icon from "leaflet/dist/images/marker-icon.png";
import iconShadow from "leaflet/dist/images/marker-shadow.png";

const DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;

// --- Sub-component: Click Listener for Dropping a Pin ---
function LocationPicker({ onLocationSelect }) {
    useMapEvents({
        click(e) {
            if (onLocationSelect) {
                onLocationSelect(e.latlng.lat, e.latlng.lng);
            }
        },
    });
    return null;
}

/**
 * EventMap Component
 * @param {Array} events - List of event objects to render as pins
 * @param {Function} onMapClick - Callback when user clicks the map: (lat, lng) => void
 * @param {Object} selectedCoords - Temporary coords for new event: { lat, lng } | null
 * @param {Function} onSelectEvent - Callback when user clicks "View Details" in a popup
 */
export default function EventMap({
    events = [],
    onMapClick,
    selectedCoords = null,
    onSelectEvent,
}) {
    const defaultCenter = [-33.8688, 151.2093]; // Sydney Center

    return (
        <div style={{ height: "450px", width: "100%", borderRadius: "8px", overflow: "hidden" }}>
            <MapContainer
                center={defaultCenter}
                zoom={13}
                scrollWheelZoom={true}
                style={{ height: "100%", width: "100%" }}
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {/* Captures clicks for creating new events */}
                <LocationPicker onLocationSelect={onMapClick} />

                {/* Existing Event Pins */}
                {events.map((ev) => (
                    <Marker key={ev.id} position={[ev.lat, ev.lng]}>
                        <Popup>
                            <div style={{ padding: "4px" }}>
                                <h3 style={{ margin: "0 0 4px 0", fontSize: "14px", fontWeight: "bold" }}>{ev.title}</h3>
                                <p style={{ margin: "0 0 4px 0", fontSize: "12px", color: "#555" }}>
                                    <strong>Vibes:</strong> {ev.vibes}
                                </p>
                                <p style={{ margin: "0 0 8px 0", fontSize: "12px", color: "#555" }}>
                                    <strong>Spots:</strong> Up to {ev.capacity} people
                                </p>
                                {onSelectEvent && (
                                    <button
                                        onClick={() => onSelectEvent(ev)}
                                        style={{
                                            background: "#2563eb",
                                            color: "#fff",
                                            border: "none",
                                            padding: "4px 8px",
                                            borderRadius: "4px",
                                            cursor: "pointer",
                                            fontSize: "12px",
                                        }}
                                    >
                                        View Details
                                    </button>
                                )}
                            </div>
                        </Popup>
                    </Marker>
                ))}

                {/* Temporary Marker for Selected Creation Point */}
                {selectedCoords && (
                    <Marker position={[selectedCoords.lat, selectedCoords.lng]}>
                        <Popup>
                            <em>New event location selected</em>
                        </Popup>
                    </Marker>
                )}
            </MapContainer>
        </div>
    );
}