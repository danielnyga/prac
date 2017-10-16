
Getting Started
===============

Compatibility
^^^^^^^^^^^^^

This software suite works out-of-the-box on Linux and Windows 64-bit machines.

Source Code
^^^^^^^^^^^

The source code is publicly available under BSD License: ::

  git clone https://github.com/danielnyga/prac.git


Prerequisites
^^^^^^^^^^^^^

* Python 2.7 (or newer) with Tkinter installed.

    .. note::

      On Windows, Tkinter is usually shipped with Python.
      On Linux, the following packages should be installed (tested for Ubuntu)::

        sudo apt-get install python-tk python-scipy

  You will also need the following python packages: `pyparsing`, `tabulate`, `nltk`, `jpype`, `graphviz`, `beautifulsoup4`, `lxml` and `psutil`. You can install them via ::

    sudo pip install pyparsing tabulate psutil==0.4.1 nltk jpype graphviz beautifulsoup4 lxml

* *PRACMLN*

    .. note::

      Get the *PRACMLN* sources on github: ::

        git clone https://github.com/danielnyga/pracmln.git

      and follow the installation instructions.



Installation
^^^^^^^^^^^^

#. Generating Apps

   Run the ``setup.py`` script: ::

    python setup.py

   This will generate a number of shell scripts (or batch files for Windows) in the ``./apps`` directory.

#. Setting up your Environment

   ``setup.py`` will report how to set up your environment.

   To temporarily configure your environment, you can simply use the ``env`` script/batch
   file it creates to get everything set up.
   If you use `pracmln` a lot, consider adding the ``./apps`` directory to your ``PATH`` variable
   or copy the files created therein to an appropriate directory.
   If you intend to make use of scripting, also set ``PYTHONPATH`` as described
   by ``setup``.

Example
^^^^^^^

As an example simply run the ``pracquery 'start the centrifuge.'`` from the console to run a complete inference using the provided modules.
By adding the parameter ``-i``, you can select the modules to be executed manually.