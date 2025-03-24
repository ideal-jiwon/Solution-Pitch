// 📌 NLP 분석 결과 시각화
async function fetchAnalysis(businessId) {
    if (!businessId) {
        console.error("❌ Invalid business_id:", businessId);
        document.getElementById("analysis-result").textContent = "Invalid business ID.";
        return;
    }

    console.log("🔍 Fetching analysis for business_id:", businessId);

    try {
        const response = await fetch(`/models/realtime_sentiment?business_id=${businessId}`);
        const data = await response.json();

        if (data.error) {
            console.error("❌ Error fetching analysis:", data.error);
            document.getElementById("analysis-result").textContent = "Error fetching analysis.";
            return;
        }

        const reviews = data.analyzed_reviews;

        // 🔸 1. 감정 평균치 계산
        const sentimentTotals = { positive: 0, neutral: 0, negative: 0 };
        const sentimentCount = { positive: 0, neutral: 0, negative: 0 };
        const sentimentDistribution = { positive: 0, neutral: 0, negative: 0 };

        // 🔸 2. 카테고리별 키워드 그룹
        const categoryGroups = {};

        for (const r of reviews) {
            sentimentTotals.positive += r.confidence.positive;
            sentimentTotals.neutral += r.confidence.neutral;
            sentimentTotals.negative += r.confidence.negative;
            sentimentCount.positive++;
            sentimentCount.neutral++;
            sentimentCount.negative++;

            if (!categoryGroups[r.category]) {
                categoryGroups[r.category] = [];
            }
            categoryGroups[r.category].push(...r.keywords);

            // 감정 빈도 카운트
            sentimentDistribution[r.sentiment] = (sentimentDistribution[r.sentiment] || 0) + 1;
        }

        // 🔸 평균 감정 점수 시각화
        const avgSentimentScores = {
            positive: sentimentTotals.positive / sentimentCount.positive,
            neutral: sentimentTotals.neutral / sentimentCount.neutral,
            negative: sentimentTotals.negative / sentimentCount.negative
        };
        drawSentimentBar(avgSentimentScores);

        // 🔸 감정 빈도 시각화
        drawSentimentFrequency(sentimentDistribution);

        // 🔸 카테고리별 키워드 시각화
        drawGroupedKeywords(categoryGroups);

        // 🔸 분석 결과 샘플 보여주기
        document.getElementById("analysis-result").innerHTML = `<pre>${JSON.stringify(reviews.slice(0, 3), null, 2)}</pre>`;

    } catch (error) {
        console.error("❌ Fetch failed:", error);
        document.getElementById("analysis-result").textContent = "Failed to fetch analysis.";
    }
}

// 📌 사용자 입력에서 business_id로 분석 요청
function fetchFromInput() {
    const businessId = document.getElementById("business-id-input").value.trim();
    if (!businessId) {
        alert("Please enter a valid Business ID.");
        return;
    }
    fetchAnalysis(businessId);
}

// 📊 감정 평균 바 차트
function drawSentimentBar(averages) {
    const ctx = document.getElementById("ratings-chart").getContext("2d");
    if (window.sentimentBarChart) window.sentimentBarChart.destroy();

    window.sentimentBarChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Positive", "Neutral", "Negative"],
            datasets: [{
                label: "Average Confidence",
                data: [averages.positive, averages.neutral, averages.negative],
                backgroundColor: ["green", "gray", "red"]
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } }
        }
    });
}

// 📊 감정 빈도 바 차트
function drawSentimentFrequency(frequency) {
    const canvas = document.createElement("canvas");
    canvas.id = "sentiment-freq-chart";
    document.getElementById("weaknesses").innerHTML = "<h3>Sentiment Distribution</h3>";
    document.getElementById("weaknesses").appendChild(canvas);

    const ctx = canvas.getContext("2d");
    new Chart(ctx, {
        type: "bar",
        data: {
            labels: Object.keys(frequency),
            datasets: [{
                label: "Review Count",
                data: Object.values(frequency),
                backgroundColor: "#ffa600"
            }]
        },
        options: { responsive: true, plugins: { legend: { display: false } } }
    });
}

// 🟩 카테고리별 키워드 시각화
function drawGroupedKeywords(categoryGroups) {
    const container = document.getElementById("strengths");
    container.innerHTML = "<h3>Keywords by Category</h3>";

    Object.entries(categoryGroups).forEach(([category, keywords]) => {
        const counts = {};
        keywords.forEach(k => { counts[k] = (counts[k] || 0) + 1; });
        const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]);

        const section = document.createElement("div");
        section.innerHTML = `<h4>${category}</h4>`;

        sorted.slice(0, 5).forEach(([word, count]) => {
            const box = document.createElement("div");
            box.textContent = `${word} (${count})`;
            box.style.display = "inline-block";
            box.style.margin = "6px";
            box.style.padding = "8px";
            box.style.background = "#e0f7fa";
            box.style.borderRadius = "8px";
            section.appendChild(box);
        });

        container.appendChild(section);
    });
}

