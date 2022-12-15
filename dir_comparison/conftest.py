import pytest

@pytest.fixture()
def fake_dirs_empty(fs):
    fs.create_dir("/0/")
    fs.create_dir("/1/")

    return fs


# takes the fs fixture which is a patched-in fake file system
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


@pytest.fixture()
def fake_dirs_with_diffs(fs):
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
