# 🎉 Yeat API V2 - New Features Guide

## What Changed from V1 to V2?

Inspired by the Juice WRLD API, V2 adds powerful discovery, filtering, and metadata features that make your API production-ready and user-friendly.

---

## 📊 1. Statistics Endpoint

**Endpoint:** `GET /stats`

### What It Does
Returns comprehensive statistics about your entire collection.

### Response
```json
{
  "total_songs": 150,
  "by_era": {
    "2093": 45,
    "Lyfë": 38,
    "Up 2 Më": 32,
    "Alivë": 20,
    "Unknown": 15
  },
  "by_category": {
    "unreleased_grail": 67,
    "snippet": 23,
    "demo": 18,
    "released_album": 15
  },
  "by_type": {
    "Throwaway": 42,
    "Demo": 28,
    "OG": 15
  },
  "by_quality": {
    "Lossless": 89,
    "CD Quality": 35,
    "320kbps": 16
  },
  "lossless_count": 89,
  "full_length_count": 112,
  "songs_with_downloads": 142
}
```

### Use Cases
- Dashboard widgets showing collection size
- Charts and visualizations
- Track growth over time
- Show users what's available

---

## 🔍 2. Advanced Filtering

**Endpoint:** `GET /songs` (enhanced)

### New Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `era` | string | Filter by era | `era=2093` |
| `category` | string | Filter by category | `category=unreleased_grail` |
| `type` | string | Filter by type | `type=Throwaway` |
| `quality` | string | Filter by quality | `quality=Lossless` |
| `available_length` | string | Full or Partial | `available_length=Full` |
| `has_download` | boolean | Has download link | `has_download=true` |
| `has_tags` | boolean | Has tags | `has_tags=true` |
| `sort_by` | string | Sort field | `sort_by=play_count` |
| `sort_order` | string | asc or desc | `sort_order=desc` |

### Example Queries

**Get all lossless grails:**
```
GET /songs?category=unreleased_grail&quality=Lossless
```

**Get most played songs:**
```
GET /songs?sort_by=play_count&sort_order=desc&page_size=20
```

**Get recent additions with downloads:**
```
GET /songs?has_download=true&sort_by=created_at&sort_order=desc
```

**Get full-length songs from 2093:**
```
GET /songs?era=2093&available_length=Full
```

### Frontend Example

```javascript
// Build filter UI
const filters = {
  era: selectedEra,
  quality: selectedQuality,
  category: selectedCategory,
  sort_by: 'play_count',
  sort_order: 'desc'
};

const params = new URLSearchParams(filters);
const response = await fetch(`/songs?${params}`);
const data = await response.json();

// data.filters_applied shows what filters were used
console.log('Showing:', data.total, 'songs');
console.log('Filters:', data.filters_applied);
```

---

## 🎲 3. Random Discovery

**Endpoint:** `GET /songs/random/pick`

### What It Does
Returns a random song, optionally filtered by criteria. Perfect for "Surprise Me!" buttons.

### Query Parameters
- `era` - Get random from specific era
- `category` - Get random from specific category
- `quality` - Get random with specific quality

### Examples

**Any random song:**
```
GET /songs/random/pick
```

**Random lossless grail:**
```
GET /songs/random/pick?category=unreleased_grail&quality=Lossless
```

**Random song from 2093:**
```
GET /songs/random/pick?era=2093
```

### Frontend Example

```javascript
// "Surprise Me" button
async function discoverRandomSong() {
  const response = await fetch('/songs/random/pick?quality=Lossless');
  const song = await response.json();
  
  playSong(song.id);
  showSongInfo(song);
}
```

---

## ⭐ 4. Featured Songs

**Endpoint:** `GET /songs/featured/list`

### What It Does
Returns curated high-quality songs (lossless, full-length, with downloads, recently added).

### Query Parameters
- `limit` - Number of songs (1-50, default 10)

### Example
```
GET /songs/featured/list?limit=20
```

### Use Cases
- Landing page "Featured Tracks" section
- "Best of Collection" playlist
- Showcase high-quality content
- Welcome new users with best songs

### Frontend Example

```javascript
// Featured section
async function loadFeaturedSongs() {
  const response = await fetch('/songs/featured/list?limit=10');
  const songs = await response.json();
  
  const featuredHTML = songs.map(song => `
    <div class="featured-song">
      <h3>${song.song_name}</h3>
      <p>${song.quality} • ${song.track_length}</p>
      <button onclick="play(${song.id})">Play</button>
    </div>
  `).join('');
  
  document.getElementById('featured').innerHTML = featuredHTML;
}
```

---

## 📦 5. Batch Operations

