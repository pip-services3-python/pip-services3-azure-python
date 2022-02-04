# -*- coding: utf-8 -*-
from typing import Any, Callable

import azure.functions as func
from pip_services3_commons.validate import Schema


class AzureFunctionAction:

    def __init__(self, cmd: str, schema: Schema, action: Callable[[func.HttpRequest], Any]):
        # Command to call the action
        self.cmd = cmd
        # Schema to validate action parameters
        self.schema = schema

        self.action = action if action else self.action

    def action(self, context: func.HttpRequest) -> Any:
        """
        Action to be executed

        :param context: action context
        """
