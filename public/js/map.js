let map;
let marker;
let googleMapsLoaded = false; 

// Google Maps API load
// function loadGoogleMaps() {
//     if (document.querySelector('script[src*="maps.googleapis.com"]')) {
//         console.warn("Google Maps API is already loaded.");
//         return;
//     }

//     const script = document.createElement("script");
//     script.src = `https://maps.googleapis.com/maps/api/js?key=YOUR_GOOGLE_MAPS_API_KEY&callback=initMap&libraries=places`;
//     script.defer = true;
//     script.async = true;
//     document.head.appendChild(script);
// }

// Map initilization
async function initMap() {
    if (googleMapsLoaded) {
        console.warn("initMap() already executed.");
        return;
    }
    googleMapsLoaded = true;

    console.log("Google Maps API:", google.maps);

    if (!google.maps) {
        console.error("Failed to load Google Maps API");
        return;
    } else {
        console.log("Google Places API load complete!");
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
    const fullAddress = document.getElementById("autocomplete-address").value.trim();

    if (!fullAddress) {
        alert("Please enter business address");
        return;
    }

    try {
        const res = await fetch("/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ full_address: fullAddress })
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

//autocomplete address 
document.getElementById("autocomplete-address").addEventListener("input", async function (e){
    const query = e.target.value.trim();

    if (query.length < 3 ){
        document.getElementById("address-suggestions").innerHTML = "";
        return;
    }
    try {
        const res = await fetch(`/api/address-suggestions?query=${encodeURIComponent(query)}`);
        const addresses = await res.json();

        const suggestionBox = document.getElementById("address-suggestions");
        suggestionBox.innerHTML = ""; // Clear first

        addresses.forEach(addr => {
            const div = document.createElement("div");
            div.className = "suggestion-item";
            div.textContent = addr;
            div.addEventListener("click", () => {
                selectSuggestion(addr);
            });
            suggestionBox.appendChild(div);
        });

    } catch (err) {
        console.error("❌ Failed to fetch suggestions:", err);
    }
});

function selectSuggestion(address) {
    document.getElementById("autocomplete-address").value = address;
    document.getElementById("address-suggestions").innerHTML = "";
}

// load Google Maps API
//loadGoogleMaps();
window.initMap = initMap;