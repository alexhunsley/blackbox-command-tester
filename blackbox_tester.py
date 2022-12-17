# blackbox_tester.py
#
# PoC for blackbox testing of commands/tools. Can test stdout and transformation of file trees
#
# Copyright Alex Hunsley 2022
#
#
# [x] add .blackbox-ignore empty file to any empty folders found. This is so git can check in empty folders which are a valid part of tests.
# [x] add stdin so can test commands that require user input
# [x] add clean command that kills all working dirs and all stdout_working.txt files
# [x] add comparison of stdout to expected stdout
# [x] add train mode -- records stout.txt and output/ from the tool run
# [x] add 'show only failures' param
# [ ] optional translation of 'first/last checksum' diffs to just checksum diff - consumer of folder compare doesn't usually care
# [ ] remove the 'variables' dict, let anything at global.yaml level be a variable for {var_name}.
# [ ] take target tests in suite as a param -- for running only some of them
# [ ] (maybe) do file timestamp comparison input v output
# [ ] make existing CSV output option a param
#
#
#
# stdin using subprocess:
#  https://stackoverflow.com/a/8475367
#
# The issue with self-test: the auto-call to clean finds legit working/ folders *inside the input/output dirs in the test* that we don't
# want to delete, and deletes those. Solution: Limit level we delete working/ folders to.
#
#

import shutil
import subprocess

import click
import yaml

from dir_comparison.dir_comparison import *
from dir_comparison.fake_file_system import *

YAML_CONFIG_FILE = "config.yaml"
YAML_GLOBAL_CONFIG_FILE = "global.yaml"

INPUT_DIR = "input"
EXPECTED_OUTPUT_DIR = "output"
WORKING_DIR = "working"
STDOUT_WORKING_COPY_FILE = 'stdout_working.txt'

STD_OUT_EXPECTED_CONTENT_FILENAME = "stdout.txt"

ignore_dirs = ["ignore_contents", ".git"]

# ENCODING = 'ascii'
ENCODING = 'utf-8'

def pr_red(skk, end='\n'): print("\033[91m{}\033[00m".format(skk), end=end)


def pr_yellow(skk): print("\033[93m{}\033[00m".format(skk))


def make_abs_path(rel_path):
    script_dir = os.path.dirname(__file__)
    return os.path.normpath(os.path.join(script_dir, rel_path))


# gets a value for key from yaml. Vars can be a dict of string replacements, or None.
# returns None if a key not found
def get_yaml_value_raw(yaml, global_yaml, key, vars=None, default_value=None):
    raw_value = yaml.get(key, default_value)

    value = raw_value

    if not value:
        value = global_yaml.get(key, default_value)

    if vars and value:
        # value is a string
        for replace_key, replace_value in vars.items():
            if isinstance(value, list):
                value = [v.replace(replace_key, replace_value) for v in value]
            else:
                value = value.replace(replace_key, replace_value)

    return value, raw_value


def get_yaml_value(yaml, global_yaml, key, vars=None, default_value=None):
    return get_yaml_value_raw(yaml, global_yaml, key, vars, default_value)[0]

# Note that this method takes and returns a byte string, only converting internally
# to list of ascii lines.
def trim_lines_until_after_line_containing(lines_as_bytes, text_match):
    if not text_match or not lines_as_bytes:
        return lines_as_bytes

    # print(f"lines_as_bytes = {lines_as_bytes}")

    all_lines = lines_as_bytes.decode(ENCODING)
    lines = all_lines.split('\n')

    return_lines = []

    append_lines = False

    for line in lines:
        if append_lines:
            return_lines.append(line)

        if text_match in line:
            append_lines = True

    # convert back to byte string
    all_lines = '\n'.join(return_lines)

    # print(f"trim lines: returning {return_lines}")
    return all_lines.encode(ENCODING)


