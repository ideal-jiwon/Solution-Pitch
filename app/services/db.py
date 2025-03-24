import os
import json
import csv
from dotenv import load_dotenv
import psycopg2

# 🔹 환경 변수 로드
load_dotenv()

def connect_db():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    return conn

def create_csv_from_json(json_file, csv_file):
    filename = os.path.basename(json_file)

    if "business" in filename:
        business_map = {}
        with open(json_file, "r") as infile:
            for line in infile:
                try:
                    data = json.loads(line)
                    business_map[data["business_id"]] = data
                except json.JSONDecodeError as e:
                    print(f"❌ JSONDecodeError in {filename}: {e}")
                    continue

        with open(csv_file, "w", newline="") as outfile:
            writer = csv.writer(outfile)
            writer.writerow([
                "business_id", "name", "address", "city", "state", "postal_code",
                "latitude", "longitude", "categories", "hours", "review_count", "stars", "is_open"
            ])

            for data in business_map.values():
                categories = data.get("categories")
                if not categories or not isinstance(categories, str) or categories.strip() == "":
                    categories = "{}"
                else:
                    cleaned = [c.strip().replace('"', '') for c in categories.split(",") if c.strip()]
                    categories = "{" + ",".join(cleaned) + "}"

                hours = json.dumps(data.get("hours", {})) if data.get("hours") else "\\N"


                writer.writerow([
                    data["business_id"],
                    data["name"],
                    data.get("address", ""),
                    data.get("city", ""),
                    data.get("state", ""),
                    data.get("postal_code", ""),
                    data.get("latitude", 0),
                    data.get("longitude", 0),
                    categories,
                    hours,
                    data.get("review_count", 0),
                    data.get("stars", 0),
                    "true" if data.get("is_open", 0) == 1 else "false"
                ])

    elif "review" in filename:
        with open(json_file, "r") as infile, open(csv_file, "w", newline="") as outfile:
            writer = csv.writer(outfile)
            writer.writerow([
                "review_id", "business_id", "user_id", "stars", "date",
                "text", "useful", "funny", "cool"
            ])

            for line in infile:
                try:
                    data = json.loads(line)
                    writer.writerow([
                        data["review_id"],
                        data["business_id"],
                        data["user_id"],
                        data.get("stars", 0),
                        data.get("date", ""),
                        data.get("text", "").replace("\n", " "),
                        data.get("useful", 0),
                        data.get("funny", 0),
                        data.get("cool", 0),
                    ])
                except json.JSONDecodeError as e:
                    print(f"❌ JSONDecodeError in {filename}: {e}")
                    continue
        print(f"✅ {filename} → CSV 변환 완료!")
"""
    elif "user" in filename:
        with open(json_file, "r") as infile, open(csv_file, "w", newline="") as outfile:
            writer = csv.writer(outfile)
            writer.writerow([
                "user_id", "name", "review_count", "yelping_since",
                "average_stars", "friends", "fans"
            ])

            for line in infile:
                try:
                    data = json.loads(line)
                    friends = data.get("friends", "")

                    if isinstance(friends, list):
                        if len(friends) == 0:
                            friends = "{}"
                        else:
                            cleaned = [f.strip().replace('"', '') for f in friends if f.strip()]
                            friends = "{" + ",".join(cleaned) + "}"
                    elif isinstance(friends, str):
                        if friends.strip() == "":
                            friends = "{}"
                        else:
                            cleaned = [f.strip().replace('"', '') for f in friends.split(",") if f.strip()]
                            friends = "{" + ",".join(cleaned) + "}"
                    else:
                        friends = "{}"

                    writer.writerow([
                        data["user_id"],
                        data["name"],
                        data.get("review_count", 0),
                        data.get("yelping_since", ""),
                        data.get("average_stars", 0),
                        friends,
                        data.get("fans", 0)
                    ])"

                except json.JSONDecodeError as e:
                    print(f"❌ JSONDecodeError in {filename}: {e}")
                    continue
"""
    
def process_all_json_to_csv(data_dir, output_dir="/Users/stellam/Desktop/temp"):
    if not os.path.exists(data_dir):
        print(f"❌ 디렉토리 없음: {data_dir}")
        return

    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            json_path = os.path.join(data_dir, filename)
            csv_path = os.path.join(output_dir, filename.replace(".json", ".csv"))
            create_csv_from_json(json_path, csv_path)

# 🔹 실행 시작
if __name__ == "__main__":
    data_dir = "/Users/stellam/restaurant-ai-backend/restaurant-ai-frontend-typescript/app/database/data"
    process_all_json_to_csv(data_dir)

