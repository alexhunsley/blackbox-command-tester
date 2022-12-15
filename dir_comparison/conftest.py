import pytest


# takes the fs fixture which is patched-in a fake file system
@pytest.fixture()
def fake_dirs_same_contents(fs):
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