# run single in-out comparison test in this folder. Returns (bool, bool) for (problem was found trying to run tests
# for this test suite dir, stdout problem status or comparison status (i.e. success/fail))
def run_command_and_compare(global_config, target_folder, test_index, expected_stdout_filename=None, record=False, report_failure_only=False, summary_csv=False):
    vars = global_config.get('variables', {})

    config_file = os.path.join(target_folder, YAML_CONFIG_FILE)

    try:
        with open(f'{target_folder}/config.yaml', 'r') as file:
            config = yaml.safe_load(file)
    except IOError as E:
        print(f'\nNo config.yaml found in {target_folder}')
        return False, False

    differences = []

    os.chdir(target_folder)

    shutil.rmtree(WORKING_DIR, ignore_errors=True)
    shutil.copytree(INPUT_DIR, WORKING_DIR)

    os.chdir(WORKING_DIR)

    stdout_mismatch_found = False

    expected_stdout_content = None

    if not record and os.path.exists(expected_stdout_filename):
        with open(expected_stdout_filename, 'rb') as f:
            expected_stdout_content = f.read()

    # copy input to working folder

    command, raw_command = get_yaml_value_raw(config, global_config, "command", vars)

    input_strings = get_yaml_value(config, global_config, "text_input", vars)

    if input_strings is not None:
        input_strings = '%s\n' % '\n'.join(input_strings)
        input_strings_binary = input_strings.encode(ENCODING)
    else:
        input_strings_binary = None

    # we need to do this in-script replacement AFTER any yaml variable replacements above
    command = command.replace("{WORKING_PATH}", make_abs_path(os.path.join(target_folder, WORKING_DIR)))

    # print(f'found command: {command}')

    completed_process = subprocess.run(command, input=input_strings_binary, shell=True, capture_output=True)

    expected_return_code = int(get_yaml_value(config, global_config, "expected_return_code", vars, default_value=0))

    ignore_stdout_until_after_line_containing = get_yaml_value(config, global_config, "ignore_stdout_until_after_line_containing", vars)

    # print(f"before trim len: {len(stdout_expected)} after trim: {len(expected_stdout_content)} trim to {ignore_stdout_until_after_line_containing}")
    #
    # print(f"Code: {completed_process.returncode} expected code: {expected_return_code}")

    response = None

    if completed_process.returncode != expected_return_code:
        differences.append(
            f"Running the command returned status code: {completed_process.returncode} when expected: {expected_return_code}")
    else:
        # if record = False, the latter can still be None, if no stdout.txt file specified.
        if record or expected_stdout_content is not None:

            raw_response = completed_process.stdout
            response = trim_lines_until_after_line_containing(raw_response, ignore_stdout_until_after_line_containing)

            if record:
                # we are recording standard out to file
                # print(f"Curr dir: {os.getcwd()}")
                with open(expected_stdout_filename, 'wb') as stdout_file:
                    stdout_file.write(response)
            else:
                if response != expected_stdout_content:
                    differences.append(f"* standard out didn't match the output given in stdout.txt.")
                    # print(f"Len found: {len(response)}, len expected: {len(expected_stdout_content)}")
                    # differences.append(f"* standard out didn't match the output given in stdout.txt.
                    # Expected:\n===8<===\n{expected_stdout_content}\n=== but I got:\n{response}\n===8<===")
                    stdout_mismatch_found = True


        # come up out of working/ folder, back to target_folder (root of this single test)
        os.chdir("..")

        if record:
            shutil.rmtree(EXPECTED_OUTPUT_DIR, ignore_errors=True)
            os.rename(WORKING_DIR, EXPECTED_OUTPUT_DIR)
        else:
            compare_folders(WORKING_DIR, EXPECTED_OUTPUT_DIR, differences, exit_on_first_difference=False,
                            section_size=1024 * 64, ignore_files=['.DS_Store', '.blackbox_ignore_this_file'])

    test_description = get_yaml_value(config, global_config, 'test_description', vars)

    test_failed = (len(differences) > 0)

    if not test_failed:
        # we want to keep working dir for comparisons when tests fail.
        shutil.rmtree(WORKING_DIR, ignore_errors=True)

    result = f"FAILED" if test_failed else f"SUCCESS"

    if not report_failure_only or test_failed:
        if summary_csv:
            output = f'{test_index},{result},"{test_description}","{os.path.basename(target_folder)}",{raw_command}'
        else:
            output = f"\nTest {test_index} {result}: \"{test_description}\" in dir \"{os.path.basename(target_folder)}\""

        if test_failed:
            pr_red(output)
        else:
            print(output)

        if test_failed:
            indent = '   '
            indent_newline = f"\n{indent}"
            pr_yellow("%s%s" % (indent, indent_newline.join(differences)))

    if stdout_mismatch_found:

        with open(STDOUT_WORKING_COPY_FILE, 'wb') as stdout_found:
            # print(f"Writing len {len(response)} to file because not matched")
            stdout_found.write(response)

    # print('\n')
    # back to root of test suite (where all test folders are based)
    os.chdir("../..")

    test_succeeded = (not stdout_mismatch_found) and len(differences) == 0

    return True, test_succeeded


