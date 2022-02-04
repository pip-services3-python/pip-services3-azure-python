# -*- coding: utf-8 -*-
from abc import ABC
from typing import Optional

from pip_services3_commons.data import PagingParams, DataPage, FilterParams

from test.Dummy import Dummy


class IDummyClient(ABC):
    def get_dummies(self, correlation_id: Optional[str], filter: FilterParams, paging: PagingParams) -> DataPage:
        raise NotImplementedError()

    def get_dummy_by_id(self, correlation_id: Optional[str], id: str) -> Dummy:
        raise NotImplementedError()

    def create_dummy(self, correlation_id: Optional[str], entity: Dummy) -> Dummy:
        raise NotImplementedError()

    def update_dummy(self, correlation_id: Optional[str], entity: Dummy) -> Dummy:
        raise NotImplementedError()

    def delete__dummy(self, correlation_id: Optional[str], id: str) -> Dummy:
        raise NotImplementedError()
