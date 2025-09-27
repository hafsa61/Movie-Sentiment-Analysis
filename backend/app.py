from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import os
import shutil
import nltk
import re
import base64
import io
from scraping import Scraping
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud
from typing import List

app = Flask(__name__)
CORS(app)

# --- SETUP ---
def download_nltk_data():
    """Download required NLTK data with error handling"""
    required_data = ["stopwords", "wordnet", "vader_lexicon", "punkt", "averaged_perceptron_tagger"]
    
    for data in required_data:
        try:
            nltk.download(data, quiet=True)
            print(f"✅ Downloaded NLTK data: {data}")
        except Exception as e:
            print(f"⚠️ Failed to download NLTK data '{data}': {e}")
            # Continue with other downloads

download_nltk_data()

data_folder = "data"

@app.route('/test-wordnet', methods=['GET'])
def test_wordnet():
    """Test endpoint to check if wordnet functionality is working"""
    try:
        # Test basic NLTK functionality
        test_text = "This is a great movie with amazing acting and wonderful story"
        
        # Test tokenization
        tokens = word_tokenize(test_text.lower())
        
        # Test stopwords
        stop_words = set(stopwords.words("english"))
        meaningful_words = [token for token in tokens if len(token) > 2 and token.isalpha() and token not in stop_words]
        
        # Test WordNet
        wordnet_results = []
        for word in meaningful_words[:5]:
            try:
                synsets = wordnet.synsets(word)
                if synsets:
                    synset = synsets[0]
                    wordnet_results.append({
                        "word": word,
                        "definition": synset.definition(),
                        "pos": synset.pos()
                    })
            except Exception as e:
                wordnet_results.append({
                    "word": word,
                    "error": str(e)
                })
        
        return jsonify({
            "status": "success",
            "test_text": test_text,
            "tokens": tokens,
            "meaningful_words": meaningful_words,
            "wordnet_results": wordnet_results,
            "nltk_data_available": {
                "stopwords": len(stop_words) > 0,
                "wordnet": len(wordnet.synsets("test")) > 0
            }
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "traceback": str(e.__traceback__)
        }), 500

