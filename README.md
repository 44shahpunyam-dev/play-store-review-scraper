# Google Play Store Reviews Scraper

A complete web application for scraping and analyzing Google Play Store reviews with filtering by date, rating, and custom hints.

## Features

- ✅ **No Authentication Required** - Use immediately without signup
- ✅ **Mobile-First Design** - Works perfectly on phones, tablets, and desktop
- ✅ **Real Backend Scraping** - Python-based scraper with pagination support
- ✅ **Advanced Filtering**
  - Date range selection
  - Rating filter (All, 5★, 4★, 3★, 2★, 1★)
  - Hint filter (text or emoji at end of review)
- ✅ **Excel Export** - Automatic .xlsx file generation with proper formatting
- ✅ **Live Preview** - See first 20 results before downloading
- ✅ **Responsive UI** - Beautiful, modern interface

## Project Structure

```
play-store-scraper/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── scraper.py              # Google Play scraper logic
│   ├── excel_generator.py       # Excel file generation
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── index.html              # Main HTML
│   ├── style.css               # Responsive styling
│   └── script.js               # Frontend logic
├── output/                      # Generated Excel files
├── README.md                    # This file
└── .gitignore                   # Git ignore rules
```

## Installation

### Prerequisites

- Python 3.8+
- Node.js (optional, for frontend development)
- macOS/Linux/Windows

### Step 1: Clone/Extract Project

```bash
cd play-store-scraper
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r backend/requirements.txt
```

## Running the Application

### Start Backend (Terminal 1)

```bash
source venv/bin/activate
cd backend
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Start Frontend (Terminal 2)

```bash
cd frontend
```

Option A: Using Python's built-in server
```bash
python -m http.server 8001
```

Then open: **http://localhost:8001**

Option B: Using Node.js http-server (if installed)
```bash
npx http-server -p 8001
```

Option C: Open directly in browser
```bash
open index.html
```
Or simply open `frontend/index.html` in your browser.

## Usage

1. **Enter Google Play Store URL**
   - Example: `https://play.google.com/store/apps/details?id=com.lendingplate`
   - The app automatically extracts the package ID

2. **Select Date Range**
   - From Date: Start date (YYYY-MM-DD)
   - To Date: End date (YYYY-MM-DD)

3. **Enter Hint (Optional)**
   - Text, emoji, or symbol that appears at the END of reviews
   - Case-insensitive for text
   - Examples: `"..."`, `"🙏"`, `"thank you"`
   - Leave empty to skip this filter

4. **Select Rating**
   - Choose All or specific rating (5★, 4★, 3★, 2★, 1★)

5. **Click "Start Scraping"**
   - Watch progress updates
   - See preview of matching reviews
   - Download Excel file with all results

## Example Test Case

```
URL: https://play.google.com/store/apps/details?id=com.lendingplate
From Date: 2026-07-28
To Date: 2026-07-28
Hint: loan
Rating: All
```

Expected Result:
- Reviews from July 28, 2026
- Containing "loan" at the end
- All ratings included
- Excel file: `Live_com.lendingplate_2026-07-28.xlsx`

## Excel Output

Generated files contain columns in this exact order:

| User | Review | Package ID | Rating | Date | Time |
|------|--------|-----------|--------|------|------|
| John Doe | Great app... | com.example | 5/5 | 2026-07-28 | 14:30:45 |

## Hint Filter Details

The hint filter matches text/emoji at the **END** of reviews only.

**Examples:**

Hint: `...`
- ✅ Matches: "Great app..."
- ❌ Doesn't match: "Great app... and useful"

Hint: `thank you` (case-insensitive)
- ✅ Matches: "Very useful THANK YOU"
- ✅ Matches: "Nice app thank you"

Hint: `🙏`
- ✅ Matches: "Excellent 🙏"
- ❌ Doesn't match: "🙏 Excellent"

## Troubleshooting

### Backend connection error
- Ensure backend is running on `http://localhost:8000`
- Check firewall settings
- Restart backend server

### No reviews found
- Verify the Play Store URL is correct
- Try a wider date range
- Remove or change the hint filter
- Try different rating selection

### Slow scraping
- This is normal - the app fetches all historical reviews with pagination
- Larger date ranges take longer
- Be patient during the "Fetching reviews..." stage

### Excel file not downloading
- Check browser download settings
- Try a different browser
- Ensure output/ directory has write permissions

## Technical Details

### Backend Stack
- **Framework**: FastAPI (Python web framework)
- **Scraper**: google-play-scraper (Python library)
- **Excel**: pandas + openpyxl
- **Server**: Uvicorn

### Frontend Stack
- **HTML5** for structure
- **CSS3** with mobile-first responsive design
- **Vanilla JavaScript** (no frameworks)

### Pagination
- Automatically fetches multiple pages of reviews
- Uses continuation tokens for efficient pagination
- Stops when date range is exceeded or no more reviews

### Date Filtering
- Strict date range filtering
- Properly handles timezone differences
- Output format: YYYY-MM-DD

## Limitations

1. **Rate Limiting**: Google Play Store may rate limit requests for large date ranges
2. **Historical Data**: Very old reviews may not be available
3. **Real-time**: Reviews are scraped at time of request
4. **Accuracy**: Review text is preserved exactly as provided by API

## Security

- URL validation prevents invalid Play Store URLs
- No user authentication needed
- No sensitive data stored
- Excel files generated locally

## License

This project is provided as-is for educational purposes.

## Support

For issues or improvements, check:
- Backend logs in terminal
- Browser console (F12)
- Ensure backend and frontend URLs match in script.js
