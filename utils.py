"""
Enhanced utility functions for Yeat API V2.
Includes expanded parsing and formatting for Juice WRLD-inspired features.
"""
import re
from typing import Dict, Optional, List, Any


def parse_song_name(raw_name: str) -> Dict[str, Any]:
    """
    Parse the raw song name field into structured data with enhanced fields.
    
    Expected format:
    '''
    [Main Artist - ]Song Name
    (feat. Artist1, Artist2) (prod. Producer1, Producer2)
    (Alt Name 1, Alt Name 2)
    '''
    
    Args:
        raw_name: The raw name string from the database
        
    Returns:
        Dictionary with parsed fields: main_artist, song_name, features, 
        producers, alt_names, track_titles (all possible names)
        
    Example:
        Input: "Lil Uzi Vert - Crazy\\n(feat. Yeat) (prod. Bnyx)\\n(Insane, Wild)"
        Output: {
            "main_artist": "Lil Uzi Vert",
            "song_name": "Crazy",
            "features": ["Yeat"],
            "producers": ["Bnyx"],
            "alt_names": ["Insane", "Wild"],
            "track_titles": ["Crazy", "Insane", "Wild"]
        }
    """
    # Initialize result dictionary
    result = {
        "main_artist": "Yeat",  # Default to Yeat
        "song_name": "",
        "features": [],
        "producers": [],
        "alt_names": [],
        "track_titles": []  # All possible names for the song
    }
    
    # Split by newlines and clean up
    lines = [line.strip() for line in raw_name.split('\n') if line.strip()]
    
    if not lines:
        return result
    
    # Parse first line: Main Artist - Song Name OR just Song Name
    first_line = lines[0]
    if ' - ' in first_line:
        parts = first_line.split(' - ', 1)
        result["main_artist"] = parts[0].strip()
        result["song_name"] = parts[1].strip()
    else:
        result["song_name"] = first_line.strip()
    
    # Add main song name to track_titles
    if result["song_name"]:
        result["track_titles"].append(result["song_name"])
    
    # Parse remaining lines for features, producers, and alt names
    for i in range(1, len(lines)):
        line = lines[i]
        
        # Extract features: (feat. Artist1, Artist2)
        feat_match = re.search(r'\(feat\.\s*([^)]+)\)', line, re.IGNORECASE)
        if feat_match:
            features_str = feat_match.group(1)
            result["features"] = [f.strip() for f in features_str.split(',')]
        
        # Extract producers: (prod. Producer1, Producer2)
        prod_match = re.search(r'\(prod\.\s*([^)]+)\)', line, re.IGNORECASE)
        if prod_match:
            producers_str = prod_match.group(1)
            result["producers"] = [p.strip() for p in producers_str.split(',')]
        
        # Check if this line is alt names (parentheses without feat. or prod.)
        # Remove feat. and prod. matches first
        cleaned_line = re.sub(r'\(feat\.\s*[^)]+\)', '', line, flags=re.IGNORECASE)
        cleaned_line = re.sub(r'\(prod\.\s*[^)]+\)', '', cleaned_line, flags=re.IGNORECASE)
        
        # Find remaining parentheses content as alt names
        alt_match = re.search(r'\(([^)]+)\)', cleaned_line)
        if alt_match:
            alt_names_str = alt_match.group(1)
            # Check if it starts with "Alt:" prefix
            if alt_names_str.lower().startswith('alt:'):
                alt_names_str = alt_names_str[4:].strip()
            result["alt_names"] = [a.strip() for a in alt_names_str.split(',')]
            # Add alt names to track_titles
            result["track_titles"].extend(result["alt_names"])
    
    return result


def convert_pillowcase_link(pillowcase_url: Optional[str]) -> Optional[str]:
    """
    Convert a Pillowcase.su file link to the direct download API link.
    
    Args:
        pillowcase_url: URL in format https://pillows.su/f/[id]
        
    Returns:
        Direct download URL: https://api.pillows.su/api/download/[id]
        Returns None if input is None or invalid
        
    Example:
        Input: "https://pillows.su/f/abc123"
        Output: "https://api.pillows.su/api/download/abc123"
    """
    if not pillowcase_url:
        return None
    
    # Extract the file ID using regex
    match = re.search(r'pillows\.su/f/([a-zA-Z0-9_-]+)', pillowcase_url)
    
    if match:
        file_id = match.group(1)
        return f"https://api.pillows.su/api/download/{file_id}"
    
    # If no match found, return original URL
    return pillowcase_url


