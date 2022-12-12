# blackbox_tester.py
#
# PoC for blackbox testing of commands/tools. Can test stdout and transformation of file trees
#
# Copyright Alex Hunsley 2022
#
#
# [ ] add .blackbox-ignore empty file to any empty folders found. This is so git can check in empty folders which are a valid part of tests.
# [x] add stdin so can test commands that require user input
# [x] add tidy command that kills all working dirs and all stdout_working.txt files
# [x] add comparison of stdout to expected stdout
#
#
# Possible future additions:
#
# train mode -- writes output to input files -- for use when you are sure the tool you are testing is behaving properly.
#    -- could do either ALL or select tests in suite.
#
# stdin using subprocess:
#  https://stackoverflow.com/a/8475367
#

import click

import yaml

import os
import hashlib
import shutil
import subprocess

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

def prRed(skk, end = '\n'): print("\033[91m{}\033[00m".format(skk), end = end)

def prYellow(skk): print("\033[93m{}\033[00m" .format(skk))


def make_abs_path(rel_path):
	script_dir = os.path.dirname(__file__)
	return os.path.normpath(os.path.join(script_dir, rel_path))


# gets a value for key from yaml. Vars can be a dict of string replacements, or None.
# returns None if a key not found
def get_yaml_value(yaml, global_yaml, key, vars = None, default_value = None):
	value = yaml.get(key, default_value)

		# print(f"BEFORE value = {value}")
	if not value:
		print(f"Didn't find {key} in yaml, looking in global_yaml = {global_yaml}: ")
		value = global_yaml.get(key, default_value)
		print(f"   ... and I found {value}")


	if value and vars:
		print("DSFDSFS")
		for replace_key, replace_value in vars.items():
			value = value.replace(replace_key, replace_value)

	# print(f"AFTER value = {value}")

	return value


# run single in-out comparison test in this folder.
# Returns (bool, bool) for (problem was found trying to run tests for this test suite dir, stdout problem status or comparison status (i.e. success/fail))
def run_command_and_compare(global_config, root_dir, target_folder, test_index, expected_stdout_content = None):
	# print(f"Running test at {folder}, wd = ", os.getcwd())

	vars = global_config.get('variables', {})

	stdout_mismatch_found = False

	config_file = os.path.join(target_folder, YAML_CONFIG_FILE)

	# print(f"Config: {config_file}")

	try: 
		with open(f'{target_folder}/config.yaml', 'r') as file:
			config = yaml.safe_load(file)
	except IOError as E:
		print(f'\nNo config.yaml found in {target_folder}')
		return (False, False)

	if testy := get_yaml_value(config, global_config, "test_var"):
		print(f"0---------- testy: {testy}")
	else:
		print("No tresty found")


	# print(config)

	differences = []

	os.chdir(target_folder)

	shutil.rmtree(WORKING_DIR, ignore_errors=True)
	shutil.copytree(INPUT_DIR, WORKING_DIR)

	os.chdir(WORKING_DIR)

	# copy input to working folder

	command = get_yaml_value(config, global_config, "command", vars)

	if input_strings := get_yaml_value(config, global_config, "text_input", vars):
		input_strings = '%s\n' % '\n'.join(input_strings)
		input_strings_binary = input_strings.encode('ascii')
	else:
		input_strings_binary = None

	# we need to do this in-script replacement AFTER any yaml variable replacements above
	command = command.replace("{WORKING_PATH}", make_abs_path(os.path.join(target_folder, WORKING_DIR)))

	completed_process = subprocess.run(command, input=input_strings_binary, shell=True, capture_output=True)

	# print(f"Completed process = {completed_process}")

	if completed_process.returncode != 0:
		differences.append(f"Running the command failed, status code: {completed_process.returncode}")
	else:
		# print(f"expected_stdout_content = {expected_stdout_content}")

		if expected_stdout_content != None:

			# response = p.stdout.readlines(-1)
			# response = p.stdout.read()
			response = completed_process.stdout

			# print(f"expected: {expected_stdout_content} got: {response}")
			
			if response != expected_stdout_content:
				differences.append(f"* standard out didn't match the output given in stdout.txt.")
				# differences.append(f"* standard out didn't match the output given in stdout.txt. Expected:\n===8<===\n{expected_stdout_content}\n=== but I got:\n{response}\n===8<===")
				stdout_mismatch_found = True
			
			# print(f"Command response: {response}")

		# back to target_folder (root of this single test)
		os.chdir("..")

		compare_folders(WORKING_DIR, EXPECTED_OUTPUT_DIR, differences, exit_on_first_difference = False, section_size = 1024 * 64, ignore_files = ['.DS_Store', '.blackbox_ignore_this_file'])

	# print(f"differences: {differences}")

	test_description = get_yaml_value(config, global_config, 'test_description', vars)

	# test_failed = True if len(differences) == 0 else False
	test_failed = (len(differences) > 0)

	if not test_failed:
		# we want to keep working dir for comparisons when tests fail.
		shutil.rmtree(WORKING_DIR, ignore_errors=True)

	result = f"FAILED: " if test_failed else f"SUCCESS: "

	output = f"Test {test_index} {result} \"{test_description}\" in dir \"{target_folder}\""

	if test_failed:
		prRed(output)
	else:
		print(output)

	#"    for test \"{test_description}\" in dir \"{target_folder}\"")

	if test_failed:
		indent = '   '
		indent_newline = f"\n{indent}"
		prYellow("%s%s" % (indent, indent_newline.join(differences)))

	if stdout_mismatch_found:
		stdout_as_ascii = response.decode('ascii')

		# print(f"[[[\nstdout gave:\n{stdout_as_ascii}\n]]]")


		with open(STDOUT_WORKING_COPY_FILE, 'wb') as stdout_found:
			stdout_found.write(response)

	print('\n')
	# back to root of test suite (where all test folders are based)
	os.chdir("../..")

	test_succeeded = (not stdout_mismatch_found) and len(differences) == 0

	return (True, test_succeeded)


