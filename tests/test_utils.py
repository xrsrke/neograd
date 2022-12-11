from pathlib import Path, PosixPath

from neograd.utils import append_path_to_filename, get_supported_image_types

# def get_files(path, extensions=None, recurse=False, include=None):
#     path = Path(path)
#     extensions = setify(extensions)
#     extensions = {e.lower() for e in extensions}
#     if recurse:
#         res = []
#         for i,(p,d,f) in enumerate(os.walk(path)): # returns (dirpath, dirnames, filenames)
#             if include is not None and i==0: d[:] = [o for o in d if o in include]
#             else:                            d[:] = [o for o in d if not o.startswith('.')]
#             res += _get_files(p, f, extensions)
#         return res
#     else:
#         f = [o.name for o in os.scandir(path) if o.is_file()]
#         return _get_files(path, f, extensions)


def test_get_supported_image_types():
    output = get_supported_image_types()
    expected = {'.png', '.xwd', '.ppm', '.jpe', '.tiff', '.ico', '.ief', '.pbm', '.jpeg', '.pgm', '.xbm', '.ras', '.bmp', '.jpg', '.gif', '.tif', '.xpm', '.pnm', '.svg', '.rgb'}
    assert output == expected


def test_append_path_to_filename():
    path = Path("./examples")
    file_names = ["h1.txt", "h2.txt"]
    
    output = append_path_to_filename(path, file_names)
    expected = [PosixPath('examples/h1.txt'), PosixPath('examples/h2.txt')]
    assert output == expected