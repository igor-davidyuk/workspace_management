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
            ignore_hidden and
            path.name.startswith('.') and
            len(path.name) > 1  # In case of '.' input path
        ):
            return
        # Find out the item name
        item_name = name_override if name_override else path.name
        if not item_name:  # In case of '.' input path
            item_name = '.'

        if path.is_file():
            self.children_dict[item_name] = File(path.name, size_b=path.stat().st_size)
        if path.is_dir():
            child_folder = self.__class__(path.name)
            for element in path.glob('*'):
                child_folder.add(str(element), ignore_hidden=ignore_hidden)
            self.children_dict[item_name] = child_folder

    def _remove_item(self, name_chain: list[str], chain_index: int) -> bool:
        if name_chain[chain_index] in self.children_dict:
            if len(name_chain) - 1 == chain_index:
                del self.children_dict[name_chain[-1]]
                return True
            else:
                return self.children_dict[name_chain[chain_index]]._remove_item(name_chain, chain_index + 1)
        else:
            return False

    def delete(self, path: str) -> bool:
        name_chain = path.split('/')

        # handle cases when path is provided in form `./foo/...` or `/foo/...`
        if name_chain[0] == '' or name_chain[0] == '.':
            starting_index = 1
        else:
            starting_index = 0
        # go down recursively to the target's parent
        return self._remove_item(name_chain, starting_index)


    # def __repr__(self) -> str:
    #     representation = f'folder name: {self.name} \tupload time: {self.initialization_time}\n'
    #     representation += '================================================================'
    #     for item in self.children_dict:
    #         representation += 
    #     return representation

