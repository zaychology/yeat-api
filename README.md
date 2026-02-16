# 🎵 Yeat API V2 - Complete Setup Guide

**NEW:** Enhanced with features inspired by Juice WRLD API!

A comprehensive RESTful API for Yeat's discography with advanced discovery, filtering, and streaming features.

## 🆕 What's New in V2

### Advanced Features
- ✅ **Statistics Endpoint** - Comprehensive metrics and breakdowns
- ✅ **Advanced Filtering** - Filter by era, category, type, quality, and more
- ✅ **Smart Sorting** - Sort by date, play count, name, etc.
- ✅ **Random Discovery** - Get random songs for discovery
- ✅ **Featured Songs** - Curated high-quality tracks
- ✅ **Batch Operations** - Get multiple songs in one request
- ✅ **Audio Streaming** - Direct streaming support
- ✅ **Enhanced Metadata** - Tags, track titles, recording details
- ✅ **Category System** - Better organization (grails, snippets, demos, etc.)
- ✅ **Play Counting** - Track song popularity

### Enhanced Database
- Multiple track titles support
- Tagging system for better discovery
- Recording session details
- Engineer and location tracking
- Instrumental tracking
- Multiple download links (YouTube, SoundCloud, Spotify)
- Popularity metrics (play count, download count)

---

## 📋 Quick Start

### 1. Choose Your Version

**Supabase-py** (Recommended for beginners)
- Simple, straightforward
- Less code
- Perfect for learning

**SQLAlchemy** (Recommended for production)
- More powerful
- Better type safety
- Industry standard

### 2. Set Up Database

```sql
-- Run schema.sql in your Supabase SQL Editor
-- This creates the enhanced table with all new fields
```

### 3. Install & Run

```bash
# Choose your version
cp main_supabase.py main.py  # OR main_sqlalchemy.py
cp requirements_supabase.txt requirements.txt  # OR requirements_sqlalchemy.txt

# Set up environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your credentials

# Run!
python main.py
```

Visit `http://localhost:8000/docs` for interactive API documentation!

---

## 📖 API Endpoints

### 🔓 Public Endpoints (No Auth Required)

#### Core Endpoints
```
GET  /                   - Welcome message
GET  /health             - Health check
GET  /stats              - Comprehensive statistics ⭐ NEW
```

#### Song Discovery
```
GET  /songs              - Paginated list with advanced filters ⭐ ENHANCED
GET  /songs/{id}         - Get specific song details
GET  /songs/random/pick  - Get random song for discovery ⭐ NEW
GET  /songs/featured/list - Get featured high-quality songs ⭐ NEW
POST /songs/batch        - Get multiple songs by IDs ⭐ NEW
```

#### Search & Browse
```
GET  /search             - Search songs (enhanced multi-field) ⭐ ENHANCED
GET  /eras               - List eras with counts ⭐ ENHANCED
GET  /categories         - List categories with counts ⭐ NEW
```

#### Streaming
```
GET  /stream/{id}        - Stream audio file ⭐ NEW
```

### 🔐 Private Endpoints (API Key Required)

```
POST   /songs/add        - Add new song
PUT    /songs/{id}       - Update song
DELETE /songs/{id}       - Delete song ⭐ NEW
```

---

## 🎯 New Features Guide

### 1. Statistics Endpoint

Get comprehensive API statistics:

```bash
curl http://localhost:8000/stats
```

Returns:
```json
{
  "total_songs": 150,
  "by_era": {
    "2093": 45,
    "Lyfë": 38,
    "Up 2 Më": 32,
    ...
  },
  "by_category": {
    "unreleased_grail": 67,
    "snippet": 23,
    ...
  },
  "lossless_count": 89,
  "songs_with_downloads": 142
}
```

### 2. Advanced Filtering

Filter songs with multiple parameters:

