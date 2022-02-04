# -*- coding: utf-8 -*-
from typing import Optional

import azure.functions as func
from pip_services3_commons.commands import CommandSet, ICommandable, ICommand
from pip_services3_commons.run import Parameters
from pip_services3_rpc.services import InstrumentTiming

from .AzureFunction import AzureFunction
from .AzureFunctionContextHelper import AzureFunctionContextHelper


class CommandableAzureFunction(AzureFunction):

    def __init__(self, name: Optional[str], description: Optional[str]):
        """
        Creates a new instance of this Azure Function.

        :param name: (optional) a container name (accessible via ContextInfo)
        :param description: (optional) a container description (accessible via ContextInfo)
        """
        super().__init__(name, description)
        self._dependency_resolver.put('controller', 'none')

    def _get_parameters(self, context: func.HttpRequest) -> Parameters:
        """
        Returns body from Azure Function context.
        This method can be overloaded in child classes

        :param context: Azure Function context
        :return: Returns Parameters from context
        """
        return AzureFunctionContextHelper.get_parameters(context)

    def __register_command_set(self, command_set: CommandSet):
        commands = command_set.get_commands()
        for i in range(len(commands)):
            command = commands[i]

            def wrapper(command: ICommand):
                # wrapper for passing context
                def action(context: func.HttpRequest):
                    correlation_id = self._get_correlation_id(context)
                    args = self._get_parameters(context)
                    timing: InstrumentTiming = self._instrument(correlation_id,
                                                                self._info.name + '.' + command.get_name())

                    try:
                        result = command.execute(correlation_id, args)
                        timing.end_timing()
                        return result
                    except Exception as e:
                        timing.end_timing(e)
                        raise e

                return action

            self._register_action(command.get_name(), None, wrapper(command))

    def register(self):
        """
        Registers all actions in this Azure Function.
        """
        controller: ICommandable = self._dependency_resolver.get_one_required('controller')
        command_set = controller.get_command_set()
        self.__register_command_set(command_set)
