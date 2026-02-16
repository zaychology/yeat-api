-- ============================================
-- YEAT API V2 - ENHANCED SUPABASE DATABASE SCHEMA
-- ============================================
-- Inspired by Juice WRLD API with expanded metadata
-- Run this in your Supabase SQL Editor

-- Drop table if exists (for clean reinstall)
-- DROP TABLE IF EXISTS unreleased_songs CASCADE;

-- Create the main songs table with enhanced fields
CREATE TABLE IF NOT EXISTS unreleased_songs (
    -- Primary key
    id BIGSERIAL PRIMARY KEY,
    
    -- ========================================
    -- BASIC INFORMATION
    -- ========================================
    era VARCHAR(100),
    name TEXT NOT NULL,  -- Raw text containing name, features, producers, alt names
    notes TEXT,
    
    -- ========================================
    -- ENHANCED METADATA (Juice WRLD inspired)
    -- ========================================
    
    -- Multiple track titles (some songs have different names)
    track_titles TEXT[],  -- Array: ["Main Name", "Alt Name 1", "Alt Name 2"]
    
    -- Expanded category system
    category VARCHAR(50),  -- released_album, released_single, unreleased_grail, snippet, demo, og_version, etc.
    
    -- Tags for better search and discovery
    tags TEXT[],  -- Array: ["hype", "melodic", "sad", "rage"]
    
    -- ========================================
    -- AUDIO INFORMATION
    -- ========================================
    track_length VARCHAR(20),
    type VARCHAR(50),  -- Throwaway, Demo, OG, Reference, etc.
    available_length VARCHAR(20),  -- Full, Partial, Snippet
    quality VARCHAR(50),  -- Lossless, CD Quality, 320kbps, 128kbps
    
    -- ========================================
    -- DATES
    -- ========================================
    file_date DATE,
    first_preview DATE,
    leak_date DATE,
    og_file_leak_date DATE,
    
    -- ========================================
    -- RECORDING DETAILS
    -- ========================================
    recording_locations TEXT,  -- "Studio Name, City, State"
    record_dates TEXT,  -- "Recorded January 15, 2023"
    session_titles TEXT,  -- Session file names
    session_tracking TEXT,  -- "27 stem tracks, 44 vocal takes"
    engineers TEXT,  -- Engineers who worked on the track
    
    -- ========================================
    -- INSTRUMENTAL DETAILS
    -- ========================================
    instrumental_names TEXT,  -- Names of instrumental versions
    instrumental_links TEXT,  -- Links to instrumental versions
    
    -- ========================================
    -- LINKS & DOWNLOADS
    -- ========================================
    links TEXT,  -- Primary Pillowcase.su link
    youtube_link TEXT,  -- YouTube link if available
    soundcloud_link TEXT,  -- SoundCloud link if available
    spotify_link TEXT,  -- Spotify link if officially released
    
    -- ========================================
    -- POPULARITY METRICS
    -- ========================================
    play_count INTEGER DEFAULT 0,
    download_count INTEGER DEFAULT 0,
    
    -- ========================================
    -- TIMESTAMPS
    -- ========================================
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- Index on era for filtering
CREATE INDEX IF NOT EXISTS idx_era ON unreleased_songs(era);

-- Index on category for filtering
CREATE INDEX IF NOT EXISTS idx_category ON unreleased_songs(category);

-- Index on quality for filtering
CREATE INDEX IF NOT EXISTS idx_quality ON unreleased_songs(quality);

-- Index on type for filtering
CREATE INDEX IF NOT EXISTS idx_type ON unreleased_songs(type);

-- Full-text search index on name
CREATE INDEX IF NOT EXISTS idx_name_search ON unreleased_songs USING gin(to_tsvector('english', name));

-- GIN index on tags array for fast tag searches
CREATE INDEX IF NOT EXISTS idx_tags ON unreleased_songs USING gin(tags);

-- Index on dates for sorting
CREATE INDEX IF NOT EXISTS idx_leak_date ON unreleased_songs(leak_date);
CREATE INDEX IF NOT EXISTS idx_created_at ON unreleased_songs(created_at);

-- Index on play_count for trending/popular queries
CREATE INDEX IF NOT EXISTS idx_play_count ON unreleased_songs(play_count DESC);

-- ============================================
-- TRIGGERS
-- ============================================

-- Function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to call the function before any UPDATE
DROP TRIGGER IF EXISTS update_unreleased_songs_updated_at ON unreleased_songs;
CREATE TRIGGER update_unreleased_songs_updated_at 
    BEFORE UPDATE ON unreleased_songs 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- SAMPLE DATA
-- ============================================

-- Insert enhanced sample songs for testing
INSERT INTO unreleased_songs (
    era, name, notes, track_length, type, available_length, quality,
    category, tags, track_titles,
    file_date, leak_date, links,
    recording_locations, record_dates, engineers
) VALUES 
(
    '2093',
    'Sample Song
(feat. Drake, Gunna) (prod. Bnyx, Starboy)
(Alt: Test Track, Demo Version)',
    'test_file_v2.mp3 - High quality lossless version',
    '2:45',
    'Throwaway',
    'Full',
    'Lossless',
    'unreleased_grail',
    ARRAY['hype', 'rage', 'melodic'],
    ARRAY['Sample Song', 'Test Track', 'Demo Version'],
    '2023-06-15',
    '2023-07-20',
    'https://pillows.su/f/abc123',
    'Recording Academy, Los Angeles, CA',
    'Recorded June 15, 2023',
    'Mike Dean, Alex Tumay'
),
(
    'Lyfë',
    'Another Test
(prod. Maaly Raw)',
    'test_snippet.mp3',
    '1:30',
    'Snippet',
    'Partial',
    'CD Quality',
    'snippet',
    ARRAY['sad', 'emotional'],
    ARRAY['Another Test', 'Untitled 2'],
    '2022-03-10',
    '2022-04-15',
    'https://pillows.su/f/def456',
    NULL,
    NULL,
    NULL
),
(
    'Up 2 Më',
    'Released Track Example
(feat. Young Thug) (prod. BNYX)',
    'official_release.mp3',
    '3:20',
    'Album Track',
    'Full',
    'Lossless',
    'released_album',
    ARRAY['hype', 'party'],
    ARRAY['Released Track Example'],
    '2021-09-10',
    NULL,
    'https://pillows.su/f/ghi789',
    'Capitol Studios, Hollywood, CA',
    'Recorded September 2021',
    'Leslie Brathwaite'
);

-- ============================================
-- VIEWS FOR COMMON QUERIES
-- ============================================

-- View for high-quality full-length songs
CREATE OR REPLACE VIEW high_quality_songs AS
SELECT * FROM unreleased_songs
WHERE quality IN ('Lossless', 'CD Quality')
AND available_length = 'Full'
AND links IS NOT NULL
ORDER BY created_at DESC;

-- View for songs by category counts
CREATE OR REPLACE VIEW category_stats AS
SELECT 
    category,
    COUNT(*) as song_count,
    COUNT(CASE WHEN quality = 'Lossless' THEN 1 END) as lossless_count,
    COUNT(CASE WHEN available_length = 'Full' THEN 1 END) as full_length_count
FROM unreleased_songs
GROUP BY category
ORDER BY song_count DESC;

-- View for era statistics
CREATE OR REPLACE VIEW era_stats AS
SELECT 
    era,
    COUNT(*) as song_count,
    COUNT(CASE WHEN links IS NOT NULL THEN 1 END) as songs_with_downloads
FROM unreleased_songs
GROUP BY era
ORDER BY song_count DESC;

-- ============================================
-- UTILITY FUNCTIONS
-- ============================================

-- Function to get random song with optional filters
CREATE OR REPLACE FUNCTION get_random_song(
    p_era VARCHAR DEFAULT NULL,
    p_category VARCHAR DEFAULT NULL,
    p_quality VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    id BIGINT,
    name TEXT,
    era VARCHAR,
    category VARCHAR,
    quality VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.id,
        s.name,
        s.era,
        s.category,
        s.quality
    FROM unreleased_songs s
    WHERE (p_era IS NULL OR s.era = p_era)
    AND (p_category IS NULL OR s.category = p_category)
    AND (p_quality IS NULL OR s.quality = p_quality)
    ORDER BY RANDOM()
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- VERIFY INSTALLATION
-- ============================================

-- Check that table was created successfully
SELECT 
    'unreleased_songs table created!' as status,
    COUNT(*) as sample_songs
FROM unreleased_songs;

-- Display sample data
SELECT 
    id,
    LEFT(name, 50) as name_preview,
    era,
    category,
    array_length(tags, 1) as tag_count,
    quality,
    created_at
FROM unreleased_songs
ORDER BY created_at DESC;

-- Display statistics views
SELECT * FROM era_stats;
SELECT * FROM category_stats;
