"""Filesystem Item Module."""
import logging
import math
import re
from pathlib import Path  # Only used in `add` method
import time
from typing import Dict, List, Optional, Tuple
import yaml

def _load_type_mapping_config(path: str) -> Dict[str, str]:
    with open(path, 'r') as reader:
        type_mapping = yaml.safe_load(reader)
    return type_mapping

TYPE_MAPPING = _load_type_mapping_config('config/filetype_mapping.yaml')
INDENT_SYMBOL = '  '
FILESIZE_LITERALS = ['B', 'kB', 'MB', 'GB', 'TB']

class Item:
    """The base Item class."""
    def __init__(self, name: str) -> None:
        self.name = name
        self.size_b = 0
        self.initialization_time = time.localtime()

class File(Item):
    """File class."""
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
    """Folder class."""
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.children_dict: Dict[str, self.__class__] = {}

    def add(
            self, path: str,
            name_override: Optional[str] = None,
            ignore_hidden: Optional[bool] = False
        ) -> None:
        """
        Add an item to the folder

        Args:
            path (str): path to real filesystem item
            name_override (Optional[str], optional): give the item a new name. Defaults to None.
            ignore_hidden (Optional[bool], optional): ignore hidden files. Defaults to False.
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
            item_name = path.absolute().name

        if path.is_file():
            self.children_dict[item_name] = File(path.name, size_b=path.stat().st_size)
        if path.is_dir():
            child_folder = self.__class__(item_name)
            for element in path.glob('*'):
                child_folder.add(str(element), ignore_hidden=ignore_hidden)
            self.children_dict[item_name] = child_folder

    def _get_item(self, name_chain: list[str], chain_index: int) -> Optional[Item]:
        """
        Get item method.

        Args:
            name_chain (list[str]): list of names leading to the item
            chain_index (int): current target index

        Returns:
            Optional[Item]: Item if found, else None
        """
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
        
    @staticmethod
    def _get_sorting_function(type='alphabetical'):
        alphabetical = lambda item: item.name
        by_time = lambda item: item.initialization_time
        by_size = lambda item: item.size_b
        return by_size

    def traverse(self, depth: int = 0, path_to_dir: str = '') -> List[Tuple[Item, int, str]]:
        result = []
        for item in self.children_dict.values():
            if type(item) == File:
                result.append((item, depth, path_to_dir))
            else:  # Folder
                result.append((item, depth, path_to_dir))
                result.extend(item.traverse(depth=depth+1, path_to_dir=path_to_dir + f'/{item.name}'))
        return result
    
    def __repr__(self) -> str:
        item_list = self.traverse()
        result = ''
        for item, depth, path_to_dir in item_list:
            file_representation = ('|- ' + str(item)) if type(item) == File else ('┎ ' + item.name)
            result += INDENT_SYMBOL * depth + file_representation + '\n'
        return result
    
    def filter(self, pattern: str = '', filetype: str = '', min_size: int = 0) -> str:
        item_list = self.traverse()
        filtered_list = []
        def combined_filter(item, pattern, filetype, min_size) -> bool:
            # print(pattern, item.name, pattern in item.name)
            match = False
            if pattern:
                if pattern in item.name:
                    match = True
                else:
                    match = False
            if filetype:
                if filetype == item.type:
                    match = True
                else:
                    match = False
            if min_size:
                if min_size <= item.size_b:
                    match = True
                else:
                    match = False
            return match

        used_folders = set()
        for item, depth, path_to_dir in item_list:
            if type(item) == File:
                if combined_filter(item, pattern, filetype, min_size):
                    filtered_list.append((item, depth, path_to_dir))
                    used_folders = used_folders.union(set(path_to_dir.split('/')))
            else:
                filtered_list.append((item, depth, path_to_dir))

        # Represent as text
        
        result = ''
        for item, depth, path_to_dir in filtered_list:
            if type(item) == Folder and item.name not in used_folders:
                continue
            file_representation = ('|- ' + str(item)) if type(item) == File else ('┎ ' + item.name)
            result += INDENT_SYMBOL * depth + file_representation + '\n'
        return result 
