# fake_file_system.py
import pytest
from pyfakefs import fake_filesystem
from pyfakefs.fake_filesystem import *


def char_count(str, c):
    return len(str.split(c))


def testo(fake_dirs_same_contents):
    assert os.path.exists("/0/file1_short_same.txt")


def tree_fake(fs, directory, indent=2, chars_for_path=30):
    fake_os = fake_filesystem.FakeOsModule(fs)

    start_dir_depth = char_count(directory, os.sep)

    for root, dirs, files in fake_os.walk(directory):

        full_dir_path = fake_os.path.join(directory, root)

        level = char_count(root, os.sep) - start_dir_depth

        indent = ' ' * 2 * (level)

        # don't print the start directory itself
        if root != directory:
            print(f'{indent}{os.path.basename(root)}/')

        subindent = ' ' * 2 * (level + 1)
        for f in files:
            full_file_path = fake_os.path.join(full_dir_path, f)

            file_size = fake_os.stat(full_file_path).st_size

            line = f'{subindent}{f}'.ljust(chars_for_path)

            print(f'{line}{file_size}')

# def demo_fake_fs():
# 	# demos making fs manually by default in function
# 	fs = make_fake_dirs_with_diff()
# 	print(fs)

# 	# Demos using general patcher
# 	with Patcher() as patcher:
# 		make_fake_dirs_with_diff(patcher.fs)

# 		# the following code works on the fake filesystem
# 		with open("0/file1.txt") as f:
# 			contents = f.read()
# 			print(contents)

# 	return fs

# fs = demo_fake_fs()
# print(tree_fake(fs, "/"))
