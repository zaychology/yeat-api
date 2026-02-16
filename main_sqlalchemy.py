"""
YEAT API V2 - Enhanced FastAPI Backend with SQLAlchemy
=======================================================
A comprehensive RESTful API for Yeat's discography with advanced features
inspired by Juice WRLD API using SQLAlchemy ORM.

NEW FEATURES:
- Statistics endpoint with comprehensive metrics
- Advanced filtering and sorting
- Random and featured song discovery  
- Audio streaming support
- Enhanced metadata (tags, track_titles, etc.)
- Batch operations
- Better category system
"""

import os
from typing import Optional, List
from datetime import date, datetime
import random

from fastapi import FastAPI, HTTPException, Security, Query, status, Depends
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, BigInteger, String, Text, Date, DateTime, Integer
from sqlalchemy import func, or_, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from dotenv import load_dotenv

# Import utilities
from utils import (
    parse_song_name,
    convert_pillowcase_link,
    format_song_response,
    format_minimal_song,
    search_in_song,
    validate_category
)

load_dotenv()

# ============================================
# CONFIGURATION
# ============================================

SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")
API_KEY = os.getenv("API_KEY")

if not SUPABASE_DB_URL:
    raise ValueError("SUPABASE_DB_URL must be set in .env file")

if not API_KEY:
    raise ValueError("API_KEY must be set in .env file")

# ============================================
# DATABASE SETUP
# ============================================

