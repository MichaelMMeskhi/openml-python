import io
import os
from collections import OrderedDict
from typing import Union, Tuple, Dict, List, Optional
from abc import ABC
from warnings import warn

import xmltodict
import numpy as np

from .. import datasets
from .split import OpenMLSplit
import openml._api_calls
from ..utils import _create_cache_directory_for_id, _tag_entity


class OpenMLTask(ABC):
    def __init__(
            self,
            task_id: Optional[Union[int, str]],
            task_type_id: Union[int, str],
            task_type: str,
            data_set_id: Union[int, str],
            estimation_procedure_id: int = 1,
            estimation_procedure_type: Optional[str] = None,
            estimation_parameters: Optional[Dict[str, str]] = None,
            evaluation_measure: Optional[str] = None,
            data_splits_url: Optional[str] = None,
    ):

        self.task_id = int(task_id) if task_id is not None else None
        self.task_type_id = int(task_type_id)
        self.task_type = task_type
        self.dataset_id = int(data_set_id)
        self.evaluation_measure = evaluation_measure
        self.estimation_procedure = dict()  # type: Dict[str, Optional[Union[str, Dict]]] # noqa E501
        self.estimation_procedure["type"] = estimation_procedure_type
        self.estimation_procedure["parameters"] = estimation_parameters
        self.estimation_procedure["data_splits_url"] = data_splits_url
        self.estimation_procedure_id = estimation_procedure_id
        self.split = None  # type: Optional[OpenMLSplit]

    def get_dataset(self) -> datasets.OpenMLDataset:
        """Download dataset associated with task"""
        return datasets.get_dataset(self.dataset_id)

    def get_train_test_split_indices(
            self,
            fold: int = 0,
            repeat: int = 0,
            sample: int = 0,
    ) -> Tuple[np.ndarray, np.ndarray]:

        # Replace with retrieve from cache
        if self.split is None:
            self.split = self.download_split()

        train_indices, test_indices = self.split.get(
            repeat=repeat,
            fold=fold,
            sample=sample,
        )
        return train_indices, test_indices

    def _download_split(self, cache_file: str):
        try:
            with io.open(cache_file, encoding='utf8'):
                pass
        except (OSError, IOError):
            split_url = self.estimation_procedure["data_splits_url"]
            split_arff = openml._api_calls._read_url(split_url,
                                                     request_method='get')

            with io.open(cache_file, "w", encoding='utf8') as fh:
                fh.write(split_arff)
            del split_arff

    def download_split(self) -> OpenMLSplit:
        """Download the OpenML split for a given task.
        """
        cached_split_file = os.path.join(
            _create_cache_directory_for_id('tasks', self.task_id),
            "datasplits.arff",
        )

        try:
            split = OpenMLSplit._from_arff_file(cached_split_file)
        except (OSError, IOError):
            # Next, download and cache the associated split file
            self._download_split(cached_split_file)
            split = OpenMLSplit._from_arff_file(cached_split_file)

        return split

    def get_split_dimensions(self) -> Tuple[int, int, int]:

        if self.split is None:
            self.split = self.download_split()

        return self.split.repeats, self.split.folds, self.split.samples

    def push_tag(self, tag: str):
        """Annotates this task with a tag on the server.

        Parameters
        ----------
        tag : str
            Tag to attach to the task.
        """
        _tag_entity('task', self.task_id, tag)

    def remove_tag(self, tag: str):
        """Removes a tag from this task on the server.

        Parameters
        ----------
        tag : str
            Tag to attach to the task.
        """
        _tag_entity('task', self.task_id, tag, untag=True)

    def _to_dict(self) -> dict:

        task_container = OrderedDict()  # type: OrderedDict[str, OrderedDict]
        task_dict = OrderedDict([
            ('@xmlns:oml', 'http://openml.org/openml')
        ])  # type: OrderedDict[str, Union[Union[List, str], int]]

        task_container['oml:task_inputs'] = task_dict
        task_dict['oml:task_type_id'] = self.task_type_id

        # having task_inputs and adding a type annotation
        # solves wrong warnings
        task_inputs = [
            OrderedDict([
                ('@name', 'source_data'),
                ('#text', str(self.dataset_id))
            ]),
            OrderedDict([
                ('@name', 'estimation_procedure'),
                ('#text', str(self.estimation_procedure_id))
            ])
        ]  # type: List[OrderedDict]

        if self.evaluation_measure is not None:
            task_inputs.append(
                OrderedDict([
                    ('@name', 'evaluation_measures'),
                    ('#text', self.evaluation_measure)
                ])
            )

        task_dict['oml:input'] = task_inputs

        return task_container

    def _to_xml(self) -> str:
        """Generate xml representation of self for upload to server.

        Returns
        -------
        str
            Task represented as XML string.
        """
        task_dict = self._to_dict()
        task_xml = xmltodict.unparse(task_dict, pretty=True)

        # A task may not be uploaded with the xml encoding specification:
        # <?xml version="1.0" encoding="utf-8"?>
        task_xml = task_xml.split('\n', 1)[-1]

        return task_xml

    def publish(self) -> int:
        """Publish task to OpenML server.

        Returns
        -------
        task_id: int
            Returns the id of the uploaded task
            if successful.

        """

        xml_description = self._to_xml()

        file_elements = {'description': xml_description}

        return_value = openml._api_calls._perform_api_call(
            "task/",
            'post',
            file_elements=file_elements,
        )

        task_id = int(xmltodict.parse(return_value)['oml:upload_task']['oml:id'])

        return task_id


