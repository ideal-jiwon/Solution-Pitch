let map;
let marker;
let googleMapsLoaded = false; // Google Maps API가 중복 로드되지 않도록 플래그 설정


// 📌 1️⃣ Google Maps API 로드 (중복 방지)
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

// 📌 2️⃣ 지도 초기화 (중복 실행 방지)
async function initMap() {
    if (googleMapsLoaded) {
        console.warn("initMap() already executed.");
        return;
    }
    googleMapsLoaded = true; // 중복 실행 방지

    console.log("Google Maps API:", google.maps);

    if (!google.maps) {
        console.error("Google Maps API가 로드되지 않았습니다.");
        return;
    } else {
        console.log("Google Places API 로드 완료!");
    }

    // 📌 3️⃣ 사용자의 현재 위치 가져오기
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(async (position) => {
            const userLocation = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };

            console.log("User's current location:", userLocation);

            // Google Maps 및 Marker 라이브러리 가져오기
            const { Map } = await google.maps.importLibrary("maps");
            const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

            // 📌 4️⃣ 지도 초기화 (현재 위치로)
            map = new Map(document.getElementById("map"), {
                zoom: 14,
                center: userLocation,
                mapId: "DEMO_MAP_ID",
            });

            // 📌 5️⃣ 사용자 위치에 마커 추가
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

// 📌 6️⃣ 기본 위치(사용자가 위치 제공을 거부했을 때)
async function loadDefaultLocation() {
    const defaultLocation = { lat: 37.7749, lng: -122.4194 }; // 샌프란시스코 (예제)

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

// 📌 7️⃣ 장소 검색 (`searchText` API 사용)
async function searchBusiness() {
    const name = document.getElementById("b-name").value.trim();
    const address = document.getElementById("b-address").value.trim();
    const city = document.getElementById("b-city").value.trim();
    const state = document.getElementById("b-state").value.trim();
    const postal_code = document.getElementById("b-postal").value.trim();

    if (!name || !address || !city || !state || !postal_code) {
        alert("모든 항목을 입력해주세요.");
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
            alert("비즈니스 검색 실패: " + data.error);
            return;
        }

        // 지도에 표시
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

        // NLP 분석 호출
        fetchAnalysis(data.business_id);
    } catch (error) {
        console.error("❌ Search error:", error);
        alert("검색 중 오류 발생");
    }
}


// 📌 9️⃣ Google Maps API 로드
loadGoogleMaps();