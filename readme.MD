# Blackbox command tester

This is a proof-of-concept.

It's a tool for verifying input files versus output files for a command line tools.

As a very simple example, image you want to verify that the `cat` command is able to write to a file (and also that it will not change a file with a different name that already exists). The directory `examples_tests/1` demonstrates the setup to do this:


```
    0_cat_command_creates_a_file/
      input/
        existing_file.txt
      output/
        existing_file.txt
        file_created_by_cat.txt
      config.yml      
```

This `0_cat_command_creates_a_file` directory describes a single test.

`Blackox_tester` works by running the command (specified in `config.yml`) inside the `input` folder. It then verifies that the contents of the folder match what is in `output`.

Here's the contents of config.yml:

```
    test_description: 'test if cat command creates a file, leaving an existing file alone'
    command: 'echo This is some text. | cat > file_created_by_cat.txt'
```

Note that `test_description` is cosmetic only, but is worth specifying -- it will make `blackbox_tester` output easier to understand.
