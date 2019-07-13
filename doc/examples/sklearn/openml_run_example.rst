.. note::
    :class: sphx-glr-download-link-note

    Click :ref:`here <sphx_glr_download_examples_sklearn_openml_run_example.py>` to download the full example code
.. rst-class:: sphx-glr-example-title

.. _sphx_glr_examples_sklearn_openml_run_example.py:


OpenML Run Example
==================

An example of an automated machine learning experiment.


.. code-block:: default

    import openml
    from sklearn import tree, preprocessing, pipeline

    # Uncomment and set your OpenML key. Don't share your key with others.
    # openml.config.apikey = 'YOURKEY'

    # Define a scikit-learn pipeline
    clf = pipeline.Pipeline(
        steps=[
            ('imputer', preprocessing.Imputer()),
            ('estimator', tree.DecisionTreeClassifier())
        ]
    )






Download the OpenML task for the german credit card dataset.


.. code-block:: default

    task = openml.tasks.get_task(97)






Run the scikit-learn model on the task (requires an API key).


.. code-block:: default

    run = openml.runs.run_model_on_task(clf, task)
    # Publish the experiment on OpenML (optional, requires an API key).
    run.publish()

    print('URL for run: %s/run/%d' % (openml.config.server, run.run_id))




.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    URL for run: https://test.openml.org/api/v1/xml/run/4054



.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  10.099 seconds)


.. _sphx_glr_download_examples_sklearn_openml_run_example.py:


.. only :: html

 .. container:: sphx-glr-footer
    :class: sphx-glr-footer-example



  .. container:: sphx-glr-download

     :download:`Download Python source code: openml_run_example.py <openml_run_example.py>`



  .. container:: sphx-glr-download

     :download:`Download Jupyter notebook: openml_run_example.ipynb <openml_run_example.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.readthedocs.io>`_