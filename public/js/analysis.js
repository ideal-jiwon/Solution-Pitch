async function fetchAnalysis(placeId) {
    try {
        const response = await fetch(`/analyze_reviews?place_id=${placeId}`);
        const data = await response.json();

        if (data.error) {
            console.error("Error fetching analysis:", data.error);
            document.getElementById("analysis-result").textContent = "Error fetching analysis.";
            return;
        }

        // 분석 결과 UI 업데이트
        document.getElementById("analysis-result").textContent = data.relationship_analysis;

        // 카테고리 별점 업데이트
        document.getElementById("service-rating").textContent = data.avg_scores.service || "-";
        document.getElementById("price-rating").textContent = data.avg_scores.price || "-";
        document.getElementById("menu-rating").textContent = data.avg_scores.menu || "-";
        document.getElementById("location-rating").textContent = data.avg_scores.location || "-";
        document.getElementById("ambiance-rating").textContent = data.avg_scores.ambiance || "-";
    } catch (error) {
        console.error("Error:", error);
        document.getElementById("analysis-result").textContent = "Failed to fetch analysis.";
    }
}

// 📌 장소 검색 후 자동으로 분석 요청
async function searchLocation() {
    const place = autocomplete.getPlace();
    if (place && place.geometry) {
        map.setCenter(place.geometry.location);
        map.setZoom(15);
        marker.position = place.geometry.location;
        marker.title = place.formatted_address;
        
        document.getElementById("business-name").textContent = place.name;

        // 🔹 Azure LLM 분석 요청
        fetchAnalysis(place.place_id);
    } else {
        alert("Please select a valid location from the suggestions.");
    }
}