**Endpoint:** `POST /songs/batch`

### What It Does
Get multiple songs by their IDs in a single request.

### Query Parameters
- `song_ids` - Array of IDs (max 50)

### Example
```
POST /songs/batch?song_ids=1&song_ids=5&song_ids=10&song_ids=15
```

### Use Cases
- Build playlists
- Compare different versions
- Batch download
- Bookmarks/favorites system

### Frontend Example

```javascript
// Get user's favorite songs
async function loadFavorites(favoriteIds) {
  const params = favoriteIds.map(id => `song_ids=${id}`).join('&');
  const response = await fetch(`/songs/batch?${params}`);
  const songs = await response.json();
  
  return songs;
}

// Example usage
const favorites = await loadFavorites([1, 3, 7, 12, 15]);
```

---

## 🎵 6. Audio Streaming

**Endpoint:** `GET /stream/{song_id}`

### What It Does
Redirects to the direct download URL for streaming. Works with HTML5 audio players and supports seeking.

### Example
```
GET /stream/1
```

### Frontend Example

```html
<!-- HTML5 Audio Player -->
<audio id="player" controls>
  <source src="/stream/1" type="audio/mpeg">
</audio>

<script>
// JavaScript player controls
function playSong(songId) {
  const player = document.getElementById('player');
  player.src = `/stream/${songId}`;
  player.play();
}
</script>
```

### React Example

```jsx
function AudioPlayer({ songId }) {
  return (
    <audio controls>
      <source src={`/stream/${songId}`} type="audio/mpeg" />
      Your browser does not support audio playback.
    </audio>
  );
}
```

---

## 🏷️ 7. Tags System

### What Changed
Songs now support tags for better categorization and discovery.

### Available Tags
Common tags you can use:
- `hype` - High-energy, rage songs
- `sad` - Emotional, melancholic
- `melodic` - Melodic, singing
- `rage` - Rage/aggressive style
- `chill` - Laid-back vibes
- `party` - Party anthems
- `emotional` - Emotionally charged
- `freestyle` - Freestyle recordings

### Adding Tags (Admin)

```json
POST /songs/add
{
  "name": "Song Name",
  "era": "2093",
  "tags": ["hype", "rage", "melodic"]
}
```

### Searching by Tags

Tags are automatically searched in the search endpoint:

```
GET /search?q=hype
```

This will return songs with "hype" in the name OR in tags.

### Frontend Filter

```javascript
// Filter songs with specific tags
const songs = await fetch('/songs').then(r => r.json());
const hypeSongs = songs.songs.filter(song => 
  song.tags && song.tags.includes('hype')
);
```

---

## 📂 8. Enhanced Categories

### New Category System

Instead of just "released" vs "unreleased", V2 has detailed categories:

| Category | Description |
|----------|-------------|
| `released_album` | Official album releases |
| `released_single` | Official singles |
| `unreleased_grail` | High-demand unreleased (must-have) |
| `unreleased_throwaway` | Throwaway tracks |
| `snippet` | Short previews (< 1:30) |
| `demo` | Demo versions |
| `og_version` | Original versions (before mixing) |
| `alternate_version` | Alternative takes |
| `live_performance` | Live recordings |
| `freestyle` | Freestyle recordings |
| `reference` | Reference tracks |
| `session` | Studio session recordings |

### Using Categories

**Get all grails:**
```
GET /songs?category=unreleased_grail
```

**Get all snippets:**
```
GET /songs?category=snippet
```

**List available categories:**
```
GET /categories
```

Response:
```json
{
  "categories": [
    "released_album",
    "unreleased_grail",
    "snippet",
    ...
  ],
  "counts": {
    "unreleased_grail": 67,
    "snippet": 23,
    "released_album": 15
  }
}
```

---

## 🎤 9. Enhanced Metadata

### New Fields

Songs now include rich metadata:

```json
{
  "id": 1,
  "song_name": "Sample Song",
  
  // Multiple track titles
  "track_titles": ["Sample Song", "Alt Name 1", "Alt Name 2"],
  
  // Recording details
  "recording_locations": "Recording Academy, Los Angeles, CA",
  "record_dates": "Recorded June 15, 2023",
  "session_titles": "Sample_Session_Final.ptx",
  "session_tracking": "27 stem tracks, 44 vocal takes",
  "engineers": "Mike Dean, Alex Tumay",
  
  // Instrumental info
  "instrumental_names": "Sample_Instrumental_V2, Sample_Beat_Final",
  "instrumental_links": "https://pillows.su/f/inst123",
  
  // Multiple streaming links
  "youtube_link": "https://youtube.com/...",
  "soundcloud_link": "https://soundcloud.com/...",
  "spotify_link": "https://open.spotify.com/...",  // If released
  
  // Popularity metrics
  "play_count": 142,
  "download_count": 89
}
```

