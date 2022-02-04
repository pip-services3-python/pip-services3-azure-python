# -*- coding: utf-8 -*-
from pip_services3_commons.convert import TypeCode
from pip_services3_commons.validate import ObjectSchema


class AzureFunctionRequestSchema(ObjectSchema):
    def __init__(self):
        super(AzureFunctionRequestSchema, self).__init__()
        self.with_required_property('cmd', TypeCode.String)
        self.with_optional_property('dummy', TypeCode.Map)
        self.with_optional_property('dummy_id', TypeCode.String)