def format_song_response(song_data: Dict, include_full_details: bool = True) -> Dict:
    """
    Format a song from the database into a complete API response with parsed fields.
    
    Args:
        song_data: Raw song dictionary from database
        include_full_details: If False, return minimal info for list views
        
    Returns:
        Formatted dictionary with all parsed fields
    """
    # Parse the name field
    parsed_name = parse_song_name(song_data.get('name', ''))
    
    # Convert the download link
    download_link = convert_pillowcase_link(song_data.get('links'))
    
    # Build basic response (always included)
    response = {
        "id": song_data.get('id'),
        "song_name": parsed_name['song_name'],
        "main_artist": parsed_name['main_artist'],
        "era": song_data.get('era'),
        "category": song_data.get('category'),
        "quality": song_data.get('quality'),
        "available_length": song_data.get('available_length'),
        "track_length": song_data.get('track_length'),
    }
    
    # Add full details if requested (for single song views)
    if include_full_details:
        response.update({
            # Parsed name fields
            "features": parsed_name['features'],
            "producers": parsed_name['producers'],
            "alt_names": parsed_name['alt_names'],
            "track_titles": song_data.get('track_titles') or parsed_name['track_titles'],
            
            # Original raw name (kept for reference)
            "raw_name": song_data.get('name'),
            
            # Track info
            "type": song_data.get('type'),
            "tags": song_data.get('tags') or [],
            
            # Dates (convert to ISO format string if present)
            "file_date": str(song_data.get('file_date')) if song_data.get('file_date') else None,
            "first_preview": str(song_data.get('first_preview')) if song_data.get('first_preview') else None,
            "leak_date": str(song_data.get('leak_date')) if song_data.get('leak_date') else None,
            "og_file_leak_date": str(song_data.get('og_file_leak_date')) if song_data.get('og_file_leak_date') else None,
            
            # Recording details
            "recording_locations": song_data.get('recording_locations'),
            "record_dates": song_data.get('record_dates'),
            "session_titles": song_data.get('session_titles'),
            "session_tracking": song_data.get('session_tracking'),
            "engineers": song_data.get('engineers'),
            
            # Instrumental details
            "instrumental_names": song_data.get('instrumental_names'),
            "instrumental_links": song_data.get('instrumental_links'),
            
            # Links
            "pillowcase_link": song_data.get('links'),
            "download_link": download_link,
            "youtube_link": song_data.get('youtube_link'),
            "soundcloud_link": song_data.get('soundcloud_link'),
            "spotify_link": song_data.get('spotify_link'),
            
            # Popularity
            "play_count": song_data.get('play_count', 0),
            "download_count": song_data.get('download_count', 0),
            
            # Notes
            "notes": song_data.get('notes'),
            
            # Timestamps
            "created_at": str(song_data.get('created_at')) if song_data.get('created_at') else None,
            "updated_at": str(song_data.get('updated_at')) if song_data.get('updated_at') else None,
        })
    
    return response


def search_in_song(song_data: Dict, query: str) -> bool:
    """
    Check if a search query matches a song across multiple fields.
    
    Args:
        song_data: Song dictionary
        query: Search query string
        
    Returns:
        True if the song matches the query
    """
    query_lower = query.lower()
    
    # Parse the name to search in all fields
    parsed = parse_song_name(song_data.get('name', ''))
    
    # Check in various fields
    search_fields = [
        song_data.get('name', ''),
        parsed['song_name'],
        ' '.join(parsed['alt_names']),
        ' '.join(parsed['producers']),
        ' '.join(parsed['features']),
        ' '.join(song_data.get('tags') or []),
        ' '.join(song_data.get('track_titles') or []),
        song_data.get('notes', ''),
        song_data.get('era', ''),
    ]
    
    # Check if query matches in any field
    return any(query_lower in str(field).lower() for field in search_fields if field)


def extract_tags_from_name(name: str) -> List[str]:
    """
    Automatically extract potential tags from song name.
    This is a helper for data migration/enhancement.
    
    Args:
        name: Song name
        
    Returns:
        List of suggested tags
    """
    tags = []
    name_lower = name.lower()
    
    # Mood tags
    if any(word in name_lower for word in ['sad', 'cry', 'pain', 'hurt', 'die']):
        tags.append('sad')
    if any(word in name_lower for word in ['hype', 'crazy', 'turnt', 'lit', 'rage']):
        tags.append('hype')
    if any(word in name_lower for word in ['love', 'heart', 'feel']):
        tags.append('emotional')
    
    # Style tags
    if 'freestyle' in name_lower:
        tags.append('freestyle')
    if any(word in name_lower for word in ['snippet', 'preview']):
        tags.append('snippet')
    
    return list(set(tags))  # Remove duplicates


def validate_category(category: Optional[str]) -> bool:
    """
    Validate that a category is one of the allowed values.
    
    Args:
        category: Category string to validate
        
    Returns:
        True if valid, False otherwise
    """
    valid_categories = [
        'released_album',
        'released_single',
        'unreleased_grail',
        'unreleased_throwaway',
        'snippet',
        'demo',
        'og_version',
        'alternate_version',
        'live_performance',
        'freestyle',
        'reference',
        'session',
    ]
    
    return category is None or category in valid_categories


def get_quality_rank(quality: Optional[str]) -> int:
    """
    Get numeric rank for quality (higher is better).
    Used for sorting by quality.
    
    Args:
        quality: Quality string
        
    Returns:
        Numeric rank (0-5)
    """
    quality_ranks = {
        'Lossless': 5,
        'CD Quality': 4,
        '320kbps': 3,
        '256kbps': 2,
        '128kbps': 1,
    }
    
    return quality_ranks.get(quality, 0)


def format_minimal_song(song_data: Dict) -> Dict:
    """
    Format song with minimal information for list views.
    Optimizes response size for paginated endpoints.
    
    Args:
        song_data: Raw song dictionary
        
    Returns:
        Minimal song info dictionary
    """
    parsed_name = parse_song_name(song_data.get('name', ''))
    
    return {
        "id": song_data.get('id'),
        "song_name": parsed_name['song_name'],
        "main_artist": parsed_name['main_artist'],
        "features": parsed_name['features'],
        "era": song_data.get('era'),
        "category": song_data.get('category'),
        "quality": song_data.get('quality'),
        "track_length": song_data.get('track_length'),
        "has_download": bool(song_data.get('links')),
        "tags": song_data.get('tags') or [],
    }
