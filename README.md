# WORKSPACE MANAGEMENT APPLICATION

This repository contains a command-line workspace management application. 

The base entity is the `Item` class and its two subclasses: `File` and `Folder`. The latter contains a hash table with all its children, this turned the workspace structure into a tree, giving quick `add`, `delete`, and `get` item operations - the complexity of those does not scale with the number of Items in the workspace.
`Filter` and `view` operations invoke iteration over all the elements in the workspace and have the complexity of O(n) which is the minimal possible.

## Requirements:
- python3.10

## How to Run:
- create and activate a virtual environment
- do `pip install -r requirements.txt`
- run `python main.py`

## Supported Operations
- add ...(path in your real filesystem)
- delete ...(path in workspace filesystem)
- view ...(path in workspace filesystem)
- filter ...(path in workspace filesystem) --name ...(part of the name without special caracters)
