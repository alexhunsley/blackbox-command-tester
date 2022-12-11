# Blackbox command tester

This is a proof-of-concept.

It's a tool for verifying input files versus output files for a command line tools.

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

