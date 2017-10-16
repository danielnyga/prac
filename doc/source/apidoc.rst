
API-Specification
=================

`prac` comes with an easy-to-use API, which lets you use the
modules provided by `prac` of which each solves an own inference task conveniently
in your own applications.


PRACModules
^^^^^^^^^^^

A PRACModule is represented by an instance of the class
:class:`prac.core.base.PRACModule`. Each module provides a `predicates.mln` file
containing the predicate declarations for the MLN of the respective module and
a `pracmodule.yaml` file specifying module properties such as its name and a
description, as well as dependencies to other PRACModules, the names of the
module's class and a file (usually `predicates.mln`) containing the predicate
declarations for the related MLN. It also specifies which project file
contains the default project to be loaded for this module. This file will be
processed during initialization of the *PRAC* reasoning system.


PRAC
^^^^

The PRAC reasoning system is represented by an instance of the class
:class:`prac.core.base.PRAC`. This class encapsulates information about
the modules of the *PRAC* pipeline and the ontology used for the inference.
It also provides a method :attr:`run` to execute a module of the *PRAC*
pipeline.

.. automethod:: prac.core.base.PRAC.run


PRACInference
^^^^^^^^^^^^^

An instance of the class :class:`prac.core.inference.PRACInference` represents
an inference chain in *PRAC* which is initialized with a reference to an
instance of the *PRAC* reasoning system (:class:`prac.core.base.PRAC`) and a
list of natural-language sentences subject to inference.

The method :attr:`next_module` returns the name of the next module to be
executed according to the predefined *PRAC* pipeline. An instance of this
module can then be created and executed: ::

    >>> modulename = inference.next_module()
    >>> module = prac.module(modulename)
    >>> prac.run(inference, module)

.. automethod:: prac.core.inference.PRACInference.next_module

PRACInferenceStep
^^^^^^^^^^^^^^^^^

A PRACInferenceStep instance encapsulates a single inference step in the
*PRAC* pipeline. It consists of `n` input databases and `m` output databases.
Initialize an instance of the class :class:`prac.core.inference.PRACInference`
with a reference to the PRACInference object, a reference to the PRACModule
performing this inference step and list of databases taken as inputs.


WordNet
^^^^^^^

The class :class:`prac.core.wordnet.WordNet` is a wrapper class for
`Wordnet <http://wordnet.princeton.edu/>`_, which may be initialized with
some WordNet concepts spanning an initial, collapsed concept taxonomy.
The methods :attr:`synsets` and :attr:`synset` allow creating WordNet synsets
from strings and perform a number of preprocessing steps to generate temporary
WordnetConcepts for numbers that are not contained in the WordNet ontology.
The method :attr:`similarity` will calculate the WUP- or path-similarity
provided by WordNet after preprocessing the synsets. In particular, if at least
one of the synsets is an adjective, this preprocessing includes looking up
the synset in predefined similarity tables for colors, shapes and sizes and
numbers not contained in the original ontology. Otherwise the derivationally
related noun form of the adjective is retrieved from WordNet and used for the
similarity calculation.

.. automethod:: prac.core.wordnet.WordNet.synsets
.. automethod:: prac.core.wordnet.WordNet.synset
.. automethod:: prac.core.wordnet.WordNet.similarity


Reasoning
^^^^^^^^^

Once a PRAC- and a PRACInference instance have been initialized, we can
run the *PRAC* pipeline.

    >>> prac = PRAC()
    >>> inference = PRACInference(prac, sentences)
    >>> while inference.next_module() != None and not is_inference_process_aborted:
    >>>     modulename = inference.next_module()
    >>>     module = prac.module(modulename)
    >>>     prac.run(inference, module)




    >>> prac = PRAC()
    >>> inference = PRACInference(prac, sentences)
    >>> while inference.next_module() != None and not is_inference_process_aborted:
    >>>     modulename = inference.next_module()
    >>>     module = prac.module(modulename)
    >>>     prac.run(inference, module)




    >>> prac = PRAC()
    >>> inference = PRACInference(prac, sentences)
    >>> while inference.next_module() != None and not is_inference_process_aborted:
    >>>     modulename = inference.next_module()
    >>>     module = prac.module(modulename)
    >>>     prac.run(inference, module)


API Reference
^^^^^^^^^^^^^

.. automodule:: prac.core.base
    :members: PRAC, PRACModule


.. automodule:: prac.core.wordnet
    :members: WordNet


.. automodule:: prac.core.inference
    :members: PRACInference, PRACInferenceStep
