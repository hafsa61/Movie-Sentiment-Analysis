# Movie Sentiment Analysis

A web application that analyzes movie reviews from IMDb to show sentiment analysis and keyword insights.

## Features

- **Movie Review Analysis**: Scrapes and analyzes IMDb movie reviews
- **Sentiment Analysis**: Shows positive, negative, and neutral sentiment distribution
- **Keyword Extraction**: Finds most common words with definitions using WordNet
- **Interactive Charts**: Beautiful visualizations of ratings and sentiment data
- **Real-time Results**: Fast analysis with comprehensive insights

## Tech Stack

**Backend:**
- Flask (Python web framework)
- NLTK (Natural language processing)
- Pandas (Data analysis)
- BeautifulSoup (Web scraping)

**Frontend:**
- React (User interface)
- Recharts (Data visualization)
- Axios (HTTP requests)

## Quick Start

### Option 1: Automated Setup
```bash
python setup.py
```

### Option 2: Manual Setup

**1. Install Python dependencies:**
```bash
pip install -r requirements.txt
```

**2. Install Node.js dependencies:**
```bash
cd frontend
npm install
```

**3. Run the application:**
```bash
# Terminal 1 - Start backend
cd backend
python app.py

# Terminal 2 - Start frontend
cd frontend
npm start
```

**4. Open your browser:**
- Frontend: http://localhost:3000
- Backend API: http://127.0.0.1:5000

## How to Use

1. **Enter a movie name** in the search box
2. **Click "Analyze"** to start the analysis
3. **View the results:**
   - Sentiment distribution (pie chart)
   - Rating distribution (bar chart)
   - Average rating by sentiment
   - Top keywords with definitions

## Project Structure

```
├── backend/
│   ├── app.py          # Flask API server
│   └── scraping.py     # IMDb scraping logic
├── frontend/
│   ├── src/
│   │   ├── App.js      # Main React component
│   │   └── App.css     # Styles
│   └── package.json    # Node.js dependencies
├── requirements.txt    # Python dependencies
├── setup.py           # Automated setup script
└── README.md          # This file
```

## API Endpoints

- `POST /analyze` - Analyze movie reviews
  ```json
  {
    "movie_name": "The Matrix"
  }
  ```

- `GET /test-wordnet` - Test WordNet functionality

## Example Output

The analysis provides:
- **Sentiment Counts**: Number of positive/negative/neutral reviews
- **Average Rating**: Overall IMDb rating
- **Rating Distribution**: How ratings are spread (1-10)
- **Top Keywords**: Most frequent words with WordNet definitions
- **Summary**: AI-generated summary of the analysis

## Troubleshooting

**Backend not starting?**
- Check if Python 3.8+ is installed
- Run `pip install -r requirements.txt`
- Test with: `python backend/app.py`

**Frontend not loading?**
- Check if Node.js 16+ is installed
- Run `cd frontend && npm install`
- Start with: `npm start`

**WordNet issues?**
- Visit http://127.0.0.1:5000/test-wordnet to test
- NLTK data downloads automatically on first run

## Notes

- Reviews are scraped from IMDb in real-time
- Data is processed in memory (not stored permanently)
- The `data/` folder is created automatically for temporary files
- NLTK downloads required data on first run

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Commit: `git commit -m "Add feature"`
5. Push: `git push origin feature-name`
6. Open a Pull Request

## License

This project is for educational purposes.

---

Made with love for learning sentiment analysis