def run_all_tests(root_dir, record=False, report_failure_only=False, summary_csv=False):
    if not os.path.exists(root_dir):
        print(f"Couldn't find test suite directory: {root_dir}.\nExiting.\n\n")
        sys.exit(1)

    global_config = {}

    yaml_global_config_path = f'{root_dir}/{YAML_GLOBAL_CONFIG_FILE}'

    if os.path.exists(yaml_global_config_path):
        try:
            with open(yaml_global_config_path, 'r') as file:
                global_config = yaml.safe_load(file)
        except IOError:

            print(f"\nCouldn't open global.yaml found in {root_dir}")
            return False, False

    # remap all vars to {var} inm the global config
    if global_config:
        vars = global_config.get('variables', {})

        vars = dict((f"{{{key}}}", val) for key, val in vars.items())

        global_config['variables'] = vars

    for root, dirs, files in os.walk(root_dir, topdown=True):

        test_index = 0
        succeeded_test_count = 0
        failed_test_count = 0

        dirs_filt = [x for x in dirs if not x in ignore_dirs]
        dirs_filt.sort()

        for dir in dirs_filt:

            target_dir = os.path.join(root_dir, dir)

            stdout_expected = None

            # expected_stdout_filename = os.path.join(target_dir, STD_OUT_EXPECTED_CONTENT_FILENAME)
            expected_stdout_filename = os.path.join("..", STD_OUT_EXPECTED_CONTENT_FILENAME)

            (found_test_suite, test_status) = run_command_and_compare(global_config, target_dir, test_index,
                                                                      expected_stdout_filename, record, report_failure_only, summary_csv=summary_csv)

            if not found_test_suite:
                print(
                    '\nError when running test suite, giving up. Did you specify the correct folder?\nTypically you '
                    'want to specify a folder two directories up from the input/ and output/ folders.\n')
                sys.exit(1)

            if test_status:
                succeeded_test_count += 1
            else:
                failed_test_count += 1

            test_index += 1

        # replace dirs list in-place to stop any descending further in the tree
        dirs[:] = []

    print(f"\n{failed_test_count} failures in {test_index} tests.\n")


# removes diagnostic files from test suite, i.e. working/ dirs and stdout_working.txt files.
# this function doesn't remove such files that are deeper than 2 dirs in the hierarchy,
# as they would be part of test case data, and not result of direct running of a test case (v meta).
def clean_test_suite(root_dir):
    for root, dirs, files in os.walk(root_dir, topdown=True):

        num_path_components = len(root.split('/'))

        if num_path_components != 2:
            # Only target files/dir names at this level are legitimately things to delete for these tests.
            # Any deeper instances are part of test input or output!
            return

        if STDOUT_WORKING_COPY_FILE in files:
            file_to_remove = os.path.join(root, STDOUT_WORKING_COPY_FILE)
            os.remove(file_to_remove)

        if WORKING_DIR in dirs:
            dir_to_remove = os.path.join(root, WORKING_DIR)
            shutil.rmtree(dir_to_remove)


@click.command(no_args_is_help=False)
@click.argument('test_suite_dir')
@click.option('--clean', is_flag=True, help='Clean the test suite dir of output fragments')
@click.option('--record', is_flag=True, help='Record standard out from tests as the expected content')
@click.option('--report-failure-only', is_flag=True, help='Only report details for failed tests')
def run(test_suite_dir, clean, record, report_failure_only):
    # print("TEST SUITE DIR: ", test_suite_dir) DE

    # print(f"Running test at {os.getcwd()}")

    print(f"Cleaning artifacts from test suite dir: {test_suite_dir}\n")
    clean_test_suite(test_suite_dir)
    # print("Done.\n\n")

    if clean:
        sys.exit(0)

    print(f"Running test suite in dir: {test_suite_dir}\n\n")
    run_all_tests(test_suite_dir, record, report_failure_only)

    print("Done.\n\n")


if __name__ == '__main__':
    run()
