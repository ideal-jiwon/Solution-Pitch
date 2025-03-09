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
async function searchLocation() {
    const query = document.getElementById("autocomplete").value;
    if (!query) {
        alert("Please enter a location.");
        return;
    }

    try {
        const response = await fetch("/api/places/search", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ query })
        });

        const data = await response.json();
        console.log("API Response:", data);

        if (data.places && data.places.length > 0) {
            const firstPlace = data.places[0];  // 첫 번째 검색 결과 사용
            console.log("First Place:", firstPlace);

            if (!firstPlace.id) {
                console.warn("❌ No place_id found in API response.");
                return;
            }
            const location = {
                lat: firstPlace.location.latitude,
                lng: firstPlace.location.longitude
            };

            // 지도 이동
            map.setCenter(location);
            map.setZoom(15);
        

            // 마커 업데이트
            marker.position = location;
            marker.title = firstPlace.displayName.text;

            document.getElementById("business-name").textContent = firstPlace.displayName.text;

            // 🔹 `place_id`가 존재하면 분석 요청 실행
            console.log("✅ Fetching analysis for place_id:", firstPlace.id);
            fetchAnalysis(firstPlace.id);
        } else {
            alert("No places found.");
        }
    } catch (error) {
        console.error("Error fetching places:", error);
    }
}


async function fetchAnalysis(placeId) {
    if (!placeId) {
        console.error("❌ Invalid place_id:", placeId);
        document.getElementById("analysis-result").textContent = "Invalid place ID.";
        return;
    }

    // 🔹 요청 URL을 확인하기 위한 로그 추가
    const requestUrl = `/models/analyze_reviews?place_id=${placeId}`;
    console.log(`✅ Sending request to: ${requestUrl}`);

    try {
        const response = await fetch(requestUrl);
        console.log("🔹 Fetch response status:", response.status);

        if (!response.ok) {
            console.error(`❌ Error fetching analysis. HTTP Status: ${response.status}`);
            console.error("🔹 Response text:", await response.text());  // 에러 원인 확인
            return;
        }

        const data = await response.json();
        console.log("🔹 Fetch response data:", data);

        updateAnalysisUI(data);

        if (data.error) {
            console.error("❌ Error fetching analysis:", data.error);
            return;
        }

    } catch (error) {
        console.error("❌ Network error:", error);
    }
}
        
// 📌 8️⃣ 리뷰 분석 결과 UI 업데이트
function updateAnalysisUI(data) {
    document.getElementById("analysis-result").textContent = data.relationship_analysis;

    document.getElementById("service-rating").textContent = data.avg_scores.service || "-";
    document.getElementById("price-rating").textContent = data.avg_scores.price || "-";
    document.getElementById("menu-rating").textContent = data.avg_scores.menu || "-";
    document.getElementById("location-rating").textContent = data.avg_scores.location || "-";
    document.getElementById("ambiance-rating").textContent = data.avg_scores.ambiance || "-";

    let strengthsHTML = "<h4>Strengths</h4>";
    for (const [key, value] of Object.entries(data.analysis?.strengths || {})) {
        strengthsHTML += `<p>${key}: ${value}%</p>`;
    }
    document.getElementById("strengths").innerHTML = strengthsHTML;

    let weaknessesHTML = "<h4>Weaknesses</h4>";
    for (const [key, value] of Object.entries(data.analysis?.weaknesses || {})) {
        weaknessesHTML += `<p>${key}: ${value}%</p>`;
    }
    document.getElementById("weaknesses").innerHTML = weaknessesHTML;

    document.getElementById("restaurant-rank").textContent = `Rank: ${data.ranking?.rank_category || "N/A"}`;
}

// 📌 9️⃣ Google Maps API 로드
loadGoogleMaps();

