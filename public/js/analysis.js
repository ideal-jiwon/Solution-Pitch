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
        console.log("📦 Fetched data:", data);

        if (data.error) {
            console.error("❌ Error fetching analysis:", data.error);
            document.getElementById("analysis-result").textContent = "Error fetching analysis.";
            return;
        }

        const reviews = data.analyzed_reviews;
        const sentimentTotals = { positive: 0, neutral: 0, negative: 0 };
        const sentimentCount = { positive: 0, neutral: 0, negative: 0 };
        const sentimentDistribution = { positive: 0, neutral: 0, negative: 0 };
        const categoryScores = {};
        const keywordMap = {};

        for (const r of reviews) {
            sentimentTotals.positive += r.confidence.positive;
            sentimentTotals.neutral += r.confidence.neutral;
            sentimentTotals.negative += r.confidence.negative;

            sentimentCount.positive++;
            sentimentCount.neutral++;
            sentimentCount.negative++;

            sentimentDistribution[r.sentiment] = (sentimentDistribution[r.sentiment] || 0) + 1;

            if (!categoryScores[r.category]) categoryScores[r.category] = [];
            categoryScores[r.category].push(r.confidence.positive);

            r.keywords.forEach(k => {
                keywordMap[k] = (keywordMap[k] || 0) + 1;
            });
        }

        const avgSentimentScores = {
            positive: sentimentTotals.positive / sentimentCount.positive,
            neutral: sentimentTotals.neutral / sentimentCount.neutral,
            negative: sentimentTotals.negative / sentimentCount.negative
        };

        drawSentimentBar(avgSentimentScores);
        drawSentimentFrequency(sentimentDistribution);
        drawGroupedKeywords(categoryScores, keywordMap);
        

        if (data.my_scores && data.nearby_scores) {
            drawComparisonChart(data.my_scores, data.nearby_scores);
            drawComparisonSummary(data.my_scores, data.nearby_scores);
        }
    } catch (error) {
        console.error("❌ Fetch failed:", error);
        document.getElementById("analysis-result").textContent = "Failed to fetch analysis.";
    }
    fetchComparisonData(businessId);
}
async function fetchComparisonData(businessId) {
    try {
        const res = await fetch(`/models/compare_reviews?business_id=${businessId}`);
        const data = await res.json();

        if (data.my_scores && data.nearby_scores) {
            drawComparisonChart(data.my_scores, data.nearby_scores);
            drawComparisonSummary(data.my_scores, data.nearby_scores);
        }
    } catch (err) {
        console.error("❌ Error fetching comparison data:", err);
    }
}

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
    const container = document.getElementById("sentiment-distribution");
    container.innerHTML = "<h3>Sentiment Distribution</h3>";
    container.appendChild(canvas);

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
        options: {
            responsive: true,
            plugins: { legend: { display: false } }
        }
    });
}

// 🔄 키워드 요약 및 시각화
function drawGroupedKeywords(categoryScores, keywordMap) {
    const container = document.getElementById("review-characteristics");
    container.innerHTML = "<h3>📊 Review Characteristics of My Business</h3>";

    const summary = document.createElement("p");
    const categories = Object.keys(categoryScores);
    const avgScores = categories.map(cat => {
        const scores = categoryScores[cat];
        return scores.reduce((a, b) => a + b, 0) / scores.length;
    });

    const maxIdx = avgScores.indexOf(Math.max(...avgScores));
    const minIdx = avgScores.indexOf(Math.min(...avgScores));

    summary.textContent = `📝 My business has the most reviews about ${categories[maxIdx]} (satisfaction: ${(avgScores[maxIdx] * 100).toFixed(1)}%), and the least about ${categories[minIdx]} (satisfaction: ${(avgScores[minIdx] * 100).toFixed(1)}%).`;
    container.appendChild(summary);

    const wrapper = document.createElement("div");
    wrapper.className = "review-visuals-container";

    const canvas = document.createElement("canvas");
    wrapper.appendChild(canvas);
    new Chart(canvas.getContext("2d"), {
        type: "bar",
        data: {
            labels: categories,
            datasets: [{
                label: "Avg. Positive Sentiment (%)",
                data: avgScores.map(s => (s * 100).toFixed(1)),
                backgroundColor: "rgba(100, 149, 237, 0.6)"
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    suggestedMax: Math.ceil(Math.max(...avgScores) * 100 * 1.3),
                    ticks: { callback: v => v + "%" }
                }
            },
            plugins: { legend: { display: false } }
        }
    });

    const treemap = document.createElement("div");
    treemap.className = "treemap-box";
    treemap.style.display = "grid";
    treemap.style.gridTemplateColumns = "repeat(4, 1fr)";
    treemap.style.gap = "12px";
    treemap.style.marginLeft = "20px";

    const sorted = Object.entries(keywordMap).sort((a, b) => b[1] - a[1]);
    const maxCount = sorted[0]?.[1] || 1;

    sorted.slice(0, 8).forEach(([word, count]) => {
        const box = document.createElement("div");
        box.textContent = word;
        box.style.display = "flex";
        box.style.alignItems = "center";
        box.style.justifyContent = "center";
        box.style.aspectRatio = "1/1";
        box.style.borderRadius = "12px";
        box.style.background = `rgba(144, 86, 255, ${0.3 + 0.7 * (count / maxCount)})`;
        box.style.color = "white";
        box.style.fontSize = "0.9rem";
        box.style.wordBreak = "break-word";
        treemap.appendChild(box);
    });

    wrapper.appendChild(treemap);
    container.appendChild(wrapper);
    
    window.analysisSummary = {
        categoryScores,
        keywordMap
    };
}

