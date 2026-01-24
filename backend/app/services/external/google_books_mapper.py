from typing import Any, Dict, Optional

def google_json_to_book(data: Dict[str, Any]) -> Dict[str, Any]:
    volume = data.get('volumeInfo', {})
    image_links = volume.get('imageLinks', {})
    industry_ids = volume.get('industryIdentifiers', [])
    isbn_10 = None
    isbn_13 = None
    for id_obj in industry_ids:
        if id_obj.get('type') == 'ISBN_10':
            isbn_10 = id_obj.get('identifier')
        if id_obj.get('type') == 'ISBN_13':
            isbn_13 = id_obj.get('identifier')
    return {
        'google_books_id': data.get('id'),
        'title': volume.get('title'),
        'authors': volume.get('authors', []),
        'publisher': volume.get('publisher'),
        'published_date': volume.get('publishedDate'),
        'description': volume.get('description'),
        'isbn_10': isbn_10,
        'isbn_13': isbn_13,
        'page_count': volume.get('pageCount'),
        'categories': volume.get('categories', []),
        'language': volume.get('language'),
        'image_url': image_links.get('thumbnail'),
        'preview_link': volume.get('previewLink'),
    }