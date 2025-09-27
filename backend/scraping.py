import requests
import time
import csv
import html
import json
import os
import random
from bs4 import BeautifulSoup


class Scraping:
    def __init__(self, teardown=False):
        self.teardown = teardown   
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "referer": "https://www.imdb.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "x-imdb-client-name": "imdb-web-next"
        }

    def __enter__(self):
        return self 

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            print("Cleaning up resources...")  

    def get_movie_id(self, movie_name):
        url = f"https://v3.sg.media-imdb.com/suggestion/x/{movie_name}.json"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            data = response.json()
            if "d" in data:
                first = data["d"][0]
                fetched_id = first["id"] 
                return fetched_id
        return None

    def fetch_reviews(self, movie_id):
        all_reviews = []
        seen_reviews = set()   # ✅ track duplicates
        cursor = None

        while True:
            variables = {
                "const": movie_id,
                "filter": {"spoiler": "EXCLUDE"},
                "first": 50,
                "locale": "en-GB",
                "sort": {"by": "HELPFULNESS_SCORE", "order": "DESC"}
            }

            if cursor:
                variables["after"] = cursor  

            payload = {
                "operationName": "TitleReviewsRefine",
                "variables": variables,
                "extensions": {
                    "persistedQuery": {
                        "sha256Hash": "d389bc70c27f09c00b663705f0112254e8a7c75cde1cfd30e63a2d98c1080c87",
                        "version": 1
                    }
                }
            }

            # Retry loop
            retries = 0
            while retries < 3:
                try:
                    response = requests.post(
                        "https://caching.graphql.imdb.com/",
                        headers=self.headers,
                        json=payload,
                        timeout=10
                    )
                    data = response.json()
                    if "data" in data and "title" in data["data"]:
                        break
                except Exception as e:
                    print(f"Error fetching page (attempt {retries+1}):", e)

                retries += 1
                time.sleep(2)
            else:
                print("Failed after retries, stopping.")
                break

            edges = data["data"]["title"]["reviews"].get("edges", [])
            if not edges:
                print("No more edges, stopping.")
                break

            new_count = 0
            for e in edges:
                node = e["node"]
                review_text = BeautifulSoup(node.get("text", {}).get("originalText", {}).get("plaidHtml", ""), "html.parser").get_text()

                # ✅ skip if already seen
                unique_key = (review_text, node.get("author", {}).get("username", {}).get("text",""))
                if unique_key in seen_reviews:
                    continue

                seen_reviews.add(unique_key)
                all_reviews.append({
                    "Author": node.get("author", {}).get("username", {}).get("text","undefined"),
                    "Rating": node.get("authorRating") or "NaN",
                    "Helpful_upVotes": node.get("helpfulness", 0).get("upVotes", 0),
                    "Helpful_downVotes": node.get("helpfulness", 0).get("downVotes", 0),
                    "Summary": node.get("summary", {}).get("originalText", ""),
                    "Review": review_text
                })
                new_count += 1

            print(f"Fetched {len(all_reviews)} reviews so far... (+{new_count})")

            # pagination
            page_info = data["data"]["title"]["reviews"]["pageInfo"]
            next_cursor = page_info.get("endCursor")

            if page_info.get("hasNextPage") and next_cursor and next_cursor != cursor:
                cursor = next_cursor
                time.sleep(random.uniform(0, 1.5))
            else:
                print("No further pages, stopping.")
                break

        return all_reviews


    def saving_to_csv(self, movie_id, all_reviews):
        print(f"Fetched {len(all_reviews)} reviews")

        os.makedirs("data", exist_ok=True)

        file_path = os.path.join("data", f"Reviews_{movie_id}.csv")

        with open(file_path, "w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["Author", "Rating", "Helpful_upVotes", "Helpful_downVotes", "Summary", "Review"]
            )
            writer.writeheader()
            writer.writerows(all_reviews)

        print(f"Saved Reviews for {movie_id} in {file_path}")
        return (f"Reviews_{movie_id}.csv")