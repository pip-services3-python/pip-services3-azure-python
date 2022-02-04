# -*- coding: utf-8 -*-
import json
from copy import deepcopy
from typing import Any

import azure.functions as func
from pip_services3_commons.convert import TypeCode
from pip_services3_commons.data import PagingParams, FilterParams
from pip_services3_commons.refer import Descriptor, IReferences
from pip_services3_commons.validate import ObjectSchema, PagingParamsSchema, FilterParamsSchema

from pip_services3_azure.services.AzureFunctionService import AzureFunctionService
from test.AzureFunctionRequestSchema import AzureFunctionRequestSchema
from test.Dummy import Dummy
from test.DummySchema import DummySchema
from test.IDummyController import IDummyController


class DummyAzureFunctionService(AzureFunctionService):

    def __init__(self):
        super(DummyAzureFunctionService, self).__init__('dummies')

        self.__controller: IDummyController = None
        self.__headers: dict = {'Content-Type': 'application/json'}

        self._dependency_resolver.put('controller',
                                      Descriptor('pip-services-dummies', 'controller', 'default', '*', '*'))

    def _get_body_data(self, context: func.HttpRequest) -> dict:
        params = deepcopy(context.get_body())

        if params:
            params = json.loads(params)
        return params

    def set_references(self, references: IReferences):
        super(DummyAzureFunctionService, self).set_references(references)
        self.__controller = self._dependency_resolver.get_one_required('controller')

    def __get_page_by_filter(self, params: func.HttpRequest) -> Any:
        params = self._get_body_data(params)
        page = self.__controller.get_page_by_filter(
            params.get('correlation_id'),
            FilterParams(params.get('filter')),
            PagingParams(params.get('paging'))
        )

        return {'body': page, 'headers': self.__headers}

    def __get_one_by_id(self, params: func.HttpRequest) -> Any:
        params = self._get_body_data(params)
        dummy = self.__controller.get_one_by_id(
            params.get('correlation_id'),
            params.get('dummy_id')
        )
        return {'body': None if not dummy else dummy.to_dict(), 'headers': self.__headers}

    def __create(self, params: func.HttpRequest) -> Any:
        params = self._get_body_data(params)
        dummy = self.__controller.create(
            params.get('correlation_id'),
            Dummy(**params.get('dummy'))
        )
        return {'body': dummy.to_dict(), 'headers': self.__headers}

    def __update(self, params: func.HttpRequest) -> Any:
        params = self._get_body_data(params)
        dummy = self.__controller.update(
            params.get('correlation_id'),
            Dummy(**params.get('dummy'))
        )
        return {'body': dummy.to_dict(), 'headers': self.__headers}

    def __delete_by_id(self, params: func.HttpRequest) -> Any:
        params = self._get_body_data(params)
        dummy = self.__controller.delete_by_id(
            params.get('correlation_id'),
            params.get('dummy_id'),
        )
        return {'body': dummy.to_dict(), 'headers': self.__headers}

    def register(self):
        self._register_action(
            'get_dummies',
            AzureFunctionRequestSchema()
                .with_optional_property('body',
                                        ObjectSchema(True)
                                        .with_optional_property("filter", FilterParamsSchema())
                                        .with_optional_property("paging", PagingParamsSchema())
                                        )
            , self.__get_page_by_filter
        )

        self._register_action(
            'get_dummy_by_id',
            AzureFunctionRequestSchema()
                .with_optional_property("body",
                                        ObjectSchema(True)
                                        .with_optional_property("dummy_id", TypeCode.String)
                                        ),
            self.__get_one_by_id)

        self._register_action(
            'create_dummy',
            AzureFunctionRequestSchema()
                .with_optional_property("body",
                                        ObjectSchema(True)
                                        .with_optional_property("dummy", DummySchema())
                                        ),
            self.__create)

        self._register_action(
            'update_dummy',
            AzureFunctionRequestSchema()
                .with_optional_property("body",
                                        ObjectSchema(True)
                                        .with_optional_property("dummy", DummySchema())
                                        ),
            self.__update)

        self._register_action(
            'delete_dummy',
            AzureFunctionRequestSchema()
                .with_optional_property("body",
                                        ObjectSchema(True)
                                        .with_optional_property("dummy_id", TypeCode.String)
                                        ),
            self.__delete_by_id)
