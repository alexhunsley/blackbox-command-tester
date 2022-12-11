from pyfakefs import fake_filesystem
from pyfakefs.fake_filesystem import *
from pyfakefs.fake_filesystem_unittest import Patcher
import pyfakefs

import sys

import os
import hashlib
import io

# SECTION_SIZE_DEFAULT = 1024
# the doctests require start/end section size that is v small, 4 is good.
SECTION_SIZE_DEFAULT = 4

# seek and tell to return the current file position after seek.
# Doing this because pyfakefs returns None from Seek, like python2 does - backwards compatability thing?
def seek_t(file, offset, whence):
    file.seek(offset, whence)
    return file.tell()


def hash_data(data):
    return hashlib.md5(data).hexdigest()


def hash_file(filename):
    with open(filename, 'rb') as file:
        return hash_data(file.read())



def compare_files(filename1, filename2, section_size=1024):
    # with open_provider.open(filename1, "rb") as f1, open_provider.open(filename2, "rb") as f2:
    #     return compare_files_f(filename1, filename2, f1, f2, section_size)

    with open(filename1, "rb") as f1, open(filename2, "rb") as f2:
        return compare_files_f(filename1, filename2, f1, f2, section_size)


def compare_files_f(file1, file2, f1, f2, section_size=1024):
    """
    None is returned when two empty files given:
        >>> compare_files_f("A", \
                            "B", \
                            io.BytesIO(b""), \
                            io.BytesIO(b""), \
                            1024)
        >>>

    Files are the same and are small enough to be checksummed in total:
        >>> compare_files_f("A", \
                            "B", \
                            io.BytesIO(b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01"), \
                            io.BytesIO(b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01"), \
                            1024)
        >>>

    Files are the same and are large enough to be checksummed at start and end::
        >>> compare_files_f("A", \
                            "B", \
                            io.BytesIO(b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01"), \
                            io.BytesIO(b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01"), \
                            2)
        >>>

    Files are different lengths: (1):
        >>> compare_files_f("A", \
                            "B", \
                            io.BytesIO(b"\x02\x01\"), \
                            io.BytesIO(b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01"), \
                            1024)
        '* Size differs: A != B: A = 2, B = 16'
    
    Files differ and are small enough to be checksummed in total (1):
        >>> compare_files_f("A", \
                            "B", \
                            io.BytesIO(b"\x02\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01"), \
                            io.BytesIO(b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01"), \
                            1024)
        '* Full file checksum differs: A != B'


    Files differ and are small enough to be checksummed in total (2):
        >>> compare_files_f("A", \
                            "B", \
                            io.BytesIO(b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x02"), \
                            io.BytesIO(b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01"), \
                            1024)
        '* Full file checksum differs: A != B'

    Files differ and are small enough to be checksummed in total (3):
        >>> compare_files_f("A", \
                            "B", \
                            io.BytesIO(b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01"), \
                            io.BytesIO(b"\x02\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01"), \
                            1024)
        '* Full file checksum differs: A != B'


    Files differ and are small enough to be checksummed in total (4):
        >>> compare_files_f("A", \
                            "B", \
                            io.BytesIO(b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01"), \
                            io.BytesIO(b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x02"), \
                            1024)
        '* Full file checksum differs: A != B'


    Files differ at start and are large enough to be checksummed at start and end: (1):
        >>> compare_files_f("A", \
                            "B", \
                            io.BytesIO(b"\x02\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01"), \
                            io.BytesIO(b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01"), \
                            4)
        '* First part checksum mismatch: A and B'

    Files differ at end and are large enough to be checksummed at start and end: (2):
        >>> compare_files_f("A", \
                            "B", \
                            io.BytesIO(b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01"), \
                            io.BytesIO(b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x02"), \
                            4)
        '* Last part checksum mismatch: A and B'
    """

    # print(f"*** compare files called with {file1} {file2}")
    # Get the file sizes
    size1 = seek_t(f1, 0, 2)
    size2 = seek_t(f2, 0, 2)

    # If the files are different sizes, return False
    if size1 != size2:
        return f"* Size differs: {file1} != {file2}: {file1} = {size1}, {file2} = {size2}"

    # If the files are small enough, compute the MD5 checksum of the entire contents
    # of both files and compare the checksums
    # print(f"comp sizes: {size1} {section_size}")
    if size1 < 3 * section_size:
        # return to start of files
        f1.seek(0)
        f2.seek(0)

        checksum1 = hash_data(f1.read())
        checksum2 = hash_data(f2.read())

        return None if checksum1 == checksum2 else f"* Full file checksum differs: {file1} != {file2}"

    # print(f"============ doing the start, end comparison! for {file1}")

    # File is large enough that we want to compute the MD5 checksum of
    # the first and last section_size bytes of each file
    f1.seek(0)
    f2.seek(0)
    first1 = f1.read(section_size)
    first2 = f2.read(section_size)

    # Compute the MD5 checksums of the first section of each file
    first_checksum1 = hash_data(first1)
    first_checksum2 = hash_data(first2)

    # print(f"first checksums: {first_checksum1} {first_checksum2}")
    # If the first section_size bytes of each file have different checksums,
    # return False
    if first_checksum1 != first_checksum2:
        return f"* First part checksum mismatch: {file1} and {file2}"

    # print("___________ comparing last:")
    # Read the last section_size bytes of each file and compute their checksums

    f1.seek(-section_size, 2)
    f2.seek(-section_size, 2)
    last1 = f1.read(section_size)
    last2 = f2.read(section_size)
    last_checksum1 = hash_data(last1)
    last_checksum2 = hash_data(last2)

    # Return True if the checksums are the same, otherwise return False
    return None if last_checksum1 == last_checksum2 else f"* Last part checksum mismatch: {file1} and {file2}"


