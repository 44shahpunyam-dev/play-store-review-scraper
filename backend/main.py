from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
import re
import os
from pathlib import Path
import sys

from backend.scraper import ReviewScraper
from backend.excel_generator import ExcelGenerator

app = FastAPI()

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


class ScrapeRequest(BaseModel):
    url: str
    from_date: str  # Format: YYYY-MM-DD
    to_date: str    # Format: YYYY-MM-DD
    hint: str = ""  # Optional hint at end of review
    rating: int = 0  # 0 = All, 1-5 for specific rating


def validate_play_store_url(url: str) -> str:
    """Extract package ID from Play Store URL and validate."""
    # Expected format: https://play.google.com/store/apps/details?id=com.example.app
    pattern = r'play\.google\.com/store/apps/details\?id=([a-zA-Z0-9._]+)'
    match = re.search(pattern, url)
    
    if not match:
        raise ValueError("Invalid Google Play Store URL format")
    
    package_id = match.group(1)
    if not package_id or len(package_id) < 3:
        raise ValueError("Invalid package ID extracted")
    
    return package_id


def validate_dates(from_date: str, to_date: str):
    """Validate date format and logic."""
    try:
        from_dt = datetime.strptime(from_date, "%Y-%m-%d")
        to_dt = datetime.strptime(to_date, "%Y-%m-%d")
        
        if from_dt > to_dt:
            raise ValueError("From date cannot be later than To date")
        
        return True
    except ValueError as e:
        raise ValueError(f"Invalid date format or range: {str(e)}")


def get_app_name(package_id: str) -> str:
    """Fetch Play Store app title or fallback to package ID."""
    try:
        from google_play_scraper import app as play_app
        details = play_app(package_id, lang='en', country='in')
        title = details.get('title', '')
        if title:
            return title
    except Exception:
        pass
    return package_id


@app.post("/api/scrape")
async def scrape_reviews(request: ScrapeRequest):
    """Main scraping endpoint"""
    try:
        # Validate URL and extract package ID
        package_id = validate_play_store_url(request.url)
        
        # Validate dates
        validate_dates(request.from_date, request.to_date)
        
        # Parse dates
        from_date = datetime.strptime(request.from_date, "%Y-%m-%d").date()
        to_date = datetime.strptime(request.to_date, "%Y-%m-%d").date()
        
        # Scrape reviews
        scraper = ReviewScraper()
        reviews = scraper.scrape(
            package_id=package_id,
            from_date=from_date,
            to_date=to_date,
            rating=request.rating,
            hint=request.hint
        )
        
        if not reviews:
            return {
                "success": False,
                "message": "No matching reviews found for the selected filters.",
                "count": 0,
                "preview": [],
                "filename": None
            }
        
        # Generate Excel file
        generator = ExcelGenerator()
        
        # Determine filename as: AppName_Hint_Date.xlsx
        app_name = get_app_name(package_id)
        filename = generator.get_filename(
            app_name=app_name,
            hint=request.hint,
            from_date=request.from_date,
            to_date=request.to_date
        )
        
        filepath = OUTPUT_DIR / filename
        
        generator.generate(reviews, filepath)
        
        # Prepare preview (first 20 rows)
        preview = []
        for review in reviews[:20]:
            preview.append({
                "User": review.get("User", ""),
                "Review": review.get("Review", ""),
                "Rating": review.get("Rating", ""),
                "Date": review.get("Date", "")
            })
        
        return {
            "success": True,
            "message": f"{len(reviews)} matching reviews found",
            "count": len(reviews),
            "preview": preview,
            "filename": filename
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


from fastapi.responses import FileResponse
from fastapi import HTTPException

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download generated Excel file"""

    # Prevent path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    filepath = OUTPUT_DIR / filename

    print(f"Download requested: {filename}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Full file path: {filepath}")
    print(f"File exists: {filepath.exists()}")

    if not filepath.exists():
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {filename}"
        )

    return FileResponse(
        path=str(filepath),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


# Mount static frontend files AFTER all API routes
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
