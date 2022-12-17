# Blackbox command tester

This is a proof-of-concept.

It's a tool for verifying standard output and/or file processing for a command line tool. Typically you'd use it to verify the behaviour of a tool you'd
written.

As a very simple example, suppose you want to verify that the `cat` command is able to write to a file (and also that it will not change a
file with a different name that already exists). The directory `examples_tests/0_cat_command_creates_a_file` demonstrates the setup to do
this:

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

`Blackox_tester` works by running the command (specified in `config.yml`) against the contents of the `input` folder. It then verifies that
the result matches what is in the `output` directory.

The `config.yml` file specifies what command to run:

```
    test_description: 'test if cat command creates a file, leaving an existing file alone'
    command: 'echo This is some text. | cat > file_created_by_cat.txt'
```

Note that `test_description` is cosmetic only, but is worth specifying -- it will make `blackbox_tester` output easier to understand.

# Blackbox Tester runs a suite of tests

If you look inside the directory `bbtests_examples`, you'll see three folders, specifying three tests:

```
    0_cat_command_creates_a_file
    1_cat_output_to_stdout
    2_a_faulty_test_that_demonstrates_failure
```

This `bbtests_examples` folder comprises a *test suite*. When you run Blackbox Tester, you point it at a test suite directory, and all the
tests in that directory are run. The directory names don't matter; try to give them briefly descriptive names. It *is* recommended to prefix
your test suite directories with `bbtests_` in order to make it obvious which is a test suite.

For example, to run the `bbtests_examples` suite, you run the command:

```
    python3 blackbox_tester.py bbtests_examples
```

The output summarises the success or failure of every test in the suite:

```
    Cleaning artifacts from test suite dir: bbtests_examples
    
    Running test suite in dir: bbtests_examples
        
    Test 0 SUCCESS: "test if cat command creates a file, leaving an existing file alone" in dir "0_cat_command_creates_a_file"
    
    Test 1 SUCCESS: "test if echo emits to standard out" in dir "1_cat_output_to_stdout"
    
    Test 2 FAILED: "test if cat command creates a file, leaving an existing file alone, deliberate diffs" in dir "2_a_faulty_test_that_demonstrates_failure"
       * standard out didn't match the output given in stdout.txt.
       Between working and output, found orphan files/folders: ['orphan_in_input.txt']
    
    1 failures in 3 tests.
    
    Done.
```

Test 2 has deliberately been set up to demonstrate failure. When a test fails because the `input` folder contents don't match the `output`
folder contents, Blackbox Tester tells you about any problems it found and leaves a directory named `working` behind to help you debug the
issue. To see the differences, run your favourite diff tool on the directories `output/` and `working/` inside the failed test.

If you do that in this case, you'll see a file `orphan_in_input.txt` in the `input` folder that isn't present in the `output` folder.

Once you've corrected your tests (or fixed a bug in the tool you're testing!), and want to try the tests again, you might think to remove
the `working` folder(s). But there's no need to do this yourself: at the start of a test suite run, Blackbox Tester automatically removes
any `working` folders at the top level. If you want to clean these folders up without running the test suite again, run `python3 blackbox_tester.py --clean`.

# Testing standard output for a command

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

Should the `stdout.txt` contents not match what the command actually output, a file is saved that shows the actual
output: `stdout_working.txt`. You can this against your `stdout.txt` file.

Note that the `--clean` command also removes any `stdout_working.txt` files it finds, as well as the `working/` folders.

# Record mode

If you are confident that the tool you are testing is currently in a good working state, you can ask Blackbox Tester to create `output/`
and `stdout.txt` based on what your tool actually produces. To do this, run the tool with the `--record` flag:

```
    python3 blackbox_tester.py my_test_suite --record-stdout
```

# Checking in empty input/output directories using Git

You might want to use an empty `input` or `output` folder for a test. This is fine as far as Blackbox Tester is concerned, but if you're
using git for source control, you might have a problem because it doesn't 'see' empty folders. To get around this, put an empty
file `.blackbox_ignore_this_file` inside any empty folder. It's a file name that Blackbox Tester ignores, but it will allow git to see the
folder.