def run_all_tests(root_dir):

	print(f"AA 1.1    Running test at {os.getcwd()}")

	if not os.path.exists(root_dir):
		print(f"Couldn't find test suite directory: {root_dir}.\nExiting.\n\n")
		sys.exit(1)


	# global_config_file = os.path.join(root_dir, YAML_GLOBAL_CONFIG_FILE)

	# print(f"Config: {config_file}")

	global_config = {}

	yaml_global_config_path = f'{root_dir}/{YAML_GLOBAL_CONFIG_FILE}'

	print(f"AA 1 global path = {yaml_global_config_path}")
	print(f"AA 1.5    Running test at {os.getcwd()}")

	if os.path.exists(yaml_global_config_path):
		print("AA 2")
		try: 
			with open(yaml_global_config_path, 'r') as file:
				global_config = yaml.safe_load(file)
		except IOError as E:
			print("AA 4")

			print(f"\nCouldn't open global.yaml found in {root_dir}")
			return (False, False)

	# remap all vars to {var} inm the global config
	if global_config:
		print("============ gpt global config!")
		vars = global_config.get('variables', {})

		# print(f"|{global_config}|")

		vars = dict((f"{{{key}}}", val) for key, val in vars.items())

		global_config['variables'] = vars


	print("AA 5")

	for root, dirs, files in os.walk(root_dir, topdown=True):

		test_index = 0
		succeeded_test_count = 0
		failed_test_count = 0

		dirs_filt = [x for x in dirs if not x in ignore_dirs]
		dirs_filt.sort()
		# print("dirs_filt = ", dirs_filt)

		for dir in dirs_filt:

			target_dir = os.path.join(root_dir, dir)
			
			stdout_expected = None

			stdout_filename = os.path.join(target_dir, STD_OUT_EXPECTED_CONTENT_FILENAME)

			if os.path.exists(stdout_filename):
				with open(stdout_filename, 'rb') as f:
					stdout_expected = f.read()

			(found_test_suite, test_status) = run_command_and_compare(global_config, root_dir, target_dir, test_index, stdout_expected)

			if not found_test_suite:
				print('\nError when running test suite, giving up. Did you specify the correct folder?\nTypically you want to specify a folder two directories up from the input/ and output/ folders.\n')
				sys.exit(1)

			if test_status:
				succeeded_test_count += 1
			else:
				failed_test_count += 1

			test_index += 1

		# replace dirs list in-place to stop any descending further in the tree
		dirs[:] = []

	print(f"{failed_test_count} failures in {test_index} tests.\n")


# removes diagnostic files from test suite, i.e. working/ dirs and stdout_working.txt files
def clean_test_suite(root_dir):
	for root, dirs, files in os.walk(root_dir, topdown=True):

		if STDOUT_WORKING_COPY_FILE in files:
			file_to_remove = os.path.join(root, STDOUT_WORKING_COPY_FILE)
			os.remove(file_to_remove)
			# print(f"Deleted file: {file_to_remove}")

		if WORKING_DIR in dirs:
			dir_to_remove = os.path.join(root, WORKING_DIR)
			# print(f"Deleted dir: {dir_to_remove}")
			shutil.rmtree(dir_to_remove)


@click.command(no_args_is_help=False)
@click.argument('test_suite_dir')
@click.option('--clean', is_flag=True, help='Clean the test suite dir of output fragments')
def run(test_suite_dir, clean):

	# print("TEST SUITE DIR: ", test_suite_dir) DE

	print(f"AA 1.0    Running test at {os.getcwd()}")

	print(f"Cleaning artifacts from test suite dir: {test_suite_dir}\n")
	clean_test_suite(test_suite_dir)
	# print("Done.\n\n")

	if clean:
		sys.exit(0)

	print(f"Running test suite in dir: {test_suite_dir}\n\n")
	run_all_tests(test_suite_dir)

	print("Done.\n\n")

if __name__ == '__main__':
	run()

