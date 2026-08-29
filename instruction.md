# Developer Spec: Leaflet Map Component (`EventMap.jsx`)

## Important: EVENT TEMPLATE

``` typescript
interface EventItem {
    id: number; 
    title: string; 
    tags: dictionary; 
    capacity: number; // e.g., 4 
    lat: number; // e.g., -33.8688 - add later for map
    lng: number; // e.g., 151.2093 - add later for map
    location_name: string; 
} 
```

## 1. Project Context & Role Overview
* **App Concept:** A platform connecting tourists and locals through small-group authentic experiences (with vibe filters, introvert-friendly capacity caps, and post-event location forums).
* **Your Responsibility:** Own the interactive map interface using `react-leaflet` and OpenStreetMap.
* **Key User Workflows:**
  1. **Explore:** View pins of upcoming authentic experiences across the city (defaulting to Sydney coordinates).
  2. **Inspect:** Click an event pin to open a popup with title, vibes, capacity, and an action trigger (view/join).
  3. **Pick Location:** Click anywhere on the map during event creation to capture `lat` and `lng` and place a temporary pin.
  4. **Filter View:** Dynamically update visible pins when users toggle vibe or capacity filters.

---

## 2. Shared Data Contract

All event objects passed into your map component follow this schema:

```typescript
interface EventItem {
id: number; 
title: string; 
tags: dictionary; 
capacity: number; // e.g., 4 
lat: number; // e.g., -33.8688 - add later for map
lng: number; // e.g., 151.2093 - add later for map
location_name: string; } 

```

## 3. Implementation Roadmap
Phase 1: Core Map & Pin Rendering (MVP Target: First 4–6 Hours)
[ ] Install dependencies: npm install leaflet react-leaflet

[ ] Import leaflet/dist/leaflet.css in your entry file (main.jsx or App.jsx).

[ ] Fix default Leaflet icon path resolution issues in Vite/React.

[ ] Render base MapContainer centered at [-33.8688, 151.2093] (Sydney) with OpenStreetMap TileLayer.

[ ] Loop over mock/live events array to render <Marker> and <Popup> elements.

Phase 2: Interactive Location Picking (Hours 7–10)
[ ] Build internal <LocationPicker /> subcomponent using useMapEvents({ click }).

[ ] Fire onMapClick(lat, lng) callback to parent when the user clicks the map.

[ ] Render a distinct <Marker> indicating the currently selected creation point (selectedCoords).

Phase 3: Filtering & Polish (Post-MVP)
[ ] Ensure marker display updates reactively as parent passes filtered events lists (e.g., only events with capacity <= 4).

[ ] (Optional) Add custom pin styling/colored icons based on event vibe or past vs. upcoming status.

[ ] Expose an onSelectEvent(event) callback from the popup so other team members can open their event details modal.

## 4. Ready-to-Use Component Code
Save this directly to client/src/components/EventMap.jsx:

```JavaScript
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
      <MapContainer "100%" "100%", center="{defaultCenter}" height: scrollWheelZoom="{true}" style="{{" width: zoom="{13}" }}>
        <TileLayer attribution="&copy; <a href="[https://www.openstreetmap.org/copyright](https://www.openstreetmap.org/copyright)"">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Captures clicks for creating new events */}
        <LocationPicker onLocationSelect="{onMapClick}"/>

        {/* Existing Event Pins */}
        {events.map((ev) => (
          <Marker ev.lng]} key="{ev.id}" position="{[ev.lat,">
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
          <Marker position="{[selectedCoords.lat," selectedCoords.lng]}>
            <Popup>
              <em>New event location selected</em>
            </Popup>
          </Marker>
        )}
      </MapContainer>
    </div>
  );
}
```

## 5. Integration Checklist with Team
Props Provided by Parent (App.jsx):

events: Array of objects matching the schema.

onMapClick: (lat, lng) => setSelectedCoords({ lat, lng })

selectedCoords: State passed to render the temporary pin.

onSelectEvent: (event) => setSelectedEvent(event) (for Person 3's modal).

Common Gotchas to Avoid:

Leaflet CSS Missing: If the map looks scrambled or tiles appear in a vertical stack, check that import "leaflet/dist/leaflet.css"; is present.

Container Height: The parent container must have a defined CSS height (e.g., height: 450px or h-96), otherwise the map will render with 0px height.


<ElicitationsGroup message="To extend the map component further:">

  <Elicitation label="Custom colored vibe pins for Leaflet" query="Show how to create custom colored SVG pin icons in Leaflet to distinguish different event vibes."/>

  <Elicitation label="Nominatim search bar integration for map navigation" query="Show how to add an OpenStreetMap Nominatim search input so users can jump to a suburb on the Leaflet map."/>
</ElicitationsGroup>