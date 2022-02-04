# -*- coding: utf-8 -*-
from pip_services3_commons.refer import Descriptor
from pip_services3_components.build import Factory

from test.DummyController import DummyController
from test.services.DummyAzureFunctionService import DummyAzureFunctionService
from test.services.DummyCommandableAzureFunctionService import DummyCommandableAzureFunctionService


class DummyFactory(Factory):
    FactoryDescriptor = Descriptor("pip-services-dummies", "factory", "default", "default", "1.0")
    ControllerDescriptor = Descriptor("pip-services-dummies", "controller", "default", "*", "1.0")
    AzureFunctionServiceDescriptor = Descriptor("pip-services-dummies", "service", "azure-function", "*", "1.0")
    CmdAzureFunctionServiceDescriptor = Descriptor("pip-services-dummies", "service", "commandable-azure-function", "*",
                                                   "1.0")

    def __init__(self):
        super(DummyFactory, self).__init__()
        self.register_as_type(DummyFactory.ControllerDescriptor, DummyController)
        self.register_as_type(DummyFactory.AzureFunctionServiceDescriptor, DummyAzureFunctionService)
        self.register_as_type(DummyFactory.CmdAzureFunctionServiceDescriptor, DummyCommandableAzureFunctionService)