def filepath_with_slashes_added_to_dirs(filename, dir1, dir2):
    if os.path.isdir(os.path.join(dir1, filename)) or os.path.isdir(os.path.join(dir2, filename)):
        return f"{filename}/"

    return filename


def set_to_sorted_list(s):
    arr = list(s)
    arr.sort()
    return arr



def pretty_print_differences(diffs):
    print(len(diffs))
    for difference in diffs:
        print(difference)


def test_same_contents():
    """ 
>>> test_same_contents()
0
    """    
    with Patcher() as patcher:
        fs = fake_file_system.make_fake_dirs_same_contents(patcher.fs)
        # print("compare_files result: (None = same) ", compare_files(f1, f2))
        differences = []
        compare_folders("0/", "1/", differences, False)
        pretty_print_differences(differences)




def test_no_diffs_when_no_contents():
    """ 
>>> test_no_diffs_when_no_contents()
0
    """    
    with Patcher() as patcher:
        fs = fake_file_system.make_fake_dirs_empty(patcher.fs)
        # print("compare_files result: (None = same) ", compare_files(f1, f2))
        differences = []
        compare_folders("0/", "1/", differences, False)
        pretty_print_differences(differences)


def test_it_show_all_issues_with_diffs():
    """ 
>>> test_it_show_all_issues_with_diffs()
7
Between 0/dir1/dir1.1 and 1/dir1/dir1.1, found orphan files/folders: ['file_orphan_1.1.1.txt', 'file_orphan_1.1.1b.txt']
* Size differs: 0/dir1/file1.2.txt != 1/dir1/file1.2.txt: 0/dir1/file1.2.txt = 20, 1/dir1/file1.2.txt = 25
* One file, one folder: file-dir-same-name-A in dirs 0/ and 1/
* One file, one folder: file-dir-same-name-B in dirs 0/ and 1/
* Last part checksum mismatch: 0/file1_long_diff_end.txt and 1/file1_long_diff_end.txt
* First part checksum mismatch: 0/file1_long_diff_start.txt and 1/file1_long_diff_start.txt
* Full file checksum differs: 0/file1_short_diff.txt != 1/file1_short_diff.txt
>>>    
    """
    with Patcher() as patcher:
        fs = fake_file_system.make_fake_dirs_with_diff(patcher.fs)
        # print("compare_files result: (None = same) ", compare_files(f1, f2))
        differences = []
        compare_folders("0/", "1/", differences, False)
        pretty_print_differences(differences)


def test_it_exit_on_first_issue_with_diffs():
    """ 
>>> test_it_exit_on_first_issue_with_diffs()
3
Between 0/dir1/dir1.1 and 1/dir1/dir1.1, found orphan files/folders: ['file_orphan_1.1.1.txt', 'file_orphan_1.1.1b.txt']
* Size differs: 0/dir1/file1.2.txt != 1/dir1/file1.2.txt: 0/dir1/file1.2.txt = 20, 1/dir1/file1.2.txt = 25
* One file, one folder: file-dir-same-name-A in dirs 0/ and 1/
>>>    
    """
    with Patcher() as patcher:
        fs = fake_file_system.make_fake_dirs_with_diff(patcher.fs)
        # print("compare_files result: (None = same) ", compare_files(f1, f2))
        differences = []
        compare_folders("0/", "1/", differences, True)
        pretty_print_differences(differences)



# returns a set
def filter_files(files):
    
    ignore_files = ['.DS_Store']
    
    return set([x for x in files if not x in ignore_files])


# TODO use walkdir instead of listdir (which requires us to isdir())
def compare_folders(folder1, folder2, differences, exit_on_first_difference = False, section_size = SECTION_SIZE_DEFAULT):

    files1 = filter_files(os.listdir(folder1))
    files2 = filter_files(os.listdir(folder2))

    # files1 = filter_files(files1)
    # files2 = filter_files(files2)

    # make debugging easier!
    # files1.sort()
    # files2.sort()

    all_files = files1.union(files2)
    common_files = files1.intersection(files2)
    orphan_files = all_files - common_files

    if len(orphan_files):
        # make it obvious which is a folder by appending '/'
        files_with_slashes_end_dirs = [filepath_with_slashes_added_to_dirs(f, folder1, folder2) for f in orphan_files]
        files_with_slashes_end_dirs.sort()

        differences.append(f"Between {folder1} and {folder2}, found orphan files/folders: {files_with_slashes_end_dirs}")


    # Compare the files in each folder
    for file in set_to_sorted_list(common_files):
        # print(f"        processing {file}")

        num_dirs = (1 if os.path.isdir(os.path.join(folder1, file)) else 0) \
                 + (1 if os.path.isdir(os.path.join(folder2, file)) else 0)

        # print(f"|||||||| numDir = {num_dirs}")

        if num_dirs == 2:
            compare_folders(
                os.path.join(folder1, file),
                os.path.join(folder2, file),
                differences,
                exit_on_first_difference,
                section_size = section_size
            )
            continue
        elif num_dirs == 1:
            differences.append(f"* One file, one folder: {file} in dirs {folder1} and {folder2}")
            if exit_on_first_difference:
                return
            continue 
        else:  # it's two files
            # Check if the file exists in the other folder
            # If the file exists, compare the contents of the files
            result_differences = compare_files(
                os.path.join(folder1, file),
                os.path.join(folder2, file),
                section_size = section_size
            )
            if result_differences is not None:
                differences.append(result_differences)
                if exit_on_first_difference:
                    return


# test_it_show_all_issues_with_diffs()


if __name__ == "__main__":

    # do here so it's not imported if we're used from another module (like black_box_tester.py)
    # as that fails
    import fake_file_system

    import doctest
    print("Runnting doctests...")
    doctest.testmod()
