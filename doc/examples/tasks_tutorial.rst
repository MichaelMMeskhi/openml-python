.. note::
    :class: sphx-glr-download-link-note

    Click :ref:`here <sphx_glr_download_examples_tasks_tutorial.py>` to download the full example code
.. rst-class:: sphx-glr-example-title

.. _sphx_glr_examples_tasks_tutorial.py:


Tasks
=====

A tutorial on how to list and download tasks.


.. code-block:: default


    import openml
    import pandas as pd
    from pprint import pprint







Tasks are identified by IDs and can be accessed in two different ways:

1. In a list providing basic information on all tasks available on OpenML.
This function will not download the actual tasks, but will instead download
meta data that can be used to filter the tasks and retrieve a set of IDs.
We can filter this list, for example, we can only list tasks having a
special tag or only tasks for a specific target such as
*supervised classification*.

2. A single task by its ID. It contains all meta information, the target
metric, the splits and an iterator which can be used to access the
splits in a useful manner.

Listing tasks
^^^^^^^^^^^^^

We will start by simply listing only *supervised classification* tasks:


.. code-block:: default


    tasks = openml.tasks.list_tasks(task_type_id=1)







**openml.tasks.list_tasks()** returns a dictionary of dictionaries, we convert it into a
`pandas dataframe <http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html>`_
to have better visualization and easier access:


.. code-block:: default


    tasks = pd.DataFrame.from_dict(tasks, orient='index')
    print(tasks.columns)
    print("First 5 of %s tasks:" % len(tasks))
    pprint(tasks.head())





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Index(['tid', 'ttid', 'did', 'name', 'task_type', 'status',
           'estimation_procedure', 'source_data', 'target_feature',
           'MajorityClassSize', 'MaxNominalAttDistinctValues', 'MinorityClassSize',
           'NumberOfClasses', 'NumberOfFeatures', 'NumberOfInstances',
           'NumberOfInstancesWithMissingValues', 'NumberOfMissingValues',
           'NumberOfNumericFeatures', 'NumberOfSymbolicFeatures'],
          dtype='object')
    First 5 of 818 tasks:
       tid  ttid  ...  NumberOfNumericFeatures NumberOfSymbolicFeatures
    1    1     1  ...                      6.0                     33.0
    2    2     1  ...                      6.0                     33.0
    3    3     1  ...                      6.0                     33.0
    4    4     1  ...                      6.0                     33.0
    5    5     1  ...                      6.0                     33.0

    [5 rows x 19 columns]


We can filter the list of tasks to only contain datasets with more than
500 samples, but less than 1000 samples:


.. code-block:: default


    filtered_tasks = tasks.query('NumberOfInstances > 500 and NumberOfInstances < 1000')
    print(list(filtered_tasks.index))





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    [1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23, 24, 37, 38, 39, 40, 41, 42, 91, 92, 93, 94, 95, 96, 115, 116, 117, 118, 119, 120, 127, 128, 129, 130, 131, 132, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 181, 182, 183, 184, 185, 186, 193, 194, 195, 196, 197, 198, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 229, 230, 231, 232, 233, 234, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 307, 308, 309, 310, 311, 312, 379, 380, 381, 382, 383, 384, 391, 392, 393, 394, 395, 396, 433, 434, 435, 436, 437, 438, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 565, 566, 567, 568, 569, 570, 595, 596, 597, 598, 599, 600, 607, 608, 609, 610, 611, 612, 1069, 1072, 1075, 1084, 1088, 1090, 1093, 1094, 1099, 1101, 1103, 1104, 1105, 1107, 1109, 1110, 1111, 1120, 1132, 1134, 1141, 1154, 1155, 1163, 1168, 1206, 1209, 1212, 1221, 1225, 1227, 1230, 1231, 1236, 1238, 1240, 1241, 1242, 1244, 1246, 1247, 1248, 1257, 1267, 1269, 1276, 1289, 1290, 1298, 1303]



.. code-block:: default


    # Number of tasks
    print(len(filtered_tasks))





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    206


Then, we can further restrict the tasks to all have the same resampling strategy:


.. code-block:: default


    filtered_tasks = filtered_tasks.query('estimation_procedure == "10-fold Crossvalidation"')
    print(list(filtered_tasks.index))





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    [1, 19, 37, 91, 115, 127, 145, 151, 181, 193, 205, 211, 217, 229, 241, 247, 253, 307, 379, 391, 433, 511, 517, 565, 595, 607]



.. code-block:: default


    # Number of tasks
    print(len(filtered_tasks))





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    26


Resampling strategies can be found on the
`OpenML Website <http://www.openml.org/search?type=measure&q=estimation%20procedure>`_.

Similar to listing tasks by task type, we can list tasks by tags:


