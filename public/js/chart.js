<canvas id="ratings-chart"></canvas>

function drawChart(data) {
    const ctx = document.getElementById("ratings-chart").getContext("2d");

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Service", "Price", "Menu", "Location", "Ambiance"],
            datasets: [{
                label: "Average Ratings",
                data: [
                    data.avg_scores.service, 
                    data.avg_scores.price, 
                    data.avg_scores.menu, 
                    data.avg_scores.location, 
                    data.avg_scores.ambiance
                ],
                backgroundColor: ["red", "blue", "green", "orange", "purple"]
            }]
        },
        options: { responsive: true }
    });
}
