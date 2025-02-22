import os
import pickle
import json
from functools import wraps


def cache_response_forever_in_fs(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        os.makedirs(".cached_responses", exist_ok=True)
        
        cache_key = json.dumps((args, sorted(kwargs.items())), sort_keys=True)
        
        cached_response_map = {}
        cache_file_path = f".cached_responses/{func.__name__}.pkl"
        
        if os.path.exists(cache_file_path):
            with open(cache_file_path, 'rb') as f:
                cached_response_map = pickle.load(f)
            
            if cache_key in cached_response_map:
                return cached_response_map[cache_key]
        
        response = func(*args, **kwargs)
        cached_response_map[cache_key] = response
        
        with open(cache_file_path, 'wb') as f:
            pickle.dump(cached_response_map, f)
        
        return response
    return wrapper