```bash
# Get lossless full-length songs from 2093 era
curl "http://localhost:8000/songs?era=2093&quality=Lossless&available_length=Full"

# Get songs sorted by play count
curl "http://localhost:8000/songs?sort_by=play_count&sort_order=desc"

# Get songs with tags
curl "http://localhost:8000/songs?has_tags=true"
```

Available filters:
- `era` - Filter by era
- `category` - Filter by category (unreleased_grail, snippet, etc.)
- `type` - Filter by type (Throwaway, Demo, OG, etc.)
- `quality` - Filter by quality (Lossless, CD Quality, etc.)
- `available_length` - Full or Partial
- `has_download` - true/false
- `has_tags` - true/false
- `sort_by` - created_at, leak_date, play_count, name
- `sort_order` - asc or desc

### 3. Random Discovery

Get a random song (optionally filtered):

```bash
# Any random song
curl http://localhost:8000/songs/random/pick

# Random song from 2093 era
curl "http://localhost:8000/songs/random/pick?era=2093"

# Random lossless grail
curl "http://localhost:8000/songs/random/pick?category=unreleased_grail&quality=Lossless"
```

### 4. Featured Songs

Get curated high-quality songs:

```bash
# Get top 10 featured songs
curl http://localhost:8000/songs/featured/list

# Get top 20
curl "http://localhost:8000/songs/featured/list?limit=20"
```

Returns highest-quality, full-length songs with downloads, sorted by recency.

### 5. Batch Operations

Get multiple songs in one request:

```bash
# Get songs with IDs 1, 5, and 10
curl "http://localhost:8000/songs/batch?song_ids=1&song_ids=5&song_ids=10"
```

Perfect for:
- Building playlists
- Comparing versions
- Bulk operations

### 6. Audio Streaming

Stream songs directly in browser:

```bash
# Stream song with ID 1
curl http://localhost:8000/stream/1
```

Works with HTML5 audio players:
```html
<audio controls>
  <source src="http://localhost:8000/stream/1" type="audio/mpeg">
</audio>
```

### 7. Enhanced Metadata

Songs now include:

```json
{
  "id": 1,
  "song_name": "Sample Song",
  "track_titles": ["Sample Song", "Alt Name 1", "Alt Name 2"],
  "tags": ["hype", "rage", "melodic"],
  "category": "unreleased_grail",
  "recording_locations": "Recording Academy, Los Angeles, CA",
  "record_dates": "Recorded June 15, 2023",
  "session_tracking": "27 stem tracks, 44 vocal takes",
  "engineers": "Mike Dean, Alex Tumay",
  "instrumental_names": "Sample_Instrumental_V2",
  "youtube_link": "https://youtube.com/...",
  "soundcloud_link": "https://soundcloud.com/...",
  "play_count": 142,
  "download_count": 89
}
```

### 8. Categories System

New category types:
- `released_album` - Official album releases
- `released_single` - Official singles
- `unreleased_grail` - High-demand unreleased
- `unreleased_throwaway` - Throwaway tracks
- `snippet` - Short previews
- `demo` - Demo versions
- `og_version` - Original versions
- `alternate_version` - Alternative takes
- `live_performance` - Live recordings
- `freestyle` - Freestyle recordings
- `reference` - Reference tracks
- `session` - Studio sessions

List all categories:
```bash
curl http://localhost:8000/categories
```

---

## 🗄️ Database Schema Changes

### New Fields

```sql
-- Multiple track titles
track_titles TEXT[]

-- Category system
category VARCHAR(50)

-- Tags for discovery
tags TEXT[]

-- Recording details
recording_locations TEXT
record_dates TEXT
session_titles TEXT
session_tracking TEXT
engineers TEXT

-- Instrumental tracking
instrumental_names TEXT
instrumental_links TEXT

-- Additional links
youtube_link TEXT
soundcloud_link TEXT
spotify_link TEXT

-- Popularity metrics
play_count INTEGER DEFAULT 0
download_count INTEGER DEFAULT 0
```

---

## 📊 Example Queries

