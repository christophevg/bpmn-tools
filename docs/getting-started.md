# Getting Started

PyPi template is hosted on PyPi, so...

```console
$ pip install pypi-template
```

## Use PyPi Template to Setup a New Package

```console
$ mkdir my-new-project
$ cd my-new-project
$ git init
$ pypi-template init
```

PyPi template will ask you to provide some basic information, which allows it to generate several files for your. All files that are written are reported. When ready, you have a fresh, customized source tree.

### Minimal Things to Edit

1. your package/module code ;-)

There is a placeholder top-level module folder, containing a dummy `module.py`, which you'll want to replace with your own actial code.

2. docs/

The `docs/` a copy of PyPi Templates own docs. These can be published to [ReadTheDocs](https://readthedocs.org) (see below). You can edit those files to accommodate your project.

> **NOTE regarding editing generated files:** you can re-run `pypi-template`, and it will regenerate files that have changed. This is useful if you have made changes to `.pypi-template`, which contains your provided values. In case of the actual documentation, which contains no variables, you can add these files to the `skip` variable in the `.pypi-template` file, to avoid them being overwritten.

## Use PyPi Template to Manage Your Package

Run `pypi-template edit all` in an existing PyPi Template package, it will again ask all questions, providing your with previously given answers, ready for editing.

```console
$ pypi-template edit all
A description for the package: A managed template repository for PyPi packages
Current classifiers:
- Environment :: Console
- Development Status :: 4 - Beta
- Intended Audience :: Developers
- Intended Audience :: System Administrators
- Topic :: Software Development
- License :: OSI Approved :: MIT License
- Programming Language :: Python
- Programming Language :: Python :: 3.7
Select classifiers: 
...
Your name: Christophe VG
backing up requirements.txt
writing requirements.txt
```

You can also simply a single variable in this way:

```console
$ pypi-template edit requires
Current requires:
- jinja2
- pyyaml
- prompt-toolkit
- colorama
Select requires:
```

To get a list of all available variables:

```console
$ pypi-template variables
a_description_for_the_package
classifiers
console_scripts
first_year_of_publication
github_account
github_repo_name
keywords_describing_the_package
license
package_module_name
package_name
package_tagline
package_title
requires
scripts
skip
your_author_name
your_email_address
your_full_name
your_name
classifiers
requires
console_scripts
scripts
skip
```

A few more command line arguments are available:

```console
% pypi-template --help
NAME
    pypi-template - allows you to manage your PyPi-published Python project.

SYNOPSIS
    pypi-template COMMAND

DESCRIPTION
    It is essentially a set of templates, which you can customise using several
    variables. The variables are stored in a file called `.pypi-template` in the 
    root of the project. You can edit this file directly, or use the `edit`
    command to do it in an interactive way.

    Several commands can be issues at the same time. These are chainable commands
    and are as such indicated in the help description of each command.

    To actually `apply` your changes, end your

COMMANDS
    COMMAND is one of the following:

     apply
       Apply the currently registered configuration.

     debug
       Don't actually do it, but tell what would have been done. (chainable)

     edit
       Edit a variable (or provide "all") and apply the change. (chainable)

     init
       Initialize a fresh project.

     path
       Set the path to the provided one. Defaults to the current working directory. (chainable)

     variables
       Returns a list of all available template variables you can edit.

     verbose
       Explain everything that is done. (chainable)

     version
       Output PyPiTemplate's version.

     yes
       Accept all previous values for variables. Only not yet initialized variables need handling. (chainable)
```

## Things to do

Besides providing you with a lot of boilerplate (configuration) files, there are also things to do...

The included `Makefile` offers several useful (IMHO) targets to perform some common tasks:

### Testing

A basic testing setup has been prepared. To run it locally, issue...

```console
% make test                
tox
GLOB sdist-make: /Users/xtof/Workspace/temp/setup.py
py3 inst-nodeps: /Users/xtof/Workspace/temp/.tox/.tmp/package/1/temp-pypi-template-0.0.1.zip
py3 installed: attrs==22.1.0,certifi==2022.6.15,charset-normalizer==2.1.0,coverage==6.4.3,coveralls==3.3.1,docopt==0.6.2,idna==3.3,iniconfig==1.1.1,packaging==21.3,pluggy==1.0.0,py==1.11.0,pyparsing==3.0.9,pytest==7.1.2,requests==2.28.1,temp-pypi-template @ file:///Users/xtof/Workspace/temp/.tox/.tmp/package/1/temp-pypi-template-0.0.1.zip,tomli==2.0.1,urllib3==1.26.11
py3 run-test-pre: PYTHONHASHSEED='1204045229'
py3 run-test: commands[0] | coverage run -m '--omit=*/.tox/*,*/distutils/*,tests/*' pytest
============================================== test session starts ===============================================
platform darwin -- Python 3.8.12, pytest-7.1.2, pluggy-1.0.0
cachedir: .tox/py3/.pytest_cache
rootdir: /Users/xtof/Workspace/temp, configfile: tox.ini, testpaths: tests
collected 1 item                                                                                                 

tests/test_example.py .                                                                                    [100%]

=============================================== 1 passed in 0.00s ================================================
____________________________________________________ summary _____________________________________________________
  py3: commands succeeded
  congratulations :)
```

Head over to [https://travis-ci.org](https://travis-ci.org) and register your project. A basic CI configuration is also provided.

Head over to [https://coveralls.io](https://coveralls.io) and register your project to consult your code coverage reporting.

### Generate/Publish Documentation

```console
$ make docs
...
```

This wil generate a HTML version of your `docs/` and open it in a browser.

If you want to publish your documentation (from the `docs/` folder) to e.g. [ReadTheDocs](https://readthedocs.org), import the repository over there also.

### Lint

```console
% make lint
...
```

> You will get some errors, since I prefer 2 spaces ;-) #sorry

### Publishing to PyPi

Head over to [https://test.pypi.org](https://test.pypi.org) and register for an account. Next simply issue...

```console
$ make publish-test
...
```

to publish your module to the test instance of PyPi.

or

```console
$ make publish
...
```

to publish your module to the main instance of [PyPi](https://pypi.org).
