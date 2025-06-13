import os
import json
from typing import Any, Dict

def load_json(file_path: str) -> Dict[str, Any]:
    """
    Load a JSON file and return its contents as a dictionary.
    
    Args:
        file_path (str): The path to the JSON file
    
    Returns:
        Dict[str, Any]: The contents of the JSON file as a dictionary
    """
    if not os.path.exists(file_path):
        return {}
    
    with open(file_path, 'r') as file:
        return json.load(file)

def save_json(file_path: str, data: Dict[str, Any]):
    """
    Save a dictionary as a JSON file.
    
    Args:
        file_path (str): The path where to save the JSON file
        data (Dict[str, Any]): The dictionary to save
    """
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def ensure_dir(directory: str):
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory (str): The path to the directory
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_file_extension(file_path: str) -> str:
    """
    Get the file extension from a file path.
    
    Args:
        file_path (str): The path to the file
    
    Returns:
        str: The file extension (without the dot)
    """
    return os.path.splitext(file_path)[1][1:]

def is_valid_file(file_path: str, allowed_extensions: list) -> bool:
    """
    Check if a file has a valid extension.
    
    Args:
        file_path (str): The path to the file
        allowed_extensions (list): List of allowed file extensions
    
    Returns:
        bool: True if the file has a valid extension, False otherwise
    """
    return get_file_extension(file_path).lower() in [ext.lower() for ext in allowed_extensions]

def truncate_string(string: str, max_length: int) -> str:
    """
    Truncate a string to a maximum length, adding an ellipsis if truncated.
    
    Args:
        string (str): The string to truncate
        max_length (int): The maximum length of the string
    
    Returns:
        str: The truncated string
    """
    return (string[:max_length-3] + '...') if len(string) > max_length else string