// 📊 내 사업체 vs 근처 비교
function drawComparisonChart(my, others) {
    const container = document.getElementById("restaurant-rank");
    container.innerHTML = "<h3>🆚 Compared with Nearby Businesses</h3>";

    const canvas = document.createElement("canvas");
    container.appendChild(canvas);

    const labels = Object.keys(my);
    const myData = labels.map(k => (my[k] * 100).toFixed(1));
    const otherData = labels.map(k => (others[k] * 100).toFixed(1));

    new Chart(canvas.getContext("2d"), {
        type: "bar",
        data: {
            labels,
            datasets: [
                {
                    label: "My Business",
                    data: myData,
                    backgroundColor: "rgba(46, 204, 113, 0.7)",
                },
                {
                    label: "Others (Nearby)",
                    data: otherData,
                    backgroundColor: "rgba(231, 76, 60, 0.6)",
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    suggestedMax: 100,
                    ticks: { callback: v => v + "%" }
                }
            }
        }
    });
}

function drawComparisonSummary(my, others) {
    const strengthList = [];
    const weaknessList = [];

    for (const cat in my) {
        const mine = my[cat] || 0;
        const other = others[cat] || 0;
        const diff = mine - other;

        if (diff >= 0.05) {
            strengthList.push({ cat, diff });
        } else if (diff <= -0.05) {
            weaknessList.push({ cat, diff });
        }
    }

    const strengthBox = document.getElementById("strengths");
    strengthBox.innerHTML = "<h3>💪 Strengths</h3>";
    strengthList.forEach(({ cat, diff }) => {
        const item = document.createElement("div");
        item.textContent = `${cat} (+${(diff * 100).toFixed(1)}%)`;
        item.style.marginBottom = "6px";
        item.style.background = "#d1e7dd";
        item.style.padding = "8px";
        item.style.borderRadius = "6px";
        strengthBox.appendChild(item);
    });

    const weaknessBox = document.getElementById("weaknesses");
    weaknessBox.innerHTML = "<h3>🧱 Needs Improvement</h3>";
    weaknessList.forEach(({ cat, diff }) => {
        const item = document.createElement("div");
        item.textContent = `${cat} (${(diff * 100).toFixed(1)}% lower)`;
        item.style.marginBottom = "6px";
        item.style.background = "#f8d7da";
        item.style.padding = "8px";
        item.style.borderRadius = "6px";
        weaknessBox.appendChild(item);
    });
}
async function submitImage() {
    const fileInput = document.getElementById("shop-image");
    const formData = new FormData();
    formData.append("image", fileInput.files[0]);

    const res = await fetch("/photo/upload_photo", {
        method: "POST",
        body: formData
    });

    const data = await res.json();
    const resultBox = document.getElementById("photo-analysis-result");
    resultBox.innerHTML = `<p>${data.solution}</p>`;

    data.matches.forEach(([url, score]) => {
        const img = document.createElement("img");
        img.src = url;
        img.style.width = "180px";
        img.style.margin = "10px";
        resultBox.appendChild(img);
    });
}


