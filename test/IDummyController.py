# -*- coding: utf-8 -*-
from abc import ABC

from pip_services3_commons.data import FilterParams, PagingParams, DataPage

from .Dummy import Dummy


class IDummyController(ABC):
    def get_page_by_filter(self, correlation_id: str, filter: FilterParams, paging: PagingParams) -> DataPage:
        raise NotImplementedError()

    def get_one_by_id(self, correlation_id: str, id: str) -> Dummy:
        raise NotImplementedError()

    def create(self, correlation_id: str, entity: Dummy) -> Dummy:
        raise NotImplementedError()

    def update(self, correlation_id: str, entity: Dummy) -> Dummy:
        raise NotImplementedError()

    def delete_by_id(self, correlation_id: str, id: str) -> Dummy:
        raise NotImplementedError()
