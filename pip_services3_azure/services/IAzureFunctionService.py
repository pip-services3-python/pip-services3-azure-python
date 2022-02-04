# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import List

from .AzureFunctionAction import AzureFunctionAction


class IAzureFunctionService(ABC):

    @abstractmethod
    def get_actions(self) -> List[AzureFunctionAction]:
        ...
