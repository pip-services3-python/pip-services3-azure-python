# -*- coding: utf-8 -*-
import json
from typing import Optional

import azure.functions as func
from pip_services3_commons.commands import CommandSet, Command, ICommand
from pip_services3_commons.convert import TypeCode
from pip_services3_commons.data import FilterParams, DataPage, PagingParams
from pip_services3_commons.run import Parameters
from pip_services3_commons.validate import ObjectSchema, FilterParamsSchema, PagingParamsSchema

from test.Dummy import Dummy
from test.DummySchema import DummySchema
from test.IDummyController import IDummyController


class DummyCommandSet(CommandSet):
    __controller: IDummyController

    def __init__(self, controller: IDummyController):
        super().__init__()

        self.__controller = controller

        self.__headers: dict = {'Content-Type': 'application/json'}

        self.add_command(self.__make_get_page_by_filter_command())
        self.add_command(self.__make_get_one_by_id_command())
        self.add_command(self.__make_create_command())
        self.add_command(self.__make_update_command())
        self.add_command(self.__make_delete_by_id_command())

    def __make_get_page_by_filter_command(self) -> ICommand:
        def handler(correlation_id: Optional[str], args: Parameters) -> func.HttpResponse:
            filter = FilterParams.from_value(args.get("filter"))
            paging = PagingParams.from_value(args.get('paging'))

            page = self.__controller.get_page_by_filter(correlation_id, filter, paging)
            page.data = list(map(lambda d: json.dumps(d.to_dict()), page.data))

            return func.HttpResponse(body=json.dumps(page.to_json()), headers=self.__headers)

        return Command(
            'get_dummies',
            ObjectSchema(True)
                .with_optional_property('filter', FilterParamsSchema())
                .with_optional_property('paging', PagingParamsSchema()),
            handler
        )

    def __make_get_one_by_id_command(self) -> ICommand:
        def handler(correlation_id: Optional[str], args: Parameters) -> func.HttpResponse:
            id = args.get_as_string('dummy_id')
            dummy = self.__controller.get_one_by_id(correlation_id, id)

            json_dummy = None if not dummy else json.dumps(dummy.to_dict())
            return func.HttpResponse(body=json_dummy, headers=self.__headers)

        return Command(
            'get_dummy_by_id',
            ObjectSchema(True).with_required_property('dummy_id', TypeCode.String),
            handler
        )

    def __make_create_command(self) -> ICommand:
        def handler(correlation_id: Optional[str], args: Parameters) -> func.HttpResponse:
            entity = args.get('dummy')
            dummy = self.__controller.create(correlation_id, Dummy(**entity))
            return func.HttpResponse(body=json.dumps(dummy.to_dict()), headers=self.__headers)

        return Command(
            'create_dummy',
            ObjectSchema(True).with_required_property('dummy', DummySchema()),
            handler
        )

    def __make_update_command(self) -> ICommand:
        def handler(correlation_id: Optional[str], args: Parameters) -> func.HttpResponse:
            entity = args.get('dummy')
            dummy = self.__controller.update(correlation_id, Dummy(**entity))
            return func.HttpResponse(body=json.dumps(dummy.to_dict()), headers=self.__headers)

        return Command(
            'update_dummy',
            ObjectSchema(True).with_required_property('dummy', DummySchema()),
            handler
        )

    def __make_delete_by_id_command(self) -> ICommand:
        def handler(correlation_id: Optional[str], args: Parameters) -> func.HttpResponse:
            id = args.get('dummy_id')
            dummy = self.__controller.delete_by_id(correlation_id, id)
            return func.HttpResponse(body=json.dumps(dummy.to_dict()), headers=self.__headers)

        return Command(
            "delete_dummy",
            ObjectSchema(True).with_required_property('dummy_id', TypeCode.String),
            handler
        )