### Using Enhanced Metadata

**Show recording details:**
```javascript
function showRecordingInfo(song) {
  if (song.recording_locations) {
    console.log(`Recorded at: ${song.recording_locations}`);
  }
  if (song.engineers) {
    console.log(`Engineers: ${song.engineers}`);
  }
  if (song.session_tracking) {
    console.log(`Session: ${song.session_tracking}`);
  }
}
```

**Show all streaming options:**
```javascript
function getStreamingLinks(song) {
  const links = [];
  
  if (song.download_link) {
    links.push({ platform: 'Download', url: song.download_link });
  }
  if (song.youtube_link) {
    links.push({ platform: 'YouTube', url: song.youtube_link });
  }
  if (song.soundcloud_link) {
    links.push({ platform: 'SoundCloud', url: song.soundcloud_link });
  }
  if (song.spotify_link) {
    links.push({ platform: 'Spotify', url: song.spotify_link });
  }
  
  return links;
}
```

---

## 📈 10. Play Count Tracking

### Automatic Tracking
Every time someone calls `GET /songs/{id}`, the play count automatically increments.

### Use Cases
- Track most popular songs
- Build "Trending" sections
- Analytics dashboard
- Recommendation system

### Get Most Played Songs

```
GET /songs?sort_by=play_count&sort_order=desc&page_size=20
```

### Frontend Example

```javascript
// Trending songs section
async function loadTrending() {
  const response = await fetch(
    '/songs?sort_by=play_count&sort_order=desc&page_size=10'
  );
  const data = await response.json();
  
  return data.songs.map(song => ({
    ...song,
    trending: `${song.play_count} plays`
  }));
}
```

---

## 🔄 Migration Guide

### If You Have V1 Data

**Option 1: Add New Columns (Recommended)**

```sql
-- Add new columns to existing table
ALTER TABLE unreleased_songs 
  ADD COLUMN track_titles TEXT[],
  ADD COLUMN category VARCHAR(50),
  ADD COLUMN tags TEXT[],
  ADD COLUMN play_count INTEGER DEFAULT 0,
  -- ... (see schema.sql for all new fields)
```

**Option 2: Fresh Start**

1. Export existing data
2. Drop table
3. Run new `schema.sql`
4. Import data back

### Update Existing Songs

```python
# Add categories to existing songs
for song in existing_songs:
    category = 'unreleased_grail'  # Determine based on song
    tags = ['hype', 'rage']  # Add relevant tags
    
    requests.put(
        f'/songs/{song.id}',
        headers={'X-API-Key': API_KEY},
        json={
            'category': category,
            'tags': tags,
            # ... other existing fields
        }
    )
```

---

## 💡 Best Practices

### For Frontend Developers

1. **Use minimal endpoint for lists** - Saves bandwidth
2. **Use full endpoint for details** - Get all metadata
3. **Cache statistics** - They don't change often
4. **Use streaming for players** - Better UX
5. **Implement filters progressively** - Don't overwhelm users

### For API Performance

1. **Use pagination** - Don't fetch all songs at once
2. **Add indexes** - Already done in schema.sql
3. **Use batch operations** - Reduce request count
4. **Cache popular queries** - Statistics, featured songs

### For Data Quality

1. **Add tags consistently** - Use standard tag names
2. **Categorize properly** - Follow category definitions
3. **Fill metadata** - Recording details add value
4. **Update play counts** - Track popularity

---

## 🎯 What to Build Next

### Frontend Ideas
- Browse by era timeline
- Tag-based discovery
- Most played/trending section
- Random discovery button
- Featured playlist
- Search with autocomplete
- Filtering UI
- Audio player with queue

### Analytics Ideas
- Track listening patterns
- Most popular eras
- Quality distribution
- Tag analytics
- Growth over time

### Community Features
- User playlists
- Favorites/bookmarks
- Comments/reviews
- Voting system
- Share songs

---

## 🆘 Common Questions

**Q: Do I need to use all features?**
A: No! Start with what you need. Features are optional.

**Q: Can I add custom categories?**
A: Yes, just add them to the database. The API accepts any category.

**Q: How do play counts work?**
A: Auto-incremented when viewing a song. Can be manually set via admin endpoint.

**Q: Can I have multiple tags per song?**
A: Yes! Tags are an array - add as many as relevant.

**Q: What if I don't have all metadata?**
A: All enhanced fields are optional. Add what you have.

---

**Ready to build something awesome!** 🚀

Version 2.0.0 - Enhanced Edition
