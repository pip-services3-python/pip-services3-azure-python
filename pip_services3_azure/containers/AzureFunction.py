# -*- coding: utf-8 -*-
import json
import os
import signal
import sys
import threading
from typing import Optional, Dict, Any, List, Callable

import azure.functions as func
from pip_services3_commons.config import ConfigParams
from pip_services3_commons.errors import UnknownException, BadRequestException
from pip_services3_commons.refer import DependencyResolver, IReferences, Descriptor
from pip_services3_commons.validate import Schema
from pip_services3_components.count import CompositeCounters
from pip_services3_components.log import ConsoleLogger
from pip_services3_components.trace import CompositeTracer
from pip_services3_container import Container
from pip_services3_rpc.services import InstrumentTiming

from .AzureFunctionContextHelper import AzureFunctionContextHelper
from ..services import IAzureFunctionService


class AzureFunction(Container):
    """
    Abstract Azure Function, that acts as a container to instantiate and run components
    and expose them via external entry point.

    When handling calls "cmd" parameter determines which what action shall be called, while
    other parameters are passed to the action itself.

    Container configuration for this Azure Function is stored in `"./config/config.yml"` file.
    But this path can be overriden by `CONFIG_PATH` environment variable.

    ### References ###
        - `*:logger:*:*:1.0`            (optional) :class:`ILogger <pip_services3_components.log.ILogger.ILogger>`  components to pass log messages
        - `*:counters:*:*:1.0`          (optional) :class:`ICounters <pip_services3_components.count.ICounters.ICounters>`  components to pass collected measurements
        - `*:ervice:azure-function:*:*:1.0`        (optional) :class:`IAzureFunctionService <pip_services3_azure.services.IAzureFunctionService.IAzureFunctionService>` services to handle action requests
        - `*:service:commandable-azure-function:*:*:1.0`   (optional) :class:`IAzureFunctionService <pip_services3_azure.services.IAzureFunctionService.IAzureFunctionService>` services to handle action requests

    Example:

    .. code-block:: python
        class MyAzureFunctionFunction(AzureFunction):

            def __init__(self):
                super().__init__("mygroup", "MyGroup Azure Function")

        azure_function = MyAzureFunctionFunction()

        service.run()
        print("MyAzureFunctionFunction is started")

    """

    def __init__(self, name: Optional[str], description: Optional[str]):
        """
        Creates a new instance of this Azure Function function.

        :param name: (optional) a container name (accessible via ContextInfo)
        :param description: (optional) a container description (accessible via ContextInfo)
        """
        super(AzureFunction, self).__init__(name, description)

        # The performance counters.
        self._counters: CompositeCounters = CompositeCounters()

        # The tracer.
        self._tracer: CompositeTracer = CompositeTracer()

        # The dependency resolver.
        self._dependency_resolver: DependencyResolver = DependencyResolver()

        # The map of registred validation schemas.
        self._schemas: Dict[str, Schema] = {}

        # The map of registered actions.
        self._actions: Dict[str, Callable] = {}

        # The default path to config file.
        self._config_path: str = './config/config.yml'

        self._logger: ConsoleLogger = ConsoleLogger()

    def __get_config_path(self) -> str:
        return os.environ.get('CONFIG_PATH', self._config_path)

    def __get_parameters(self) -> ConfigParams:
        return ConfigParams.from_value(os.environ)

    def __capture_errors(self, correlation_id: Optional[str]):
        def handle_exception(exc_type, exc_value, exc_traceback):
            self._logger.fatal(correlation_id, exc_value, "Process is terminated")
            sys.exit(1)

        sys.excepthook = handle_exception

    def __capture_exit(self, correlation_id: Optional[str]):
        self._logger.info(correlation_id, "Press Control-C to stop the microservice...")

        # Activate graceful exit
        signal.signal(signal.SIGINT, lambda signum, frame: sys.exit())

        # Gracefully shutdown
        def shutdown(signum, frame):
            self.close(correlation_id)
            self._logger.info(correlation_id, 'Goodbye!' or sys.exit(0))
            sys.exit(0)

        signal.signal(signal.SIGTERM, shutdown)

    def set_references(self, references: IReferences):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        super().set_references(references)
        self._counters.set_references(references)
        self._dependency_resolver.set_references(references)

        self.register()

    def open(self, correlation_id: Optional[str]):
        """
        Opens the component.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        if self.is_open():
            return

        super(AzureFunction, self).open(correlation_id)
        self._register_services()

    def _instrument(self, correlation_id: Optional[str], name: str) -> InstrumentTiming:
        """
        Adds instrumentation to log calls and measure call time.
        It returns a InstrumentTiming object that is used to end the time measurement.

        Note: This method has been deprecated. Use AzureFunctionService instead.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param name: a method name.
        :return: object to end the time measurement.
        """
        self._logger.trace(correlation_id, "Executing %s method", name)
        self._counters.increment_one(name + ".exec_count")

        counter_timing = self._counters.begin_timing(name + ".exec_time")
        trace_timing = self._tracer.begin_trace(correlation_id, name, None)
        return InstrumentTiming(correlation_id, name, "exec", self._logger, self._counters, counter_timing,
                                trace_timing)

    def run(self):
        """
        Runs this Azure Function, loads container configuration,
        instantiate components and manage their lifecycle,
        makes this function ready to access action calls.
        """
        correlation_id = self._info.name

        path = self.__get_config_path()
        parameters = self.__get_parameters()
        self.read_config_from_file(correlation_id, path, parameters)

        # signals works only in main thread
        if threading.current_thread().name == 'MainThread':
            self.__capture_exit(correlation_id)
            self.__capture_errors(correlation_id)

        self.open(correlation_id)

    def register(self):
        """
        Registers all actions in this Azure Function.

        Note: Overloading of this method has been deprecated. Use AzureFunctionService instead.
        """

    def _register_services(self):
        """
        Registers all Azure Function services in the container.
        """
        services: List[IAzureFunctionService] = self._references.get_optional(
            Descriptor("*", "service", "azure-function", "*", "*"))
        cmd_services: List[IAzureFunctionService] = self._references.get_optional(
            Descriptor("*", "service", "commandable-azure-function", "*", "*"))

        services.extend(cmd_services)

        # Register actions defined in those services
        for service in services:
            # Check if the service implements required interface
            if not callable(service.get_actions):
                continue

            actions = service.get_actions()
            for action in actions:
                self._register_action(action.cmd, action.schema, action.action)

    def _register_action(self, cmd: str, schema: Schema, action: Callable[[func.HttpRequest], Any]):
        if cmd == '':
            raise UnknownException(None, 'NO_COMMAND', 'Missing command')

        if action is None:
            raise UnknownException(None, 'NO_ACTION', 'Missing action')

        if not callable(action):
            raise UnknownException(None, 'ACTION_NOT_FUNCTION', 'Action is not a function')

        if self._actions.get(cmd):
            raise UnknownException(None, 'DUPLICATED_ACTION', f"{cmd} action already exists")

        # Hack!!! Wrapping action to preserve prototyping context
        def action_curl(context: func.HttpRequest) -> func.HttpResponse:
            # Perform validation
            if schema:
                params = {'body': {} if not context.get_body() else context.get_json()}
                params.update(context.route_params)
                params.update(context.params)

                correlation_id = self._get_correlation_id(context)
                err = schema.validate_and_return_exception(correlation_id, params, False)
                if err is not None:
                    return func.HttpResponse(
                        body=json.dumps(err.to_json()),
                        status_code=err.status
                    )

            # Todo: perform verification?
            return action(context)

        self._actions[cmd] = action_curl

    def _get_correlation_id(self, context: func.HttpRequest) -> str:
        """
        Returns correlationId from Azure Function context.
        This method can be overloaded in child classes

        :param context: Azure Function context
        :return: Returns correlationId from context
        """
        return AzureFunctionContextHelper.get_correlation_id(context)

    def _get_command(self, context: func.HttpRequest) -> str:
        """
        Returns command from Azure Function context.
        This method can be overloaded in child classes

        :param context:  Azure Function context
        :return: Returns command from context
        """
        return AzureFunctionContextHelper.get_command(context)

    def _execute(self, context: func.HttpRequest) -> func.HttpResponse:
        """
        Executes this Azure Function and returns the result.
        This method can be overloaded in child classes
        if they need to change the default behavior

        :param context: context the context parameters (or function arguments)
        :return: the result of the function execution.
        """
        cmd = self._get_command(context)
        correlation_id = self._get_correlation_id(context)
        if cmd is None:
            raise BadRequestException(
                correlation_id,
                'NO_COMMAND',
                'Cmd parameter is missing'
            )

        action = self._actions.get(cmd)
        if not action:
            raise BadRequestException(
                correlation_id,
                'NO_ACTION',
                'Action ' + cmd + ' was not found'
            ).with_details('command', cmd)

        return action(context)

    def __handler(self, context: func.HttpRequest) -> Any:
        # If already started then execute
        if self.is_open():
            return self._execute(context)
        # Start before execute
        self.run()
        return self._execute(context)

    def get_handler(self) -> Callable[[func.HttpRequest], func.HttpResponse]:
        # Return plugin function
        return lambda context: self.__handler(context)

    def act(self, context: func.HttpRequest) -> func.HttpResponse:
        """
        Calls registered action in this Azure Function.
        "cmd" parameter in the action parameters determin
        what action shall be called.

        This method shall only be used in testing.

        :param context: action parameters.
        :return: action result
        """
        return self.get_handler()(context)
