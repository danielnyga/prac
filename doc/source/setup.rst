
Getting Started
===============

Compatibility
^^^^^^^^^^^^^

This software suite works out-of-the-box on Linux and Windows 64-bit machines.

Prerequisites
^^^^^^^^^^^^^

* Python 2.7 (or newer) with Tkinter installed.

    .. note::

      On Windows, Tkinter is usually shipped with Python.
      On Linux, the following packages should be installed (tested for Ubuntu)::

        sudo apt-get install python-tk python-scipy


* *PRACMLN*

    .. note::

      Get the *PRACMLN* sources on github: ::

        git clone https://github.com/danielnyga/pracmln.git

      and follow the installation instructions.



Installation
^^^^^^^^^^^^

As of Version 1.0.0, `PRAC` is shipped as a ``pip``-compliant package. For installing it, just checkout the code from::

  $> git clone https://github.com/danielnyga/prac.git

and install it with::

  $> python setup.py install

Example
^^^^^^^

As an example simply run the ``pracquery 'start the centrifuge.'`` from the console to run a complete inference using the provided modules.
By adding the parameter ``-i``, you can select the modules to be executed manually.