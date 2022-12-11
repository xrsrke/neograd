from pathlib import Path
from typing import Union, List, TypeVar

from neograd.utils import get_image_files


Item = TypeVar("Item")

class ListContainer:
    """A generic iterable container"""
    def __init__(self, items: List[Item]):
        self.items: List[Item] = items
    
    def __getitem__(self, idxs: Union[int, slice, List[int], List[bool]]) -> Union[Item, List[Item]]:
        """_summary_

        Args:
            idxs (Union[int, slice, List[int], List[bool]]): _description_

        Returns:
            List[Item]: _description_
        """
        if isinstance(idxs, (int, slice)):
            return self.items[idxs]
        elif isinstance(idxs[0], bool):
            return [item for item, idx in zip(self.items, idxs) if idx is True]
        elif isinstance(idxs[0], int):
            return [item for item, idx in zip(self.items, idxs) if item == self.items[idx]]
    
    def __len__(self) -> int:
        return len(self.items)


class ItemList(ListContainer):
    """A generic iterable list"""
    pass


class ImageList(ItemList):
    """A generic iterable image list"""
    
    @classmethod
    def from_files(cls, path: Union[str, Path]) -> ListContainer:
        """Load the list of images from a given path

        Args:
            path (Union[str, Path]): path

        Returns:
            ListContainer: A iterable list of images
        """
        image_files = get_image_files(path)
        return image_files


ImageList.from_files('/Users/study/Downloads')