@app.route('/analyze', methods=['POST'])
def analyze_movie():
    movie_name = request.json.get('movie_name')
    if not movie_name:
        return jsonify({'error': 'Movie name is required'}), 400

    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    else:
        for filename in os.listdir(data_folder):
            file_path = os.path.join(data_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

    with Scraping() as scraper:
        movie_id = scraper.get_movie_id(movie_name)
        if not movie_id:
            return jsonify({'error': 'Movie not found'}), 404
        all_reviews = scraper.fetch_reviews(movie_id)
        csv_name = scraper.saving_to_csv(movie_id, all_reviews)

    df = pd.read_csv(f"data/{csv_name}")

    def clean_text(text):
        text = text.lower()
        text = re.sub(r"[^a-z\s]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    df.drop_duplicates(subset="Review", inplace=True)
    df.dropna(subset=["Review", "Summary"], inplace=True)
    df["Rating"] = df["Rating"].fillna(round(df["Rating"].mean()))

    stop_words = set(stopwords.words("english"))
    lemmatizer = WordNetLemmatizer()

    df["Review"] = df["Review"].astype(str).apply(clean_text)
    df["Summary"] = df["Summary"].astype(str).apply(clean_text)

    df["Review"] = df["Review"].apply(
        lambda x: " ".join([lemmatizer.lemmatize(w) for w in x.split() if w not in stop_words])
    )
    df["Summary"] = df["Summary"].apply(
        lambda x: " ".join([lemmatizer.lemmatize(w) for w in x.split() if w not in stop_words])
    )

    sia = SentimentIntensityAnalyzer()
    df["Sentiment"] = df["Review"].apply(lambda x: sia.polarity_scores(str(x)))
    df["Compound"] = df["Sentiment"].apply(lambda x: x["compound"])
    df["Sentiment_label"] = df["Compound"].apply(
        lambda s: "positive" if s > 0.05 else ("negative" if s < -0.05 else "neutral")
    )
    df["Negative"] = df["Sentiment"].apply(lambda x: x["neg"])
    df["Neutral"] = df["Sentiment"].apply(lambda x: x["neu"])
    df["Positive"] = df["Sentiment"].apply(lambda x: x["pos"])
    df = df.drop(columns=["Sentiment"])

    cleaned_file = os.path.join("data", f"Reviews_{movie_id}.csv")
    df.to_csv(cleaned_file, index=False)

    sentiment_counts = df["Sentiment_label"].value_counts().to_dict()
    avg_rating = round(df["Rating"].mean(), 1)
    rating_distribution = df['Rating'].value_counts().sort_index().to_dict()
    avg_rating_by_sentiment = df.groupby('Sentiment_label')['Rating'].mean().to_dict()

    # --- WORD CLOUD GENERATION ---
    def generate_word_cloud(texts, movie_id):
        """Generate a colorful word cloud from review texts"""
        try:
            # Combine all text
            all_text = " ".join([str(text) for text in texts if pd.notna(text) and str(text).strip()])
            print(f"🔍 Generating word cloud from {len(all_text)} characters")
            
            if not all_text.strip():
                print("⚠️ No text to generate word cloud")
                return None
            
            # Create word cloud
            wordcloud = WordCloud(
                width=800,
                height=400,
                background_color='white',
                max_words=100,
                colormap='viridis',  # Colorful colormap
                relative_scaling=0.5,
                random_state=42
            ).generate(all_text)
            
            # Save word cloud to memory
            img_buffer = io.BytesIO()
            wordcloud.to_image().save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            # Convert to base64 for frontend
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            
            print(f"✅ Word cloud generated successfully")
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            print(f"❌ Word cloud generation error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_top_keywords(texts):
        """Get top keywords for display (simplified version)"""
        try:
            # Combine all text
            all_text = " ".join([str(text) for text in texts if pd.notna(text) and str(text).strip()])
            
            if not all_text.strip():
                return []
            
            # Tokenize and filter
            try:
                tokens = word_tokenize(all_text.lower())
            except Exception:
                tokens = all_text.lower().split()
            
            meaningful_words = []
            for token in tokens:
                if (len(token) > 2 and 
                    token.isalpha() and 
                    token not in stop_words and
                    len(token) < 20):
                    meaningful_words.append(token)
            
            if not meaningful_words:
                return []
            
            # Count frequency
            from collections import Counter
            word_counts = Counter(meaningful_words)
            top_words = word_counts.most_common(15)
            
            return [{"name": word, "value": count} for word, count in top_words]
            
        except Exception as e:
            print(f"❌ Top keywords extraction error: {e}")
            return []
    
    # Generate word cloud and get top keywords
    all_reviews_text = df["Review"].fillna("").tolist()
    word_cloud_image = generate_word_cloud(all_reviews_text, movie_id)
    top_keywords = get_top_keywords(all_reviews_text)

    def _fallback_summary() -> str:
        pos_reviews = sentiment_counts.get('positive', 0)
        neg_reviews = sentiment_counts.get('negative', 0)
        if pos_reviews > neg_reviews:
            verdict = "Overall, audiences enjoyed the movie."
        elif neg_reviews > pos_reviews:
            verdict = "Overall, audiences were disappointed."
        else:
            verdict = "The audience reaction was mixed."
        return f"⭐ Avg {avg_rating}/10. {verdict}"

    def _build_ai_summary(reviews: List[str]) -> str:
        # Fast heuristic summary: combine rating, verdict, and a top keyword
        pos_reviews = sentiment_counts.get('positive', 0)
        neg_reviews = sentiment_counts.get('negative', 0)
        if pos_reviews > neg_reviews:
            verdict = "Overall positive audience reception."
        elif neg_reviews > pos_reviews:
            verdict = "Overall negative audience reception."
        else:
            verdict = "Mixed audience reception."
        top_kw = top_keywords[0]["name"] if top_keywords else None
        if top_kw:
            return f"⭐ Avg {avg_rating}/10. {verdict} Common theme: {top_kw}."
        return f"⭐ Avg {avg_rating}/10. {verdict}"

    # Prepare sample reviews for AI
    sample_reviews = (
        df.sort_values(by=["Helpful_upVotes"], ascending=False)
          .dropna(subset=["Review"])
          .head(50)["Review"].tolist()
    )
    ai_summary = _build_ai_summary(sample_reviews)

    return jsonify({
        'sentiment_counts': sentiment_counts,
        'avg_rating': avg_rating,
        'rating_distribution': rating_distribution,
        'avg_rating_by_sentiment': avg_rating_by_sentiment,
        'total_reviews': int(len(df)),
        'top_keywords': top_keywords,
        'word_cloud_image': word_cloud_image,
        'summary': ai_summary,
        'reviews': df.to_dict('records')
    })

if __name__ == '__main__':
    app.run(debug=True)