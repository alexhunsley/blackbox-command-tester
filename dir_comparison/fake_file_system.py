# fake_file_system.py

from pyfakefs import fake_filesystem
from pyfakefs.fake_filesystem import *

def char_count(str, c):
	return len(str.split(c))


def make_fake_dirs_empty(fs = fake_filesystem.FakeFilesystem()):
	fs.create_dir("/0/")
	fs.create_dir("/1/")

	return fs


def make_fake_dirs_same_contents(fs = fake_filesystem.FakeFilesystem()):
	# short identical files (full length checksum)
	fs.create_file("/0/file1_short_same.txt", contents="Hello!\n")
	fs.create_file("/1/file1_short_same.txt", contents="Hello!\n")

	# long identical files (two checksums)
	fs.create_file("/0/file1_long_same.txt", contents="Hello! And why not, my friend. Kitten!\n")
	fs.create_file("/1/file1_long_same.txt", contents="Hello! And why not, my friend. Kitten!\n")

	# short identical files (full length checksum)
	fs.create_file("/0/aaa/file1.txt", contents="Hello!\n")
	fs.create_file("/1/aaa/file1.txt", contents="Hello!\n")

	# identical file in subdir
	fs.create_file("/0/dir1/file1.1.txt", contents="Hello chicken\nBooya!")
	fs.create_file("/1/dir1/file1.1.txt", contents="Hello chicken\nBooya!")

	# empty subdirs
	fs.create_dir("/0/empty_dir")
	fs.create_dir("/1/empty_dir")

	return fs


def make_fake_dirs_with_diff(fs = fake_filesystem.FakeFilesystem()):

	# fs_module.touch('/path/to/file.txt')

	# short identical files (full length checksum)
	fs.create_file("/0/file1_short_same.txt", contents="Hello!\n")
	fs.create_file("/1/file1_short_same.txt", contents="Hello!\n")

	# long identical files (full length checksum)
	fs.create_file("/0/file1_long_same.txt", contents="Hello! And why not, my friend. Kitten!\n")
	fs.create_file("/1/file1_long_same.txt", contents="Hello! And why not, my friend. Kitten!\n")


	# short different files
	fs.create_file("/0/file1_short_diff.txt", contents="Hello!\n")
	fs.create_file("/1/file1_short_diff.txt", contents="_ello!\n")

	# long different files
	fs.create_file("/0/file1_long_diff_end.txt", contents="Hello! And why not, my friend. Kitten!\n")
	fs.create_file("/1/file1_long_diff_end.txt", contents="Hello! And why not, my friend. Kitte_!\n")

	# long different files
	fs.create_file("/0/file1_long_diff_start.txt", contents="Hello! And why not, my friend. Kitten!\n")
	fs.create_file("/1/file1_long_diff_start.txt", contents="_ello! And why not, my friend. Kitten!\n")

	# short identical files (full length checksum)
	fs.create_file("/0/file1.txt", contents="Hello!\n")
	fs.create_file("/1/file1.txt", contents="Hello!\n")

	# identical file in subdir
	fs.create_file("/0/dir1/file1.1.txt", contents="Hello chicken\nBooya!")
	fs.create_file("/1/dir1/file1.1.txt", contents="Hello chicken\nBooya!")

	# len different file in subdir
	fs.create_file("/0/dir1/file1.2.txt", contents="Hello chicken\nBooya!")
	fs.create_file("/1/dir1/file1.2.txt", contents="Hello chIcken\nBooya! more")

	# char different file in subdir
	fs.create_file("/0/dir1/file1.3.txt", contents="Hello chicken\nBooya!")
	fs.create_file("/1/dir1/file1.3.txt", contents="Hello chIcken\nBooya!")

	# empty subdirs
	fs.create_dir("/0/empty_dir")
	fs.create_dir("/1/empty_dir")

	# file only in 0
	fs.create_file("/0/dir1/dir1.1/file_orphan_1.1.1.txt", contents="This is an orphan in 0")

	# file only in 1
	fs.create_file("/1/dir1/dir1.1/file_orphan_1.1.1b.txt", contents="This is also an orphan, yay")

	# same name that is a file in 0, dir in 1
	fs.create_file("/0/file-dir-same-name-A", contents="")
	fs.create_dir("/1/file-dir-same-name-A")

	# same name that is a dir in 0, file in 0
	fs.create_dir("/0/file-dir-same-name-B")
	fs.create_file("/1/file-dir-same-name-B", contents="")

	return fs


def tree_fake(fs, directory, indent = 2, chars_for_path = 30):
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


