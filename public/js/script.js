const BACKEND_URL = "solutionpitch-h4dzfecubpa4b6gc.eastus-01.azurewebsites.net";


fetch(`${BACKEND_URL}/models/realtime_sentiment?business_id=test`)
  .then((res) => res.json())
  .then((data) => {
    document.getElementById("result").textContent = JSON.stringify(data);
  })
  .catch((err) => {
    console.error("❌ Error fetching backend:", err);
  });
