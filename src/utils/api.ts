import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000"; // FastAPI 서버 주소

// ✅ 리뷰 타입 정의
interface Review {
  text: string;
  sentiment: string;
}

interface GetStoredReviewsResponse {
  place_id: string;
  reviews: Review[]; // ✅ FastAPI 응답 구조에 맞게 변경
}

// ✅ 리뷰 저장 API 호출 함수
export const saveReview = async (placeId: string, reviewText: string, sentiment: string) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/save_review/`, {
      place_id: placeId,
      review_text: reviewText,
      sentiment: sentiment,
    });

    return response.data;
  } catch (error) {
    console.error("Error saving review:", error);
    return null;
  }
};

// ✅ 저장된 리뷰 가져오기 API 호출 함수
export const getStoredReviews = async (placeId: string): Promise<GetStoredReviewsResponse | null> => {
  try {
    const response = await axios.get<GetStoredReviewsResponse>(`${API_BASE_URL}/get_stored_reviews/${placeId}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching stored reviews:", error);
    return null;
  }
};
