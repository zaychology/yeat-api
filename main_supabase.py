"""
YEAT API V2 - Enhanced FastAPI Backend with Supabase
=====================================================
A comprehensive RESTful API for Yeat's discography with advanced features
inspired by Juice WRLD API.

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
from datetime import date

from fastapi import FastAPI, HTTPException, Security, Query, status, Header
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, RedirectResponse
from pydantic import BaseModel, Field
from supabase import create_client, Client
from dotenv import load_dotenv
import requests

# Import our utility functions
from utils import (
    parse_song_name, 
    convert_pillowcase_link, 
    format_song_response,
    format_minimal_song,
    search_in_song,
    validate_category,
    get_quality_rank
)

# Load environment variables
load_dotenv()

# ============================================
# CONFIGURATION
# ============================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
API_KEY = os.getenv("API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")

if not API_KEY:
    raise ValueError("API_KEY must be set in .env file for admin endpoints")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ============================================
# FASTAPI APP SETUP
# ============================================

app = FastAPI(
    title="Yeat API V2",
    description="Comprehensive RESTful API for Yeat's discography with advanced features",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# SECURITY
# ============================================

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify the API key for admin endpoints."""
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
    """Complete song response with all metadata"""
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
    """Minimal song info for list views"""
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
    """Paginated song list response"""
    total: int
    page: int
    page_size: int
    total_pages: int
    filters_applied: dict
    songs: List[MinimalSongResponse]

class StatsResponse(BaseModel):
    """API statistics response"""
    total_songs: int
    by_era: dict
    by_category: dict
    by_type: dict
    by_quality: dict
    lossless_count: int
    full_length_count: int
    songs_with_downloads: int

class MessageResponse(BaseModel):
    """Simple message response"""
    message: str

# ============================================
# PUBLIC ENDPOINTS
# ============================================