engine = create_engine(SUPABASE_DB_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================
# DATABASE MODEL
# ============================================

class UnreleasedSong(Base):
    """SQLAlchemy model for unreleased_songs table"""
    __tablename__ = "unreleased_songs"
    
    id = Column(BigInteger, primary_key=True, index=True)
    
    # Basic info
    era = Column(String(100), nullable=True, index=True)
    name = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Enhanced metadata
    track_titles = Column(PG_ARRAY(Text), nullable=True)
    category = Column(String(50), nullable=True, index=True)
    tags = Column(PG_ARRAY(Text), nullable=True)
    
    # Audio info
    track_length = Column(String(20), nullable=True)
    type = Column(String(50), nullable=True, index=True)
    available_length = Column(String(20), nullable=True)
    quality = Column(String(50), nullable=True, index=True)
    
    # Dates
    file_date = Column(Date, nullable=True)
    first_preview = Column(Date, nullable=True)
    leak_date = Column(Date, nullable=True, index=True)
    og_file_leak_date = Column(Date, nullable=True)
    
    # Recording details
    recording_locations = Column(Text, nullable=True)
    record_dates = Column(Text, nullable=True)
    session_titles = Column(Text, nullable=True)
    session_tracking = Column(Text, nullable=True)
    engineers = Column(Text, nullable=True)
    
    # Instrumental details
    instrumental_names = Column(Text, nullable=True)
    instrumental_links = Column(Text, nullable=True)
    
    # Links
    links = Column(Text, nullable=True)
    youtube_link = Column(Text, nullable=True)
    soundcloud_link = Column(Text, nullable=True)
    spotify_link = Column(Text, nullable=True)
    
    # Popularity
    play_count = Column(Integer, default=0, index=True)
    download_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """Convert ORM object to dictionary"""
        return {
            'id': self.id,
            'era': self.era,
            'name': self.name,
            'notes': self.notes,
            'track_titles': self.track_titles,
            'category': self.category,
            'tags': self.tags,
            'track_length': self.track_length,
            'type': self.type,
            'available_length': self.available_length,
            'quality': self.quality,
            'file_date': self.file_date,
            'first_preview': self.first_preview,
            'leak_date': self.leak_date,
            'og_file_leak_date': self.og_file_leak_date,
            'recording_locations': self.recording_locations,
            'record_dates': self.record_dates,
            'session_titles': self.session_titles,
            'session_tracking': self.session_tracking,
            'engineers': self.engineers,
            'instrumental_names': self.instrumental_names,
            'instrumental_links': self.instrumental_links,
            'links': self.links,
            'youtube_link': self.youtube_link,
            'soundcloud_link': self.soundcloud_link,
            'spotify_link': self.spotify_link,
            'play_count': self.play_count,
            'download_count': self.download_count,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

# ============================================
# FASTAPI APP SETUP
# ============================================

app = FastAPI(
    title="Yeat API V2 (SQLAlchemy)",
    description="Comprehensive RESTful API for Yeat's discography - SQLAlchemy Version",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# DATABASE DEPENDENCY
# ============================================

def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================
# SECURITY
# ============================================

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key for admin endpoints"""
    if not api_key or api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key"
        )
    return api_key

# ============================================
# PYDANTIC MODELS
# ============================================

class SongBase(BaseModel):
    """Base model for creating/updating songs"""
    era: Optional[str] = None
    name: str
    notes: Optional[str] = None
    track_length: Optional[str] = None
    type: Optional[str] = None
    available_length: Optional[str] = None
    quality: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    track_titles: Optional[List[str]] = None
    file_date: Optional[date] = None
    first_preview: Optional[date] = None
    leak_date: Optional[date] = None
    og_file_leak_date: Optional[date] = None
    recording_locations: Optional[str] = None
    record_dates: Optional[str] = None
    session_titles: Optional[str] = None
    session_tracking: Optional[str] = None
    engineers: Optional[str] = None
    instrumental_names: Optional[str] = None
    instrumental_links: Optional[str] = None
    links: Optional[str] = None
    youtube_link: Optional[str] = None
    soundcloud_link: Optional[str] = None
    spotify_link: Optional[str] = None

class SongResponse(BaseModel):
    """Complete song response"""
    id: int
    song_name: str
    main_artist: str
    features: List[str]
    producers: List[str]
    alt_names: List[str]
    track_titles: List[str]
    era: Optional[str]
    category: Optional[str]
    quality: Optional[str]
    available_length: Optional[str]
    track_length: Optional[str]
    type: Optional[str]
    tags: List[str]
    raw_name: str
    file_date: Optional[str]
    first_preview: Optional[str]
    leak_date: Optional[str]
    og_file_leak_date: Optional[str]
    recording_locations: Optional[str]
    record_dates: Optional[str]
    session_titles: Optional[str]
    session_tracking: Optional[str]
    engineers: Optional[str]
    instrumental_names: Optional[str]
    instrumental_links: Optional[str]
    pillowcase_link: Optional[str]
    download_link: Optional[str]
    youtube_link: Optional[str]
    soundcloud_link: Optional[str]
    spotify_link: Optional[str]
    play_count: int
    download_count: int
    notes: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]

class MinimalSongResponse(BaseModel):
    """Minimal song info for lists"""
    id: int
    song_name: str
    main_artist: str
    features: List[str]
    era: Optional[str]
    category: Optional[str]
    quality: Optional[str]
    track_length: Optional[str]
    has_download: bool
    tags: List[str]

class PaginatedSongsResponse(BaseModel):
    """Paginated response"""
    total: int
    page: int
    page_size: int
    total_pages: int
    filters_applied: dict
    songs: List[MinimalSongResponse]

class StatsResponse(BaseModel):
    """Statistics response"""
    total_songs: int
    by_era: dict
    by_category: dict
    by_type: dict
    by_quality: dict
    lossless_count: int
    full_length_count: int
    songs_with_downloads: int

class MessageResponse(BaseModel):
    """Simple message"""
    message: str

# ============================================
# PUBLIC ENDPOINTS
# ============================================

@app.get("/", response_model=MessageResponse)
async def root():
    """Welcome message"""
    return {
        "message": "Welcome to Yeat API V2 (SQLAlchemy)! Visit /docs for documentation."
    }

@app.get("/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """Get comprehensive API statistics"""
    try:
        total_songs = db.query(UnreleasedSong).count()
        
        # Count by era
        era_counts = {}
        for era, count in db.query(UnreleasedSong.era, func.count(UnreleasedSong.id)) \
                .group_by(UnreleasedSong.era).all():
            era_counts[era or 'Unknown'] = count
        
        # Count by category
        category_counts = {}
        for category, count in db.query(UnreleasedSong.category, func.count(UnreleasedSong.id)) \
                .group_by(UnreleasedSong.category).all():
            category_counts[category or 'uncategorized'] = count
        
        # Count by type
        type_counts = {}
        for song_type, count in db.query(UnreleasedSong.type, func.count(UnreleasedSong.id)) \
                .group_by(UnreleasedSong.type).all():
            type_counts[song_type or 'Unknown'] = count
        
        # Count by quality
        quality_counts = {}
        for quality, count in db.query(UnreleasedSong.quality, func.count(UnreleasedSong.id)) \
                .group_by(UnreleasedSong.quality).all():
            quality_counts[quality or 'Unknown'] = count
        
        # Special counts
        lossless_count = db.query(UnreleasedSong).filter(UnreleasedSong.quality == 'Lossless').count()
        full_length_count = db.query(UnreleasedSong).filter(UnreleasedSong.available_length == 'Full').count()
        songs_with_downloads = db.query(UnreleasedSong).filter(UnreleasedSong.links.isnot(None)).count()
        
        return {
            "total_songs": total_songs,
            "by_era": era_counts,
            "by_category": category_counts,
            "by_type": type_counts,
            "by_quality": quality_counts,
            "lossless_count": lossless_count,
            "full_length_count": full_length_count,
            "songs_with_downloads": songs_with_downloads
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching statistics: {str(e)}"
        )

@app.get("/songs", response_model=PaginatedSongsResponse)
async def get_songs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    era: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    quality: Optional[str] = Query(None),
    available_length: Optional[str] = Query(None),
    has_download: Optional[bool] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db)
):
    """Get songs with advanced filtering and sorting"""
    try:
        # Build query
        query = db.query(UnreleasedSong)
        
        # Apply filters
        if era:
            query = query.filter(UnreleasedSong.era == era)
        if category:
            query = query.filter(UnreleasedSong.category == category)
        if type:
            query = query.filter(UnreleasedSong.type == type)
        if quality:
            query = query.filter(UnreleasedSong.quality == quality)
        if available_length:
            query = query.filter(UnreleasedSong.available_length == available_length)
        if has_download is not None:
            if has_download:
                query = query.filter(UnreleasedSong.links.isnot(None))
            else:
                query = query.filter(UnreleasedSong.links.is_(None))
        
        # Get total count
        total_count = query.count()
        
        # Apply sorting
        if hasattr(UnreleasedSong, sort_by):
            if sort_order == "desc":
                query = query.order_by(getattr(UnreleasedSong, sort_by).desc())
            else:
                query = query.order_by(getattr(UnreleasedSong, sort_by).asc())
        
        # Apply pagination
        offset = (page - 1) * page_size
        songs = query.offset(offset).limit(page_size).all()
        
        # Format songs
        formatted_songs = [format_minimal_song(song.to_dict()) for song in songs]
        
        total_pages = (total_count + page_size - 1) // page_size
        
        return {
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "filters_applied": {
                "era": era,
                "category": category,
                "type": type,
                "quality": quality,
                "available_length": available_length,
                "has_download": has_download,
                "sort_by": sort_by,
                "sort_order": sort_order
            },
            "songs": formatted_songs
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching songs: {str(e)}"
        )

@app.get("/songs/{song_id}", response_model=SongResponse)
async def get_song(song_id: int, db: Session = Depends(get_db)):
    """Get complete song details by ID"""
    try:
        song = db.query(UnreleasedSong).filter(UnreleasedSong.id == song_id).first()
        
        if not song:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Song with ID {song_id} not found"
            )
        
        # Increment play count
        try:
            song.play_count = (song.play_count or 0) + 1
            db.commit()
        except:
            db.rollback()
        
        return format_song_response(song.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching song: {str(e)}"
        )

@app.get("/songs/random/pick", response_model=SongResponse)
async def get_random_song(
    era: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    quality: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get a random song for discovery"""
    try:
        query = db.query(UnreleasedSong)
        
        if era:
            query = query.filter(UnreleasedSong.era == era)
        if category:
            query = query.filter(UnreleasedSong.category == category)
        if quality:
            query = query.filter(UnreleasedSong.quality == quality)
        
        # Get random song using PostgreSQL's random()
        song = query.order_by(func.random()).first()
        
        if not song:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No songs found matching the filters"
            )
        
        return format_song_response(song.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting random song: {str(e)}"
        )

@app.get("/songs/featured/list", response_model=List[SongResponse])
async def get_featured_songs(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get featured high-quality songs"""
    try:
        songs = db.query(UnreleasedSong) \
            .filter(UnreleasedSong.quality.in_(['Lossless', 'CD Quality'])) \
            .filter(UnreleasedSong.available_length == 'Full') \
            .filter(UnreleasedSong.links.isnot(None)) \
            .order_by(UnreleasedSong.created_at.desc()) \
            .limit(limit) \
            .all()
        
        return [format_song_response(song.to_dict()) for song in songs]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching featured songs: {str(e)}"
        )

@app.post("/songs/batch", response_model=List[SongResponse])
async def get_songs_batch(
    song_ids: List[int] = Query(...),
    db: Session = Depends(get_db)
):
    """Get multiple songs by IDs"""
    try:
        if not song_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one song_id is required"
            )
        
        if len(song_ids) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 50 songs per batch"
            )
        
        songs = db.query(UnreleasedSong) \
            .filter(UnreleasedSong.id.in_(song_ids)) \
            .all()
        
        return [format_song_response(song.to_dict()) for song in songs]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching batch songs: {str(e)}"
        )

@app.get("/search", response_model=List[SongResponse])
async def search_songs(
    q: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search songs across multiple fields"""
    try:
        # Use PostgreSQL's ILIKE for case-insensitive search
        songs = db.query(UnreleasedSong) \
            .filter(UnreleasedSong.name.ilike(f"%{q}%")) \
            .limit(limit) \
            .all()
        
        # Additional filtering with parsed fields
        matching_songs = []
        for song in songs:
            if search_in_song(song.to_dict(), q):
                matching_songs.append(format_song_response(song.to_dict()))
        
        return matching_songs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching songs: {str(e)}"
        )

@app.get("/eras", response_model=dict)
async def get_eras(db: Session = Depends(get_db)):
    """Get list of eras with counts"""
    try:
        eras = db.query(UnreleasedSong.era, func.count(UnreleasedSong.id)) \
            .filter(UnreleasedSong.era.isnot(None)) \
            .group_by(UnreleasedSong.era) \
            .all()
        
        era_counts = {era: count for era, count in eras}
        
        return {
            "eras": sorted(era_counts.keys()),
            "counts": era_counts
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching eras: {str(e)}"
        )

@app.get("/categories", response_model=dict)
async def get_categories(db: Session = Depends(get_db)):
    """Get list of categories with counts"""
    try:
        categories = db.query(UnreleasedSong.category, func.count(UnreleasedSong.id)) \
            .group_by(UnreleasedSong.category) \
            .all()
        
        category_counts = {cat or 'uncategorized': count for cat, count in categories}
        
        return {
            "categories": sorted(category_counts.keys()),
            "counts": category_counts
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching categories: {str(e)}"
        )

@app.get("/stream/{song_id}")
async def stream_song(song_id: int, db: Session = Depends(get_db)):
    """Stream audio (redirect to download URL)"""
    try:
        song = db.query(UnreleasedSong).filter(UnreleasedSong.id == song_id).first()
        
        if not song:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Song not found"
            )
        
        if not song.links:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No download link available"
            )
        
        download_url = convert_pillowcase_link(song.links)
        
        if not download_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid download link"
            )
        
        return RedirectResponse(url=download_url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error streaming song: {str(e)}"
        )

