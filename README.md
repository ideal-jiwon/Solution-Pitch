# Solution Pitch

**AI-powered customer insight tool** for small businesses.  
Turn messy reviews into actionable insights using NLP, visualizations, and a chatbot assistant.

---

## 🌐 Live Demo
[Watch Demo Video](https://your-youtube-demo-link.com)

---

##  Why Solution Pitch?

> Many small business owners rely on gut feeling or instinct, while big companies make data-driven decisions.  
> **Solution Pitch democratizes customer feedback analysis**, helping local businesses make smarter choices—without a data team.

---

##  Features

- **Sentiment Analysis** using Azure Text Analytics
- **Keyword Clustering** to identify core strengths
- **Comparison with Nearby Businesses**
- **Chatbot Summary + Apple Reminder integration**
- **Photo Uploader** with social media image recommendations
- **JSON/CSV → PostgreSQL Pipeline**

---
## Setup (Local Test)

```bash
git clone https://github.com/ideal-jiwon/restaurant-ai-frontend-koala94.git
git checkout demo-clean
cd /restaurant-ai-backend/restaurant-ai-frontend-typescript
pip install -r requirements.txt
python server.py

## Tech Stack

| Layer       | Tech                                |
|-------------|--------------------------------------|
| Frontend    | HTML, CSS, JavaScript, Chart.js      |
| Backend     | Python Flask                         |
| Database    | PostgreSQL (hosted on Azure)         |
| AI/NLP      | Azure Text Analytics, Azure OpenAI   |
| Media Search| Pexels API + PyTorch (image match)   |

---

## Data Structure

/restauarant-ai-frontend-typescript/
│
|── app/services           
│   ├── db.py
│   ├── nlp_service.py  
│   
│
|── app/database/data            
│   ├── business.json
│   ├── review.sjon
│           
│── __init__.py
│── auth.py
│── chat.py
│── image_analysis.py
│── models.py
│── photo.py
│── remind.py
│── routes.py
│── search.py
│
├── public/ (HTML/CSS/JS frontend)
│── header.html
│── index.html
│── login.html
│── report.html
│   
│
├── public/js
│   ├── map.js
│   ├── chatbot.js
│   ├── header.js
│   ├── analysis.js
│   └── auth.js
│
├── .env            
│── requirements.txt
│── server.py



