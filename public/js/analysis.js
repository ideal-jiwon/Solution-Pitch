// 📌 NLP 분석 결과 시각화
async function fetchAnalysis(businessId) {
    const loading = document.getElementById("loading-indicator");
    loading.style.display = "flex";

    if (!businessId) {
        console.error("❌ Invalid business_id:", businessId);
        document.getElementById("analysis-result").textContent = "Invalid business ID.";
        loading.style.display = "none";
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
            loading.style.display = "none";
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
    await fetchComparisonData(businessId);
    loading.style.display = "none";
    
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

function drawSentimentBar(averages) {
    const ctx = document.getElementById("ratings-chart").getContext("2d");
    if (window.sentimentBarChart) window.sentimentBarChart.destroy();

    const labels = ["Loyal Advocates", "Casual Visitors", "Unhappy Customers"];
    const values = [
        (averages.positive * 100).toFixed(1),
        (averages.neutral * 100).toFixed(1),
        (averages.negative * 100).toFixed(1)
    ];

    // 바 차트
    window.sentimentBarChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Customer Sentiment Intensity",
                data: values,
                backgroundColor: ["#2ecc71", "#f1c40f", "#e74c3c"]
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    beginAtZero: true,
                    suggestedMax: 100,
                    ticks: {
                        callback: v => v + "%"
                    }
                }
            }
        }
    });

    // summary
    const insightBox = document.getElementById("sentiment-insight");
    insightBox.innerHTML = `
        Your business has a strong base of <strong>Loyal Advocates</strong> (${values[0]}%), 
        but <strong>${values[2]}%</strong> of reviewers are <strong>Unhappy Customers</strong> — 
        consider addressing their pain points to improve customer retention.
    `;
}


function drawSentimentFrequency(frequency) {
    const container = document.getElementById("sentiment-distribution");
    container.innerHTML = "<h3>📊 What's people's impression?</h3>";

    const wrapper = document.createElement("div");
    wrapper.className = "sentiment-chart-wrapper";  // ✅ flex wrapper 추가

    const canvas = document.createElement("canvas");
    canvas.id = "sentiment-freq-chart";
    wrapper.appendChild(canvas);

    const ctx = canvas.getContext("2d");

    const labels = Object.keys(frequency);
    const data = Object.values(frequency);
    const total = data.reduce((a, b) => a + b, 0);
    const percentages = data.map((val) => ((val / total) * 100).toFixed(1));

    new Chart(ctx, {
        type: "pie",
        data: {
            labels: labels.map((label, i) => `${label} (${percentages[i]}%)`),
            datasets: [{
                label: "Sentiment Distribution",
                data: data,
                backgroundColor: ["#2ecc71", "#f1c40f", "#e74c3c", "#95a5a6"]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: 10
            },
            plugins: {
                legend: {
                    position: "right"
                }
            }
        }
    });

    const summary = document.createElement("div");
    summary.className = "summary-text";  
    summary.innerHTML = labels.map((label, i) => {
        return `<p><strong>${label}</strong>: ${percentages[i]}%</p>`;
    }).join("");

    wrapper.appendChild(summary);
    container.appendChild(wrapper);
}



function drawGroupedKeywords(categoryScores, keywordMap) {
    const container = document.getElementById("review-characteristics");
    container.innerHTML = "<h3> Review Characteristics of My Business</h3>";

    const summary = document.createElement("p");
    const categories = Object.keys(categoryScores);
    const avgScores = categories.map(cat => {
        const scores = categoryScores[cat];
        return scores.reduce((a, b) => a + b, 0) / scores.length;
    });

    const maxIdx = avgScores.indexOf(Math.max(...avgScores));
    const minIdx = avgScores.indexOf(Math.min(...avgScores));

    summary.textContent = ` My business has the most reviews about ${categories[maxIdx]} (satisfaction: ${(avgScores[maxIdx] * 100).toFixed(1)}%),and the least about ${categories[minIdx]} (satisfaction: ${(avgScores[minIdx] * 100).toFixed(1)}%).`;
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
    
        const scale = 80 + 80 * (count / maxCount); // 최소 80px ~ 최대 160px
    
        box.style.width = `${scale}px`;
        box.style.height = `${scale}px`;
    
        box.style.background = `rgba(144, 86, 255, ${0.3 + 0.7 * (count / maxCount)})`;
    
        treemap.appendChild(box);
    });

    wrapper.appendChild(treemap);
    container.appendChild(wrapper);

    window.analysisSummary = {
        categoryScores,
        keywordMap
    };
}

function drawComparisonChart(my, others) {
    const container = document.getElementById("restaurant-rank");
    container.innerHTML = "<h3>Compared with Nearby Businesses</h3>";

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
