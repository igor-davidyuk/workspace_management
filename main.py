import cmd
from tabulate import tabulate
import time
from source import Folder

MAIN_FOLDER = Folder('/')


class MyCommandPrompt(cmd.Cmd):
    """A simple command prompt application for workspace management."""

    intro = "Welcome to my command prompt! Type `help` for a list of commands."
    prompt = "> "

    def do_add(self, path):
        """Add an item."""
        MAIN_FOLDER.add(path, ignore_hidden=True)
        print('The item is loaded to the root directory.')

    def do_view(self, path: str):
        """View items."""
        if not path:
            item_list = []
            for item in MAIN_FOLDER.children_dict.values():
                item_list += [(item.name, time.asctime(item.initialization_time)),]
            print(tabulate(item_list, headers=['Item Name', 'Upload Time'], tablefmt='orgtbl'), '\n')
        else:
            # Find the Item step by step
            name_chain = path.split('/')

            # handle cases when path is provided in form `./foo/...` or `/foo/...`
            if name_chain[0] == '' or name_chain[0] == '.':
                starting_index = 1
            else:
                starting_index = 0

            element = MAIN_FOLDER._get_item(name_chain, starting_index)
            print(element)

    def do_filter(self, command: str):
        """Filter workspace contents."""
        split_command = command.split()
        path = split_command[0]
        option, descriptor = split_command[1:3]
        # Find the root folder
        name_chain = path.split('/')

        # handle cases when path is provided in form `./foo/...` or `/foo/...`
        if name_chain[0] == '' or name_chain[0] == '.':
            starting_index = 1
        else:
            starting_index = 0

        root_folder = MAIN_FOLDER._get_item(name_chain, starting_index)
        print(root_folder.filter(descriptor))
    
    def do_delete(self, path: str):
        """Delete an item."""
        is_done = MAIN_FOLDER.delete(path)
        if is_done:
            print("File removed!")
        else:
            print("File not found!")
    
    def do_exit(self, _):
        """Exit from the application"""
        print("Goodbye!")
        return True

    def do_help(self, _):
        """Print a list of commands."""
        print("Available commands:")
        print(" - add: Add a folder, accepts path pointing to somewhere in your filesystem.")
        print(" - delete: Delete an item in the Workspace.")
        print(" - help: Print this help message.")
        print(" - view: View an item.")
        print(" - filter: filter folder contents. The only working option is `--name name_part_without_special_caracters`")
        print(" - exit: Exit.")



if __name__ == "__main__":
    MyCommandPrompt().cmdloop()