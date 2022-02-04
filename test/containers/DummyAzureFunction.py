# -*- coding: utf-8 -*-
import json
from copy import deepcopy

import azure.functions as func
from pip_services3_commons.convert import TypeCode
from pip_services3_commons.data import DataPage, FilterParams, PagingParams
from pip_services3_commons.refer import Descriptor, IReferences
from pip_services3_commons.validate import ObjectSchema, FilterParamsSchema, PagingParamsSchema

from pip_services3_azure.containers import AzureFunction
from test.Dummy import Dummy
from test.DummyFactory import DummyFactory
from test.DummySchema import DummySchema
from test.IDummyController import IDummyController


class DummyAzureFunction(AzureFunction):
    def __init__(self):
        super(DummyAzureFunction, self).__init__("dummy", "Dummy lambda function")
        self._dependency_resolver.put('controller',
                                      Descriptor('pip-services-dummies', 'controller', 'default', '*', '*'))
        self._factories.add(DummyFactory())

        self._controller: IDummyController = None

    def set_references(self, references: IReferences):
        super(DummyAzureFunction, self).set_references(references)
        self._controller = self._dependency_resolver.get_one_required('controller')

    def _get_body_data(self, context: func.HttpRequest) -> dict:
        params = deepcopy(context.get_body())

        if params:
            params = json.loads(params)
        return params

    def __get_page_by_filter(self, params: func.HttpRequest) -> DataPage:
        params = self._get_body_data(params)
        return self._controller.get_page_by_filter(
            params.get('correlation_id'),
            FilterParams(params.get('filter')),
            PagingParams(params.get('paging'))
        )

    def __get_one_by_id(self, params: func.HttpRequest) -> Dummy:
        params = self._get_body_data(params)
        return self._controller.get_one_by_id(
            params.get('correlation_id'),
            params.get('dummy_id'),
        )

    def __create(self, params: func.HttpRequest) -> Dummy:
        params = self._get_body_data(params)
        return self._controller.create(
            params.get('correlation_id'),
            Dummy(**params.get('dummy')),
        )

    def __update(self, params: func.HttpRequest) -> Dummy:
        params = self._get_body_data(params)
        return self._controller.update(
            params.get('correlation_id'),
            Dummy(**params.get('dummy')),
        )

    def __delete_by_id(self, params: func.HttpRequest) -> Dummy:
        params = self._get_body_data(params)
        return self._controller.delete_by_id(
            params.get('correlation_id'),
            params.get('dummy_id'),
        )

    def register(self):
        self._register_action(
            'get_dummies',
            ObjectSchema(True)
                .with_optional_property("filter", FilterParamsSchema())
                .with_optional_property("paging", PagingParamsSchema()),
            self.__get_page_by_filter)

        self._register_action(
            'get_dummy_by_id',
            ObjectSchema(True)
                .with_optional_property("dummy_id", TypeCode.String),
            self.__get_one_by_id)

        self._register_action(
            'create_dummy',
            ObjectSchema(True)
                .with_required_property("dummy", DummySchema()),
            self.__create)

        self._register_action(
            'update_dummy',
            ObjectSchema(True)
                .with_required_property("dummy", DummySchema()),
            self.__update)

        self._register_action(
            'delete_dummy',
            ObjectSchema(True)
                .with_optional_property("dummy_id", TypeCode.String),
            self.__delete_by_id)
