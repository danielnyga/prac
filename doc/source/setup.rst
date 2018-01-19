
Getting Started
===============

Compatibility
^^^^^^^^^^^^^

This software suite works out-of-the-box on Linux and Windows 64-bit machines.

Prerequisites
^^^^^^^^^^^^^

* Python 2.7/3.x (or newer) with Tkinter installed.

    .. note::

      On Windows, Tkinter is usually shipped with Python.
      On Linux, the following packages should be installed (tested for Ubuntu)::

        sudo apt-get install python-tk

* Java Version 8. On Ubuntu: ::

  $ sudo apt-get install openjdk-8-jdk


Installation
^^^^^^^^^^^^

As of Version 1.0.0, `PRAC` is shipped as a ``pip``-compliant package. For installing it, just checkout the code from::

  $ git clone https://github.com/danielnyga/prac.git
  $ cd prac

``pip``-Package
~~~~~~~~~~~~~~~
Install it with::

  $ python setup.py install


Repository-Version
~~~~~~~~~~~~~~~~~~

If you want to develop in `PRAC`, it makes sense to directly run the code from within the repository, without installing
using ``distutils``. To do that, a few more steps are required:

  1. Choose wether you want to use Python 2 or Python3. In the following, we assume Python 3 as the language of choice.

  2. Install the dependencies: ::

     $ pip install -r python3/requirements.txt

     Create the following link: ::

     $ ln -s ../../_version python3/prac/_version


Setup `PRAC` Database
~~~~~~~~~~~~~~~~~~~~~

You should have a MongoDB (version > 3.x) installation running on your local machine. On Ubuntu, you can install it
by ::

  $ sudo apt install mongodb

By default, it will grant local access to everyone without authentication. If your MongoDB setup requires authentication,
you can put a file named ``pracconf`` in your user data folder (``~/.local/share/prac/`` by default) with the following
format: ::

  [mongodb]
  host=localhost
  port=27017
  user=<username>
  password=<password>

`PRAC` comes with a very small initial database to showcase the core functionality. Download and install it with: ::

  $ cd data
  $ mongorestore --db prac howtos


Example
^^^^^^^
If you have installed the ``pip`` package, you can just run ::

    $ pracquery "start the centrifuge."

from the console
to run a complete inference using the provided modules. By adding the parameter ``-i``, you can select the modules to be executed manually.

If you run `PRAC` from the repository, you have to go to the ``python3`` or ``python2`` subdirectory, depending
on which Python version you chose. Then invoke the Python interpreter with the respective script: ::

    $ python pracquery.py "start the centrifuge."

