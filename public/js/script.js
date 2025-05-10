const BACKEND_URL = "https://restaurant-ai-app.azurewebsites.net";


fetch(`${BACKEND_URL}/models/realtime_sentiment?business_id=test`)
  .then((res) => res.json())
  .then((data) => {
    document.getElementById("result").textContent = JSON.stringify(data);
  })
  .catch((err) => {
    console.error("❌ Error fetching backend:", err);
  });
