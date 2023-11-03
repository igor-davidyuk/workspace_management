"""Filesystem Item Module."""
from pathlib import Path  # Only used in `add` method
import time
from typing import Optional
import yaml

class Item:
    def __init__(self, name: str) -> None:
        self.name = name
        self.initialization_time = time.asctime()

class File(Item):
    def __init__(self, name: str, size_b: int) -> None:
        super().__init__(name)
        self.size_b = size_b
        self.suffix = name.split('.')[-1]

class Folder(Item):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.children_dict = {}

    def add(
            self, path: str,
            name_override: Optional[str] = None,
            ignore_hidden: Optional[bool] = False
        ) -> None:
        """
        Add a file or a folder.

        Args:
            path (str): path pointing to the item being added
                        in the computer filesystem.
        """
        path = Path(path)
        if (
            len(path.name) > 1 and  # In case of '.' input path
            path.name.startswith('.') and
            ignore_hidden
        ):
            return
        item_name = name_override if name_override else path.absolute().name

        if path.is_file():
            self.children_dict[item_name] = File(path.name, size_b=path.stat().st_size)
        if path.is_dir():
            child_folder = self.__class__(path.name)
            for element in path.glob('*'):
                child_folder.add(str(element), ignore_hidden=ignore_hidden)
            self.children_dict[item_name] = child_folder

    def delete(self, path: str) -> bool:
        split_path = path.split('/')
        filename = split_path[-1]
        parent_folder = self

        # handle cases when path is provided in form `./foo/...` or `/foo/...`
        if split_path[0] == '' or split_path[0] == '.':
            starting_index = 1
        else:
            starting_index = 0
        # go down to the target parent
        for folder_name in split_path[starting_index:-1]:
            if folder_name in parent_folder.children_dict:
                parent_folder = parent_folder.children_dict[folder_name]
            else:
                return False
        # remove the target from the children list
        if filename in parent_folder.children_dict:
            del parent_folder.children_dict[filename]
            return True
        else:
            return False


    # def __repr__(self) -> str:
    #     representation = f'folder name: {self.name} \tupload time: {self.initialization_time}\n'
    #     representation += '================================================================'
    #     for item in self.children_dict:
    #         representation += 
    #     return representation

