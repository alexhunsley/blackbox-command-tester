# Blackbox command tester

This is a proof-of-concept.

It's a tool for verifying input files versus output files for a command line tool. Typically you'd use it to test a command line tool you'd written, to ensure that its functionality has not changed.

As a very simple example, image you want to verify that the `cat` command is able to write to a file (and also that it will not change a file with a different name that already exists). The directory `examples_tests/0_cat_command_creates_a_file` demonstrates the setup to do this:


```
    0_cat_command_creates_a_file/
      input/
        existing_file.txt
      output/
        existing_file.txt
        file_created_by_cat.txt
      config.yml      
```

This entire structure describes a single test.

`Blackox_tester` works by running the command (specified in `config.yml`) against the contents of the `input` folder. It then verifies that the result matches what is in the `output` directory.

The `config.yml` file specifies what command to run:

```
    test_description: 'test if cat command creates a file, leaving an existing file alone'
    command: 'echo This is some text. | cat > file_created_by_cat.txt'
```

Note that `test_description` is cosmetic only, but is worth specifying -- it will make `blackbox_tester` output easier to understand.

# Blackbox Tester runs a suite of tests

If you look inside the directory `examples_tests`, you'll see three folders, which specify three tests:

```
    0_cat_command_creates_a_file
    1_cat_output_to_stdout
    2_a_faulty_test_that_demonstrates_failure
```

This `example_tests` folder comprises a *test suite*. When you run Blackbox Tester, you point it at a test suite directory, not at a single test, and it runs all the tests it finds in that test suite directory.

For example, to run the `example_tests` suite, you run the command:

```
    python3 blackbox_tester.py example_tests
```

The output summarises the success or failure of every test in the suite:

```
    Cleaning artifacts from test suite dir: example_tests
    
    Running test suite in dir: example_tests
    
    
    Test 0 SUCCESS:  "test if cat command creates a file, leaving an existing file alone" in dir "example_tests/0_cat_command_creates_a_file"
    
    
    Test 1 SUCCESS:  "test if echo emits to standard out" in dir "example_tests/1_cat_output_to_stdout"
    
    
    Test 2 FAILED:  "test if cat command creates a file, leaving an existing file alone, deliberate diffs" in dir "example_tests/2_a_faulty_test_that_demonstrates_failure"
       Between working and output, found orphan files/folders: ['orphan_in_input.txt']
    
    
    1 failures in 3 tests.
    
    Done.
```

Test 2 has deliberately been set up to demonstrate failure. When a test fails because the `input` folder contents don't match the `output` folder contents, Blackbox Tester leaves a directory named `working` behind to help you debug the issue. To see the problem, run your favourite diff tool on these two directories inside `example_tests/2_a_faulty_test_that_demonstrates_failure`: 

```
   output/
   working/
```

Any diff you see is the cause of the failure. In this case, it's the presence of a file `orphan_in_input.txt` in the `input` folder that isn't present in the `output` folder.

Once you've corrected your tests (or fixed a bug in your tool!), and want to try the tests again, you might think to remove the `working` folder(s). But there's no need to do this yourself: at the start of a test suite run, Blackbox Tester automatically removes any `working` folders. If you want to clean these folders up without running the test suite again, run `python3 blackbox_tester.py --clean`.

# Testing stdout output for a command

Blackbox Tester can also check the standard output produced by a command.

To do this, place the expected output in a text file `stdout.txt`. Here's a layout of a folder containing a standard out test:


```
    some_test/
      input/
        existing_file.txt
      output/
        existing_file.txt
        file_created_by_cat.txt
      stdout.txt   <----- the expected standard out contents
      config.yml      
```

Should the `stdout.txt` contents not match what the command actually output, a file is saved that shows the actual output: `stdout_working.txt`. You shoould diff this against your `stdout.txt` file to see any differences.