@app.get("/", response_model=MessageResponse)
async def root():
    """Welcome message and API info"""
    return {
        "message": "Welcome to Yeat API V2! Enhanced with advanced features. Visit /docs for documentation."
    }

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get comprehensive API statistics.
    
    Returns:
        - Total song count
        - Breakdown by era, category, type, quality
        - High-quality songs count
        - Songs with downloads
    """
    try:
        # Get all songs
        response = supabase.table("unreleased_songs").select("*").execute()
        songs = response.data
        
        # Calculate statistics
        total_songs = len(songs)
        
        # Group by era
        by_era = {}
        for song in songs:
            era = song.get('era', 'Unknown')
            by_era[era] = by_era.get(era, 0) + 1
        
        # Group by category
        by_category = {}
        for song in songs:
            category = song.get('category', 'uncategorized')
            by_category[category] = by_category.get(category, 0) + 1
        
        # Group by type
        by_type = {}
        for song in songs:
            song_type = song.get('type', 'Unknown')
            by_type[song_type] = by_type.get(song_type, 0) + 1
        
        # Group by quality
        by_quality = {}
        for song in songs:
            quality = song.get('quality', 'Unknown')
            by_quality[quality] = by_quality.get(quality, 0) + 1
        
        # Count special categories
        lossless_count = sum(1 for s in songs if s.get('quality') == 'Lossless')
        full_length_count = sum(1 for s in songs if s.get('available_length') == 'Full')
        songs_with_downloads = sum(1 for s in songs if s.get('links'))
        
        return {
            "total_songs": total_songs,
            "by_era": by_era,
            "by_category": by_category,
            "by_type": by_type,
            "by_quality": by_quality,
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
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Songs per page"),
    era: Optional[str] = Query(None, description="Filter by era"),
    category: Optional[str] = Query(None, description="Filter by category"),
    type: Optional[str] = Query(None, description="Filter by type"),
    quality: Optional[str] = Query(None, description="Filter by quality"),
    available_length: Optional[str] = Query(None, description="Filter by length (Full/Partial)"),
    has_download: Optional[bool] = Query(None, description="Filter songs with download links"),
    has_tags: Optional[bool] = Query(None, description="Filter songs with tags"),
    sort_by: str = Query("created_at", description="Sort field (created_at, leak_date, play_count, name)"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)")
):
    """
    Get songs with advanced filtering, sorting, and pagination.
    
    **Filters:**
    - era: Filter by specific era
    - category: Filter by category (released_album, unreleased_grail, etc.)
    - type: Filter by type (Throwaway, Demo, OG, etc.)
    - quality: Filter by quality (Lossless, CD Quality, etc.)
    - available_length: Full or Partial
    - has_download: true/false - songs with/without download links
    - has_tags: true/false - songs with/without tags
    
    **Sorting:**
    - sort_by: created_at, leak_date, play_count, name
    - sort_order: asc or desc
    """
    try:
        # Build query
        query = supabase.table("unreleased_songs").select("*", count="exact")
        
        # Apply filters
        if era:
            query = query.eq("era", era)
        if category:
            query = query.eq("category", category)
        if type:
            query = query.eq("type", type)
        if quality:
            query = query.eq("quality", quality)
        if available_length:
            query = query.eq("available_length", available_length)
        if has_download is not None:
            if has_download:
                query = query.not_.is_("links", "null")
            else:
                query = query.is_("links", "null")
        
        # Note: has_tags filter requires fetching and filtering in Python
        # as Supabase doesn't support array length filters directly
        
        # Apply sorting
        if sort_order == "desc":
            query = query.order(sort_by, desc=True)
        else:
            query = query.order(sort_by, desc=False)
        
        # Get total count
        count_response = query.execute()
        total_count = count_response.count
        
        # Apply pagination
        offset = (page - 1) * page_size
        response = query.range(offset, offset + page_size - 1).execute()
        songs = response.data
        
        # Apply has_tags filter if needed (post-query filtering)
        if has_tags is not None:
            if has_tags:
                songs = [s for s in songs if s.get('tags') and len(s.get('tags', [])) > 0]
            else:
                songs = [s for s in songs if not s.get('tags') or len(s.get('tags', [])) == 0]
            total_count = len(songs)
        
        # Format songs with minimal info
        formatted_songs = [format_minimal_song(song) for song in songs]
        
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
                "has_tags": has_tags,
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
async def get_song(song_id: int):
    """
    Get complete details for a specific song by ID.
    
    Includes all metadata, parsed fields, and links.
    """
    try:
        response = supabase.table("unreleased_songs") \
            .select("*") \
            .eq("id", song_id) \
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Song with ID {song_id} not found"
            )
        
        song = response.data[0]
        
        # Increment play count
        try:
            new_count = (song.get('play_count') or 0) + 1
            supabase.table("unreleased_songs") \
                .update({"play_count": new_count}) \
                .eq("id", song_id) \
                .execute()
        except:
            pass  # Don't fail if play count update fails
        
        return format_song_response(song)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching song: {str(e)}"
        )

@app.get("/songs/random/pick", response_model=SongResponse)
async def get_random_song(
    era: Optional[str] = Query(None, description="Filter by era"),
    category: Optional[str] = Query(None, description="Filter by category"),
    quality: Optional[str] = Query(None, description="Filter by quality")
):
    """
    Get a random song for discovery!
    
    Optional filters:
    - era: Get random song from specific era
    - category: Get random song from specific category
    - quality: Get random song with specific quality
    """
    try:
        # Build query with filters
        query = supabase.table("unreleased_songs").select("*")
        
        if era:
            query = query.eq("era", era)
        if category:
            query = query.eq("category", category)
        if quality:
            query = query.eq("quality", quality)
        
        # Get all matching songs
        response = query.execute()
        songs = response.data
        
        if not songs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No songs found matching the filters"
            )
        
        # Pick random song (Python random since Supabase doesn't support ORDER BY RANDOM)
        import random
        random_song = random.choice(songs)
        
        return format_song_response(random_song)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting random song: {str(e)}"
        )

@app.get("/songs/featured/list", response_model=List[SongResponse])
async def get_featured_songs(
    limit: int = Query(10, ge=1, le=50, description="Number of featured songs to return")
):
    """
    Get featured songs (high-quality, full-length, recent additions).
    
    Returns the best songs in the collection:
    - Lossless or CD Quality
    - Full length
    - Has download link
    - Recently added
    """
    try:
        response = supabase.table("unreleased_songs") \
            .select("*") \
            .in_("quality", ["Lossless", "CD Quality"]) \
            .eq("available_length", "Full") \
            .not_.is_("links", "null") \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        
        songs = response.data
        return [format_song_response(song) for song in songs]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching featured songs: {str(e)}"
        )

@app.post("/songs/batch", response_model=List[SongResponse])
async def get_songs_batch(song_ids: List[int] = Query(..., description="List of song IDs")):
    """
    Get multiple songs by their IDs in a single request.
    
    Useful for:
    - Building playlists
    - Batch downloading
    - Comparing different versions
    
    Example: `/songs/batch?song_ids=1&song_ids=5&song_ids=10`
    """
    try:
        if not song_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one song_id is required"
            )
        
        if len(song_ids) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 50 songs per batch request"
            )
        
        response = supabase.table("unreleased_songs") \
            .select("*") \
            .in_("id", song_ids) \
            .execute()
        
        songs = response.data
        return [format_song_response(song) for song in songs]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching batch songs: {str(e)}"
        )

@app.get("/search", response_model=List[SongResponse])
async def search_songs(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results to return")
):
    """
    Search for songs by name, alt name, producer, features, tags, or notes.
    
    Searches across multiple fields:
    - Song name
    - Alternative names
    - Producers
    - Featured artists
    - Tags
    - Era
    - Notes
    """
    try:
        # Get all songs (in production with many songs, use PostgreSQL full-text search)
        response = supabase.table("unreleased_songs").select("*").execute()
        
        # Filter using search utility
        matching_songs = []
        for song in response.data:
            if search_in_song(song, q):
                matching_songs.append(format_song_response(song))
                if len(matching_songs) >= limit:
                    break
        
        return matching_songs
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching songs: {str(e)}"
        )

@app.get("/eras", response_model=dict)
async def get_eras():
    """
    Get list of unique eras with song counts.
    """
    try:
        response = supabase.table("unreleased_songs").select("era").execute()
        
        # Count songs per era
        era_counts = {}
        for song in response.data:
            era = song.get('era') or 'Unknown'
            era_counts[era] = era_counts.get(era, 0) + 1
        
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
async def get_categories():
    """
    Get list of available song categories with counts.
    """
    try:
        response = supabase.table("unreleased_songs").select("category").execute()
        
        # Count songs per category
        category_counts = {}
        for song in response.data:
            category = song.get('category') or 'uncategorized'
            category_counts[category] = category_counts.get(category, 0) + 1
        
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
async def stream_song(song_id: int):
    """
    Stream audio file for a song (returns redirect to download URL).
    
    For direct in-browser playback. Supports range requests for seeking.
    """
    try:
        # Get song
        response = supabase.table("unreleased_songs") \
            .select("links, name") \
            .eq("id", song_id) \
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Song not found"
            )
        
        song = response.data[0]
        
        if not song.get('links'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No download link available for this song"
            )
        
        # Convert to download URL
        download_url = convert_pillowcase_link(song['links'])
        
        if not download_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid download link"
            )
        
        # Redirect to the download URL (which can be streamed)
        return RedirectResponse(url=download_url)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error streaming song: {str(e)}"
        )

# ============================================
# PRIVATE ENDPOINTS (ADMIN ONLY)
# ============================================

@app.post("/songs/add", response_model=SongResponse, dependencies=[Security(verify_api_key)])
async def add_song(song: SongBase):
    """
    Add a new song to the database.
    
    **Requires authentication**: X-API-Key header
    """
    try:
        # Validate category
        if song.category and not validate_category(song.category):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category: {song.category}"
            )
        
        # Convert model to dict
        song_data = song.model_dump()
        
        # Convert dates to strings
        for date_field in ['file_date', 'first_preview', 'leak_date', 'og_file_leak_date']:
            if song_data.get(date_field):
                song_data[date_field] = str(song_data[date_field])
        
        # Insert
        response = supabase.table("unreleased_songs").insert(song_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add song"
            )
        
        return format_song_response(response.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding song: {str(e)}"
        )

@app.put("/songs/{song_id}", response_model=SongResponse, dependencies=[Security(verify_api_key)])
async def update_song(song_id: int, song: SongBase):
    """
    Update an existing song.
    
    **Requires authentication**: X-API-Key header
    """
    try:
        # Check if exists
        check = supabase.table("unreleased_songs") \
            .select("id") \
            .eq("id", song_id) \
            .execute()
        
        if not check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Song with ID {song_id} not found"
            )
        
        # Validate category
        if song.category and not validate_category(song.category):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category: {song.category}"
            )
        
        # Convert model to dict
        song_data = song.model_dump()
        
        # Convert dates
        for date_field in ['file_date', 'first_preview', 'leak_date', 'og_file_leak_date']:
            if song_data.get(date_field):
                song_data[date_field] = str(song_data[date_field])
        
        # Update
        response = supabase.table("unreleased_songs") \
            .update(song_data) \
            .eq("id", song_id) \
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update song"
            )
        
        return format_song_response(response.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating song: {str(e)}"
        )

@app.delete("/songs/{song_id}", response_model=MessageResponse, dependencies=[Security(verify_api_key)])
async def delete_song(song_id: int):
    """
    Delete a song from the database.
    
    **Requires authentication**: X-API-Key header
    """
    try:
        # Check if exists
        check = supabase.table("unreleased_songs") \
            .select("id") \
            .eq("id", song_id) \
            .execute()
        
        if not check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Song with ID {song_id} not found"
            )
        
        # Delete
        supabase.table("unreleased_songs") \
            .delete() \
            .eq("id", song_id) \
            .execute()
        
        return {"message": f"Song {song_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting song: {str(e)}"
        )

# ============================================
# HEALTH CHECK
# ============================================

@app.get("/health", response_model=MessageResponse)
async def health_check():
    """Health check endpoint"""
    try:
        supabase.table("unreleased_songs").select("id").limit(1).execute()
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
