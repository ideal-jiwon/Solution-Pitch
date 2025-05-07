let map;
let marker;
let googleMapsLoaded = false; 


// Google Maps API load
function loadGoogleMaps() {
    if (document.querySelector('script[src*="maps.googleapis.com"]')) {
        console.warn("Google Maps API is already loaded.");
        return;
    }

    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=YOUR_GOOGLE_MAPS_API_KEY&callback=initMap&libraries=places`;
    script.defer = true;
    script.async = true;
    document.head.appendChild(script);
}

// Map initilization
async function initMap() {
    if (googleMapsLoaded) {
        console.warn("initMap() already executed.");
        return;
    }
    googleMapsLoaded = true;

    console.log("Google Maps API:", google.maps);

    if (!google.maps) {
        console.error("Google Maps API가 로드되지 않았습니다.");
        return;
    } else {
        console.log("Google Places API 로드 완료!");
    }

    // Bring the location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(async (position) => {
            const userLocation = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };

            console.log("User's current location:", userLocation);

            // Google Maps & Marker Library
            const { Map } = await google.maps.importLibrary("maps");
            const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

            // Map initialization
            map = new Map(document.getElementById("map"), {
                zoom: 14,
                center: userLocation,
                mapId: "DEMO_MAP_ID",
            });

            // marker added to the user location
            marker = new AdvancedMarkerElement({
                map: map,
                position: userLocation,
                title: "Your Location",
            });

        }, () => {
            console.error("Geolocation permission denied. Using default location.");
            loadDefaultLocation();
        });
    } else {
        console.error("Geolocation is not supported by this browser.");
        loadDefaultLocation();
    }
}

// when user did not agree with sharing location
async function loadDefaultLocation() {
    const defaultLocation = { lat: 37.7749, lng: -122.4194 }; // san francisco

    const { Map } = await google.maps.importLibrary("maps");
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

    map = new Map(document.getElementById("map"), {
        zoom: 12,
        center: defaultLocation,
        mapId: "DEMO_MAP_ID",
    });

    marker = new AdvancedMarkerElement({
        map: map,
        position: defaultLocation,
        title: "Default Location",
    });
}

// `searchText` API
async function searchBusiness() {
    const name = document.getElementById("b-name").value.trim();
    const address = document.getElementById("b-address").value.trim();
    const city = document.getElementById("b-city").value.trim();
    const state = document.getElementById("b-state").value.trim();
    const postal_code = document.getElementById("b-postal").value.trim();

    if (!name || !address || !city || !state || !postal_code) {
        alert("Fill out all section");
        return;
    }

    try {
        const res = await fetch("/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, address, city, state, postal_code })
        });

        const data = await res.json();
        if (data.error) {
            alert("Failed searching for your business: " + data.error);
            return;
        }

        // mark on map
        const coords = {
            lat: data.coordinates.latitude,
            lng: data.coordinates.longitude
        };
        
        map.setCenter(coords);
        map.setZoom(15);
        
        marker?.setMap(null);
        marker = new google.maps.Marker({
            map,
            position: coords,
            title: data.name
        });
        
        document.getElementById("business-name").textContent = data.name;

        // call NLP analysis
        fetchAnalysis(data.business_id);
    } catch (error) {
        console.error("❌ Search error:", error);
        alert("❌ Search error", error);
    }
}


// load Google Maps API
loadGoogleMaps();