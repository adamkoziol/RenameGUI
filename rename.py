#!/usr/bin/env python3
from gooey import Gooey, GooeyParser
from glob import glob
import shutil
import os

image_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'images')
__author__ = 'adamkoziol'


class Renamer(object):

    def main(self):
        self.parse_input()
        self.find_files()
        self.rename_files()

    def parse_input(self):
        # Create sets to store duplicate names
        duplicate_old = set()
        duplicate_new = set()
        with open(self.rename_file, 'r') as rename:
            for line in rename:
                try:
                    old, new = line.rstrip().split('\t')
                    if old not in self.old_names and new not in self.new_names:
                        self.rename_dict[old] = new
                    if old not in self.old_names:
                        self.old_names.append(old)
                    else:
                        duplicate_old.add(old)
                    if new not in self.new_names:
                        self.new_names.append(new)
                    else:
                        duplicate_new.add(new)
                except ValueError:
                    print('Incorrect format detected. The .tsv file must only be two columns: original name and new '
                          'name')
                    quit()
        if duplicate_old:
            if len(duplicate_old) == 1:
                print('Duplicate entry found in the existing name column: {dup}'
                      .format(dup=', '.join(sorted(list(duplicate_old)))), flush=True)
            else:
                print('Duplicate entries found in the existing name column: {dup}'
                      .format(dup=', '.join(sorted(list(duplicate_old)))), flush=True)
        if duplicate_new:
            if len(duplicate_new) == 1:
                print('Duplicate entry found in the new name column: {dup}'
                      .format(dup=', '.join(sorted(list(duplicate_new)))), flush=True)
            else:
                print('Duplicate entries found in the new name column: {dup}'
                      .format(dup=', '.join(sorted(list(duplicate_new)))), flush=True)
        if duplicate_old or duplicate_new:
            print('Please fix your input sheet')
            quit()

    def find_files(self):
        """
        Find all the files in the supplied file path, and create a dictionary of file_name: file_extension
        """
        # Glob all the files in the path
        self.old_files = glob(os.path.join(self.file_path, '*'))
        for file_path in self.old_files:
            # Extract the file name, and extension with os.path.basename (to get file name and extension), then
            # split the extension
            file_name, file_ext = os.path.splitext(os.path.basename(file_path))
            # Populate the dictionary
            self.file_dict[file_name] = file_ext

    def rename_files(self):
        """
        Use the created dictionaries to rename the files. Also move the original files to a new folder. Print a
        message listing missing files
        """
        missing_files = set()
        for file_name in self.rename_dict:
            try:
                # Extract the file extension corresponding to the file name
                extension = self.file_dict[file_name]
                # Set variables for the current file name, as well as the renamed file, and the migrated original file
                source_file = os.path.join(self.file_path, '{name}{ext}'.format(name=file_name, ext=extension))
                renamed_file = os.path.join(self.rename_path, '{name}{ext}'
                                            .format(name=self.rename_dict[file_name],
                                                    ext=extension))
                original_file = os.path.join(self.original_path, '{name}{ext}'.format(name=file_name, ext=extension))
                # Try to rename the file
                try:
                    shutil.copyfile(src=source_file,
                                    dst=renamed_file)
                except FileExistsError:
                    pass
                # Try to move the original file to a sub-folder
                try:
                    shutil.move(src=source_file,
                                dst=original_file)
                except FileExistsError:
                    pass
            except KeyError:
                missing_files.add(file_name)
        # Print details of missing files
        if missing_files:
            if len(missing_files) == 1:
                print('Missing the following file: {mf}'.format(mf=', '.join(sorted(list(missing_files)))), flush=True)
            else:
                print('Missing the following files: {mf}'.format(mf=', '.join(sorted(list(missing_files)))),
                      flush=True)

    def __init__(self, rename_file, file_path):
        self.rename_file = rename_file
        self.file_path = file_path
        self.rename_path = os.path.join(self.file_path, 'renamed_files')
        self.original_path = os.path.join(self.file_path, 'original_files')
        os.makedirs(self.rename_path, exist_ok=True)
        os.makedirs(self.original_path, exist_ok=True)
        self.old_names = list()
        self.new_names = list()
        self.old_files = list()
        self.rename_dict = dict()
        self.file_dict = dict()


@Gooey(program_name='Rename-O-matic (Rename-O-tron-3000)',
       image_dir=image_path,
       show_restart_button=False,
       show_success_modal=False,
       show_failure_modal=False,
       required_cols=1)
def cli():
    # Parser for arguments
    parser = GooeyParser(description='Rename your files using a GUI')
    parser.add_argument('rename_file',
                        metavar='Rename file',
                        widget='FileChooser',
                        help='.tsv file with renaming information. Format must be: \n'
                             'Current file name (no file extension)[TAB]New file name (no file extension)',
                        gooey_options={
                            'validator': {
                                'test': '".tsv" in user_input',
                                'message': 'Your file must have a .tsv extension'
                            }
                        }
                        )
    parser.add_argument('file_path',
                        metavar='Folder path',
                        widget='DirChooser',
                        help='Folder containing files to rename')
    # Get the arguments into an object
    arguments = parser.parse_args()
    rename = Renamer(rename_file=arguments.rename_file,
                     file_path=arguments.file_path)
    rename.main()


if __name__ == '__main__':
    cli()
