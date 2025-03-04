"use client";

import { useState } from "react";
import { saveReview, getStoredReviews } from "@/utils/api";

export default function Home() {
  const [placeId, setPlaceId] = useState("");
  const [reviewText, setReviewText] = useState("");
  const [sentiment, setSentiment] = useState("positive");
  const [reviews, setReviews] = useState<{ text: string; sentiment: string }[]>([]);
  const [selectedAddress, setSelectedAddress] = useState("");

  
  // ✅ 리뷰 저장 함수
  const handleSaveReview = async () => {
    if (!placeId || !reviewText) {
      alert("Place ID와 리뷰를 입력하세요.");
      return;
    }

    const result = await saveReview(placeId, reviewText, sentiment);
    if (result) {
      alert("리뷰가 성공적으로 저장되었습니다!");
      setReviewText(""); // 입력 필드 초기화
    }
  };

  // ✅ 저장된 리뷰 가져오는 함수
  const fetchStoredReviews = async () => {
    if (!placeId) {
      alert("Place ID를 입력하세요.");
      return;
    }

    const result = await getStoredReviews(placeId);
    if (result) {
      setReviews(result.reviews); // ✅ FastAPI 응답 구조에 맞게 변경
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-8">
      <h1 className="text-3xl font-bold mb-4">Google Maps 리뷰 저장 및 조회</h1>

      <input
        type="text"
        placeholder="Place ID 입력"
        value={placeId}
        onChange={(e) => setPlaceId(e.target.value)}
        className="border p-2 rounded mb-2"
      />

      <textarea
        placeholder="리뷰 입력"
        value={reviewText}
        onChange={(e) => setReviewText(e.target.value)}
        className="border p-2 rounded mb-2 w-2/3"
      />

      <select value={sentiment} onChange={(e) => setSentiment(e.target.value)} className="border p-2 rounded mb-2">
        <option value="positive">🙂 긍정</option>
        <option value="negative">☹️ 부정</option>
      </select>

      <button onClick={handleSaveReview} className="bg-blue-500 text-white px-4 py-2 rounded mr-2">
        리뷰 저장
      </button>

      <button onClick={fetchStoredReviews} className="bg-green-500 text-white px-4 py-2 rounded">
        저장된 리뷰 조회
      </button>

      {reviews.length > 0 && (
        <div className="mt-4 w-2/3 p-4 bg-white shadow-md rounded">
          <h2 className="text-xl font-bold mb-2">저장된 리뷰</h2>
          <ul>
            {reviews.map((review, idx) => (
              <li key={idx} className="p-2 border-b">
                {review.text} - <strong>{review.sentiment === "positive" ? "🙂 긍정" : "☹️ 부정"}</strong>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