class OpenMLSupervisedTask(OpenMLTask, ABC):
    def __init__(
            self,
            task_type_id: Union[int, str],
            task_type: str,
            data_set_id: int,
            target_name: str,
            estimation_procedure_id: int = 1,
            estimation_procedure_type: Optional[str] = None,
            estimation_parameters: Optional[Dict[str, str]] = None,
            evaluation_measure: Optional[str] = None,
            data_splits_url: Optional[str] = None,
            task_id: Optional[Union[int, str]] = None,
    ):
        super(OpenMLSupervisedTask, self).__init__(
            task_id=task_id,
            task_type_id=task_type_id,
            task_type=task_type,
            data_set_id=data_set_id,
            estimation_procedure_id=estimation_procedure_id,
            estimation_procedure_type=estimation_procedure_type,
            estimation_parameters=estimation_parameters,
            evaluation_measure=evaluation_measure,
            data_splits_url=data_splits_url,
        )

        self.target_name = target_name

    def get_X_and_y(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get data associated with the current task.

        Returns
        -------
        tuple - X and y

        """
        dataset = self.get_dataset()
        if self.task_type_id not in (1, 2, 3):
            raise NotImplementedError(self.task_type)
        X_and_y = dataset.get_data(
            dataset_format='array', target=self.target_name
        )
        return X_and_y

    def _to_dict(self) -> Dict[str, OrderedDict]:

        task_container = super(OpenMLSupervisedTask, self)._to_dict()
        task_dict = task_container['oml:task_inputs']

        task_dict['oml:input'].append(
            OrderedDict([
                ('@name', 'target_feature'),
                ('#text', self.target_name)
            ])
        )

        return task_container

    @property
    def estimation_parameters(self):

        warn(
            "The estimation_parameters attribute will be "
            "deprecated in the future, please use "
            "estimation_procedure['parameters'] instead",
            PendingDeprecationWarning
        )
        return self.estimation_procedure["parameters"]

    @estimation_parameters.setter
    def estimation_parameters(self, est_parameters):

        self.estimation_procedure["parameters"] = est_parameters


class OpenMLClassificationTask(OpenMLSupervisedTask):
    def __init__(
            self,
            task_type_id: Union[int, str],
            task_type: str,
            data_set_id: int,
            target_name: str,
            estimation_procedure_id: int = 1,
            estimation_procedure_type: Optional[str] = None,
            estimation_parameters: Optional[Dict[str, str]] = None,
            evaluation_measure: Optional[str] = None,
            data_splits_url: Optional[str] = None,
            task_id: Optional[Union[int, str]] = None,
            class_labels: Optional[List[str]] = None,
            cost_matrix: Optional[np.ndarray] = None,
    ):

        super(OpenMLClassificationTask, self).__init__(
            task_id=task_id,
            task_type_id=task_type_id,
            task_type=task_type,
            data_set_id=data_set_id,
            estimation_procedure_id=estimation_procedure_id,
            estimation_procedure_type=estimation_procedure_type,
            estimation_parameters=estimation_parameters,
            evaluation_measure=evaluation_measure,
            target_name=target_name,
            data_splits_url=data_splits_url,
        )
        self.class_labels = class_labels
        self.cost_matrix = cost_matrix

        if cost_matrix is not None:
            raise NotImplementedError("Costmatrix")


class OpenMLRegressionTask(OpenMLSupervisedTask):
    def __init__(
            self,
            task_type_id: Union[int, str],
            task_type: str,
            data_set_id: int,
            target_name: str,
            estimation_procedure_id: int = 7,
            estimation_procedure_type: Optional[str] = None,
            estimation_parameters: Optional[Dict[str, str]] = None,
            data_splits_url: Optional[str] = None,
            task_id: Optional[Union[int, str]] = None,
            evaluation_measure: Optional[str] = None,
    ):
        super(OpenMLRegressionTask, self).__init__(
            task_id=task_id,
            task_type_id=task_type_id,
            task_type=task_type,
            data_set_id=data_set_id,
            estimation_procedure_id=estimation_procedure_id,
            estimation_procedure_type=estimation_procedure_type,
            estimation_parameters=estimation_parameters,
            evaluation_measure=evaluation_measure,
            target_name=target_name,
            data_splits_url=data_splits_url,
        )


class OpenMLClusteringTask(OpenMLTask):
    def __init__(
            self,
            task_type_id: Union[int, str],
            task_type: str,
            data_set_id: int,
            estimation_procedure_id: int = 17,
            task_id: Optional[Union[int, str]] = None,
            estimation_procedure_type: Optional[str] = None,
            estimation_parameters: Optional[Dict[str, str]] = None,
            data_splits_url: Optional[str] = None,
            evaluation_measure: Optional[str] = None,
            target_name: Optional[str] = None,
    ):
        super(OpenMLClusteringTask, self).__init__(
            task_id=task_id,
            task_type_id=task_type_id,
            task_type=task_type,
            data_set_id=data_set_id,
            evaluation_measure=evaluation_measure,
            estimation_procedure_id=estimation_procedure_id,
            estimation_procedure_type=estimation_procedure_type,
            estimation_parameters=estimation_parameters,
            data_splits_url=data_splits_url,
        )

        self.target_name = target_name

    def _to_dict(self) -> Dict[str, OrderedDict]:

        task_container = super(OpenMLClusteringTask, self)._to_dict()

        # Right now not supported as a feture
        # Uncomment if it is supported on the server
        # in the future.
        # https://github.com/openml/OpenML/issues/925
        '''
        task_dict = task_container['oml:task_inputs']        
        if self.target_name is not None:
            task_dict['oml:input'].append(
                OrderedDict([
                    ('@name', 'target_feature'),
                    ('#text', self.target_name)
                ])
            )
        '''
        return task_container


class OpenMLLearningCurveTask(OpenMLClassificationTask):
    def __init__(
            self,
            task_type_id: Union[int, str],
            task_type: str,
            data_set_id: int,
            target_name: str,
            estimation_procedure_id: int = 13,
            estimation_procedure_type: Optional[str] = None,
            estimation_parameters: Optional[Dict[str, str]] = None,
            data_splits_url: Optional[str] = None,
            task_id: Optional[Union[int, str]] = None,
            evaluation_measure: Optional[str] = None,
            class_labels: Optional[List[str]] = None,
            cost_matrix: Optional[np.ndarray] = None,
    ):
        super(OpenMLLearningCurveTask, self).__init__(
            task_id=task_id,
            task_type_id=task_type_id,
            task_type=task_type,
            data_set_id=data_set_id,
            estimation_procedure_id=estimation_procedure_id,
            estimation_procedure_type=estimation_procedure_type,
            estimation_parameters=estimation_parameters,
            evaluation_measure=evaluation_measure,
            target_name=target_name,
            data_splits_url=data_splits_url,
            class_labels=class_labels,
            cost_matrix=cost_matrix,
        )


class TaskTypeEnum(object):
    SUPERVISED_CLASSIFICATION = 1
    SUPERVISED_REGRESSION = 2
    LEARNING_CURVE = 3
    SUPERVISED_DATASTREAM_CLASSIFICATION = 4
    CLUSTERING = 5
    MACHINE_LEARNING_CHALLENGE = 6
    SURVIVAL_ANALYSIS = 7
    SUBGROUP_DISCOVERY = 8
