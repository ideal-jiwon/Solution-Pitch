let map;
let marker;
let autocomplete;

async function initMap() {
    // 📌 1️⃣ 사용자의 현재 위치 가져오기
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(async (position) => {
            const userLocation = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };

            console.log("User's current location:", userLocation);

            //@ts-ignore
            const { Map } = await google.maps.importLibrary("maps");
            const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

            // 📌 2️⃣ 지도 초기화 (현재 위치로)
            map = new Map(document.getElementById("map"), {
                zoom: 14,
                center: userLocation,
                mapId: "DEMO_MAP_ID",
            });

            // 📌 3️⃣ 사용자 위치에 마커 추가
            marker = new AdvancedMarkerElement({
                map: map,
                position: userLocation,
                title: "Your Location",
            });

            // 📌 4️⃣ 자동완성(AutoComplete) 기능 추가
            autocomplete = new google.maps.places.Autocomplete(
                document.getElementById("autocomplete"),
                { types: ["geocode"] }
            );

            // 📌 5️⃣ 주소 선택 시 이벤트 추가
            autocomplete.addListener("place_changed", async () => {
                const place = autocomplete.getPlace();
                if (!place.geometry) return;

                // 지도 중심 이동
                map.setCenter(place.geometry.location);
                map.setZoom(15);

                // 마커 이동
                marker.position = place.geometry.location;
                document.getElementById("business-name").textContent = place.name;

                // NLP 처리된 리뷰 가져오기
                fetchReviews(place.place_id);
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

// 📌 6️⃣ 기본 위치(사용자가 위치 제공을 거부했을 때)
function loadDefaultLocation() {
    const defaultLocation = { lat: 37.7749, lng: -122.4194 }; // 샌프란시스코 (예제)

    //@ts-ignore
    const { Map } = google.maps.importLibrary("maps");
    const { AdvancedMarkerElement } = google.maps.importLibrary("marker");

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

    autocomplete = new google.maps.places.Autocomplete(
        document.getElementById("autocomplete"),
        { types: ["geocode"] }
    );

    autocomplete.addListener("place_changed", async () => {
        const place = autocomplete.getPlace();
        if (!place.geometry) return;

        map.setCenter(place.geometry.location);
        map.setZoom(15);
        marker.position = place.geometry.location;
        document.getElementById("business-name").textContent = place.name;

        fetchReviews(place.place_id);
    });
}

function searchLocation(){
    if (!autocomplete) {
        console.error("Autocomplete is not ready yet.");
        return;
    }

    const place = autocomplete.getPlace();
    if (place && place.geometry){
        map.setCenter(place.geometry.location);
        map.setZoom(15);
        marker.position = place.geometry.location;
        marker.title = place.formatted_address;
    } else {
        alert("Please select a valid location from the dropdown list.");
    }
    }


