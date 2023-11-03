"""Filesystem Item Module."""
import logging
import math
from pathlib import Path  # Only used in `add` method
import time
from typing import Dict, Optional
import yaml

def _load_type_mapping_config(path: str) -> Dict[str, str]:
    with open(path, 'r') as reader:
        type_mapping = yaml.safe_load(reader)
    return type_mapping

TYPE_MAPPING = _load_type_mapping_config('config/filetype_mapping.yaml')
INDENT_SYMBOL = '  '
FILESIZE_LITERALS = ['B', 'kB', 'MB', 'GB', 'TB']

class Item:
    def __init__(self, name: str) -> None:
        self.name = name
        self.initialization_time = time.asctime()

    # def view(self):
    #     raise NotImplementedError()

class File(Item):
    def __init__(self, name: str, size_b: int) -> None:
        super().__init__(name)
        self.size_b = size_b
        # Convert size to a readable format
        exponent = math.floor(math.log(size_b) / math.log(1024)) if size_b else 0
        self.readable_size = str(int(size_b / 1024**exponent)) + f'{FILESIZE_LITERALS[exponent]}'
        # Determine data type
        self.suffix = name.split('.')[-1]
        if self.suffix not in TYPE_MAPPING:
            # logging.warning(f'Unexpected file extantion {self.suffix}, please update the config')
            self.type = 'file'
        else:
            self.type = TYPE_MAPPING[self.suffix]

    def __repr__(self) -> str:
        return f'{self.name}  ({self.readable_size}, {self.type})'

    def view(self, indent: int = 0) -> str:
        return self.indent_symbol * indent + f''

class Folder(Item):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.children_dict: Dict[str, self.__class__] = {}

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

    def _get_item(self, name_chain: list[str], chain_index: int) -> Optional[Item]:
        if name_chain[chain_index] in self.children_dict:
            if len(name_chain) - 1 == chain_index:
                return self.children_dict[name_chain[-1]]
            else:
                return self.children_dict[name_chain[chain_index]]._get_item(name_chain, chain_index + 1)
        else:
            return None

    def delete(self, path: str) -> bool:
        name_chain = path.split('/')
        filename = name_chain[-1]

        # handle cases when path is provided in form `./foo/...` or `/foo/...`
        if name_chain[0] == '' or name_chain[0] == '.':
            starting_index = 1
        else:
            starting_index = 0

        if len(name_chain) - starting_index == 1:
            parent = self
        else:
            # go down recursively to the target's parent
            parent = self._get_item(name_chain[:-1], starting_index)
        # If the parent is found and it contains the file we remove it
        if parent and filename in parent.children_dict:
            del parent.children_dict[filename]
            return True
        else:
            logging.warning('File not found')
            return False



    # def __repr__(self) -> str:
    #     representation = f'folder name: {self.name} \tupload time: {self.initialization_time}\n'
    #     representation += '================================================================'
    #     for item in self.children_dict:
    #         representation += 
    #     return representation