.. code-block:: default


    tasks = openml.tasks.list_tasks(tag='OpenML100')
    tasks = pd.DataFrame.from_dict(tasks, orient='index')
    print("First 5 of %s tasks:" % len(tasks))
    pprint(tasks.head())





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    First 5 of 100 tasks:
        tid  ttid  ...  NumberOfNumericFeatures NumberOfSymbolicFeatures
    1     1     1  ...                      6.0                     33.0
    7     7     1  ...                      0.0                     37.0
    13   13     1  ...                     16.0                      1.0
    19   19     1  ...                      4.0                      1.0
    25   25     1  ...                    216.0                      1.0

    [5 rows x 19 columns]


Furthermore, we can list tasks based on the dataset id:


.. code-block:: default


    tasks = openml.tasks.list_tasks(data_id=61)
    tasks = pd.DataFrame.from_dict(tasks, orient='index')
    print("First 5 of %s tasks:" % len(tasks))
    pprint(tasks.head())





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    First 5 of 11 tasks:
         tid  ttid  ...  NumberOfNumericFeatures NumberOfSymbolicFeatures
    361  361     1  ...                        7                        1
    362  362     1  ...                        7                        1
    363  363     1  ...                        7                        1
    364  364     1  ...                        7                        1
    365  365     1  ...                        7                        1

    [5 rows x 19 columns]


In addition, a size limit and an offset can be applied both separately and simultaneously:


.. code-block:: default


    tasks = openml.tasks.list_tasks(size=10, offset=50)
    tasks = pd.DataFrame.from_dict(tasks, orient='index')
    pprint(tasks)





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    tid  ttid  ...  NumberOfNumericFeatures NumberOfSymbolicFeatures
    51   51     1  ...                        6                        1
    52   52     1  ...                        6                        1
    53   53     1  ...                        6                        1
    54   54     1  ...                        6                        1
    55   55     1  ...                        0                      241
    56   56     1  ...                        0                      241
    57   57     1  ...                        0                      241
    58   58     1  ...                        0                      241
    59   59     1  ...                        0                      241
    60   60     1  ...                        0                      241

    [10 rows x 19 columns]


**OpenML 100**
is a curated list of 100 tasks to start using OpenML. They are all
supervised classification tasks with more than 500 instances and less than 50000
instances per task. To make things easier, the tasks do not contain highly
unbalanced data and sparse data. However, the tasks include missing values and
categorical features. You can find out more about the *OpenML 100* on
`the OpenML benchmarking page <https://www.openml.org/guide/benchmark>`_.

Finally, it is also possible to list all tasks on OpenML with:


.. code-block:: default

    tasks = openml.tasks.list_tasks()
    tasks = pd.DataFrame.from_dict(tasks, orient='index')
    print(len(tasks))





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    1305


Exercise
########

Search for the tasks on the 'eeg-eye-state' dataset.


.. code-block:: default


    tasks.query('name=="eeg-eye-state"')







Downloading tasks
^^^^^^^^^^^^^^^^^

We provide two functions to download tasks, one which downloads only a
single task by its ID, and one which takes a list of IDs and downloads
all of these tasks:


.. code-block:: default


    task_id = 1
    task = openml.tasks.get_task(task_id)







Properties of the task are stored as member variables:


.. code-block:: default


    pprint(vars(task))





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    {'class_labels': ['1', '2', '3', '4', '5', 'U'],
     'cost_matrix': None,
     'dataset_id': 1,
     'estimation_procedure': {'data_splits_url': 'https://test.openml.org/api_splits/get/1/Task_1_splits.arff',
                              'parameters': {'number_folds': '10',
                                             'number_repeats': '1',
                                             'percentage': '',
                                             'stratified_sampling': 'true'},
                              'type': 'crossvalidation'},
     'estimation_procedure_id': 1,
     'evaluation_measure': None,
     'split': None,
     'target_name': 'class',
     'task_id': 1,
     'task_type': 'Supervised Classification',
     'task_type_id': 1}


And:


.. code-block:: default


    ids = [1, 2, 19, 97, 403]
    tasks = openml.tasks.get_tasks(ids)
    pprint(tasks[0])




.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    <openml.tasks.task.OpenMLClassificationTask object at 0x116936198>



.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  23.174 seconds)


.. _sphx_glr_download_examples_tasks_tutorial.py:


.. only :: html

 .. container:: sphx-glr-footer
    :class: sphx-glr-footer-example



  .. container:: sphx-glr-download

     :download:`Download Python source code: tasks_tutorial.py <tasks_tutorial.py>`



  .. container:: sphx-glr-download

     :download:`Download Jupyter notebook: tasks_tutorial.ipynb <tasks_tutorial.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.readthedocs.io>`_