### Get Statistics Dashboard

```python
import requests

stats = requests.get("http://localhost:8000/stats").json()

print(f"Total Songs: {stats['total_songs']}")
print(f"Lossless: {stats['lossless_count']}")
print(f"By Era: {stats['by_era']}")
```

### Build a Discovery Feature

```python
# Get random song for user
random_song = requests.get(
    "http://localhost:8000/songs/random/pick?quality=Lossless"
).json()

print(f"Discover: {random_song['song_name']}")
print(f"Stream: http://localhost:8000/stream/{random_song['id']}")
```

### Filter by Multiple Criteria

```python
# Get hype songs from 2093 era
params = {
    "era": "2093",
    "quality": "Lossless",
    "available_length": "Full",
    "sort_by": "play_count",
    "sort_order": "desc",
    "page_size": 20
}

songs = requests.get("http://localhost:8000/songs", params=params).json()

for song in songs['songs']:
    if 'hype' in song.get('tags', []):
        print(f"🔥 {song['song_name']}")
```

### Get Featured Playlist

```python
# Get top 10 featured songs
featured = requests.get(
    "http://localhost:8000/songs/featured/list?limit=10"
).json()

playlist = [
    {
        "name": song['song_name'],
        "artist": song['main_artist'],
        "features": ", ".join(song['features']),
        "stream_url": f"http://localhost:8000/stream/{song['id']}"
    }
    for song in featured
]

print(json.dumps(playlist, indent=2))
```

---

## 🚀 Deployment

Same as V1 - works on Render, Koyeb, Railway, etc.

```bash
# 1. Push to GitHub
git init
git add .
git commit -m "Yeat API V2"
git push

# 2. Deploy on Render/Koyeb
# 3. Set environment variables
# 4. Done!
```

---

## 🔧 Migration from V1

If you have V1 running:

1. **Backup your database**
```sql
-- Export your existing data
```

2. **Run migration**
```sql
-- Add new columns to existing table
ALTER TABLE unreleased_songs ADD COLUMN track_titles TEXT[];
ALTER TABLE unreleased_songs ADD COLUMN category VARCHAR(50);
ALTER TABLE unreleased_songs ADD COLUMN tags TEXT[];
-- etc. (see schema.sql for all new fields)
```

3. **Update code**
- Replace main.py with V2 version
- Update requirements.txt
- Restart server

---

## 📖 Full Documentation

- **QUICKSTART.md** - Beginner-friendly guide
- **COMPARISON.md** - Supabase vs SQLAlchemy
- **API_EXAMPLES.md** - Code examples for all endpoints
- Interactive docs at `/docs` when running

---

## 💡 Best Practices

### For Frontend Developers

```javascript
// Use minimal endpoint for lists
const songs = await fetch('/songs?page=1&page_size=20');

// Use full endpoint for details
const song = await fetch(`/songs/${id}`);

// Use streaming for player
<audio src={`/stream/${songId}`} controls />

// Use random for discovery
const discover = await fetch('/songs/random/pick?quality=Lossless');
```

### For Data Analysis

```python
# Get comprehensive stats
stats = requests.get('/stats').json()

# Filter and analyze
high_quality = requests.get('/songs?quality=Lossless&available_length=Full').json()

# Track trends
popular = requests.get('/songs?sort_by=play_count&sort_order=desc&page_size=50').json()
```

---

## 🆘 Troubleshooting

### "Column doesn't exist" errors
Run the new `schema.sql` or add missing columns with ALTER TABLE

### Filters not working
Check the field name matches exactly (case-sensitive)

### Streaming not working
Make sure Pillowcase links are valid and accessible

---

## 🎯 What's Next?

Planned features:
- Playlist system
- Version tracking (OG, CDQ, Remaster)
- Lyrics support
- Audio metadata analysis
- User favorites/bookmarks

---

**Built with ❤️ for the Yeat community**

Version 2.0.0 - Enhanced Edition