# ============================================
# PRIVATE ENDPOINTS
# ============================================

@app.post("/songs/add", response_model=SongResponse, dependencies=[Security(verify_api_key)])
async def add_song(song: SongBase, db: Session = Depends(get_db)):
    """Add new song (admin only)"""
    try:
        if song.category and not validate_category(song.category):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category: {song.category}"
            )
        
        new_song = UnreleasedSong(**song.model_dump())
        db.add(new_song)
        db.commit()
        db.refresh(new_song)
        
        return format_song_response(new_song.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding song: {str(e)}"
        )

@app.put("/songs/{song_id}", response_model=SongResponse, dependencies=[Security(verify_api_key)])
async def update_song(song_id: int, song: SongBase, db: Session = Depends(get_db)):
    """Update song (admin only)"""
    try:
        db_song = db.query(UnreleasedSong).filter(UnreleasedSong.id == song_id).first()
        
        if not db_song:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Song with ID {song_id} not found"
            )
        
        if song.category and not validate_category(song.category):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category: {song.category}"
            )
        
        for key, value in song.model_dump().items():
            setattr(db_song, key, value)
        
        db.commit()
        db.refresh(db_song)
        
        return format_song_response(db_song.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating song: {str(e)}"
        )

@app.delete("/songs/{song_id}", response_model=MessageResponse, dependencies=[Security(verify_api_key)])
async def delete_song(song_id: int, db: Session = Depends(get_db)):
    """Delete song (admin only)"""
    try:
        song = db.query(UnreleasedSong).filter(UnreleasedSong.id == song_id).first()
        
        if not song:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Song with ID {song_id} not found"
            )
        
        db.delete(song)
        db.commit()
        
        return {"message": f"Song {song_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting song: {str(e)}"
        )

# ============================================
# HEALTH CHECK
# ============================================

@app.get("/health", response_model=MessageResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check"""
    try:
        db.query(UnreleasedSong).limit(1).all()
        return {"message": "API is healthy and database connection is active"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )

# ============================================
# RUN APPLICATION
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
