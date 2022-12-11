import os
import mimetypes
from pathlib import Path
from typing import Iterable, List, Set, Union


def append_path_to_filename(path: Union[str, Path], file_names: List[str], extensions=None) -> List[Path]:
    """Append a path to the list of file names

    Args:
        path (Union[str, Path]): path
        file_names (List[str]): files' name
        extensions (_type_, optional): limits to certain file extensions

    Returns:
        List[Path]: a list of files's path
    """
    path = Path(path)
    res = [path/name for name in file_names if not name.startswith('.')
           and ((not extensions) or f'.{name.split(".")[-1].lower()}' in extensions)]
    return res


def get_supported_image_types() -> Set[str]:
    """Get a list of supported image types

    Returns:
        Set[str]: A list of supported image types
    """
    return set(k for k, v in mimetypes.types_map.items() if v.startswith('image/'))


def get_image_files(path: Union[Path, str]) -> List[Path]:
    """Get all the images in the given path

    Args:
        path (Union[Path, str]): path to get all the images

    Returns:
        List[Path]: A list of all the images's path
    """
    path = Path(path)
    images: List[Path] = []
    extensions = get_supported_image_types()

    for file_name in os.listdir(path):
        extension = f".{file_name.split('.')[-1].lower()}"
        if extension in extensions:
            images.append(file_name) 
    
    image_paths = append_path_to_filename(path, images)
    return image_paths