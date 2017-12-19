PRAC -- Probabilistic Robot Action Cores
========================================

Knowledge about actions and objects is represented as Probabilistic Robot
Action Cores (PRAC), which can be thought of as generic event patterns that
enable a robot to infer important information that is missing in an original
natural-language instruction. PRAC models are represented in Markov Logic
Networks, a powerful knowlegde represenation formalism combining first-order
logic and probability theory.

  * Project Page: http://www.actioncores.org
  * Lead developer: Daniel Nyga (nyga@cs.uni-bremen.de)
  * Contributors: Mareike Picklum (mareikep@cs.uni-bremen.de)

Release notes
-------------

  * Version 1.0.0 (19.12.2017)
    * *Release*: Initial release


Documentation
-------------

PRAC comes with its own sphinx-based documentation. To build it, conduct the following actions:

    $ cd path/to/prac/doc
    $ make html

If you have installed Sphinx, the documentation should be build. Open
it in your favorite web browser:

    $ firefox _build/html/index.html

Sphinx can be installed with

    $ sudo pip install sphinx sphinxcontrib-bibtex
