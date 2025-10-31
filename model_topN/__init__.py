"""
model_topN Package
Contains recommendation models and functions for CineMate
"""

from .Recommended import (
    get_related_movies,
    get_recommendations_combined,
    get_top_n_recommendations,
    format_results_for_json
)

__all__ = [
    'get_related_movies',
    'get_recommendations_combined',
    'get_top_n_recommendations',
    'format_results_for_json'
]

__version__ = '1.0.0'
