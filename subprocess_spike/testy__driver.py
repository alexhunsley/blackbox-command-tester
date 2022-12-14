# testy__driver.py

import subprocess
import sys



def run_command__popen(command, communicate_string = None):
	p = subprocess.Popen(command, 
		shell=True,
		stdin=subprocess.PIPE,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE)

	p_status = None

	if communicate_string != None:
		print("Calling communicate etc")
		# get ret code of None if we don't do this
		# (stdout_data, stderr_data) = p.communicate(b"alex\nhuns")
		(stdout_data, stderr_data) = p.communicate(b"a.nice.key\nThe value\nf\ny")

		# SO suggestion instead of p.returncode. Still get 1.
		p_status = p.wait()
	else:
		p_status = p.wait()

	# print(f"============ stdout looks like: {stdout_data}")


	# stdoutdata, stderrdata = process.communicate()
	# print process.returncode

	# None means the process didn't terminate yet!
	print(f"RET CODE: {p.returncode} {p_status}")


# THIS WORKS
# 'run' is preferred to 'check_output', according to https://stackoverflow.com/a/55758810
# use 'input' param for the stdin content
def run_command__run(command, input_strings = None):
	print(f"\n==================== calling run_command with command: {command} input: {input_strings}")
	# output = subprocess.check_output(command, shell=True))

	completed_process = subprocess.run(command, input=input_strings, shell=True)

	print(f"completedProcess = {completed_process}")

	# try:
	#     output = subprocess.check_output(command, shell=True)                       
	# except subprocess.CalledProcessError as grepexc:                                                                                                   
	#     print(f"error code {grepexc.returncode} output: {grepexc.output}")



# we get 127, i.e. -1, if communicate gives input not recognised, i.e. script doesn't exit
# run_command__popen("testy_no_input_ret_0.py")

# so these both work
run_command__run("python3 testy_no_input_ret_0.py")
run_command__run("python3 testy_no_input_ret_1.py")

run_command__run("python3 testy_take_input_ret_0.py", b"alex\nhunsley\n")
run_command__run("python3 testy_take_input_ret_1.py", b"alex\nhunsley\n")

# incomplete input test - bombs out with code 1 due to finding EOF in input
# run_command__run("python3 testy_take_input_ret_1.py", b"alex\n")
