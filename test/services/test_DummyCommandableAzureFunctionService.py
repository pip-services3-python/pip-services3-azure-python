# -*- coding: utf-8 -*-
import azure.functions as func

from pip_services3_commons.config import ConfigParams
from pip_services3_commons.convert import JsonConverter

from test.Dummy import Dummy
from test.containers.DummyCommandableAzureFunction import DummyCommandableAzureFunction

DUMMY1 = Dummy(None, 'Key 1', 'Content 1')
DUMMY2 = Dummy(None, 'Key 2', 'Content 2')


class TestDummyCommandableAzureFunctionService:
    _function_service: DummyCommandableAzureFunction

    def setup_method(self):
        config = ConfigParams.from_tuples(
            'logger.descriptor', 'pip-services:logger:console:default:1.0',
            'controller.descriptor', 'pip-services-dummies:controller:default:default:1.0',
            'service.descriptor', 'pip-services-dummies:service:commandable-azure-function:default:1.0'
        )

        self._function_service = DummyCommandableAzureFunction()
        self._function_service.configure(config)
        self._function_service.open(None)

    def teardown_method(self):
        self._function_service.close(None)

    def test_crud_operations(self):
        # Create one dummy
        req = {'method': 'post', 'url': '', 'body_type': '', 'params': {}, 'route_params': {}, 'headers': {},
               'body': JsonConverter.to_json(
                   {
                       'cmd': 'dummies.create_dummy',
                       'dummy': DUMMY1
                   }
               )}

        dummy1 = self._function_service.act(func.http.HttpRequest(**req))

        assert dummy1 is not None
        assert dummy1.content, DUMMY1.content
        assert dummy1.key, DUMMY1.key

        # Create another dummy
        req['body'] = JsonConverter.to_json(
            {
                'cmd': 'dummies.create_dummy',
                'dummy': DUMMY1
            }
        )
        dummy2 = self._function_service.act(func.http.HttpRequest(**req))

        assert dummy2 is not None
        assert dummy2.content, DUMMY1.content
        assert dummy2.key, DUMMY1.key

        # Update the dummy
        req['body'] = JsonConverter.to_json(
            {
                'cmd': 'dummies.update_dummy',
                'dummy': dummy1
            }
        )

        dummy1.content = 'Updated Content 1'
        updated_dummy1 = self._function_service.act(func.http.HttpRequest(**req))

        assert updated_dummy1 is not None
        assert updated_dummy1.id, dummy1.id
        assert updated_dummy1.content, dummy1.content
        assert updated_dummy1.key, dummy1.key

        # Delete dummy
        req['body'] = JsonConverter.to_json(
            {
                'cmd': 'dummies.delete_dummy',
                'dummy_id': dummy1.id
            }
        )
        self._function_service.act(func.http.HttpRequest(**req))

        req['body'] = JsonConverter.to_json(
            {
                'cmd': 'dummies.get_dummy_by_id',
                'dummy_id': dummy1.id
            }
        )

        dummy = self._function_service.act(func.http.HttpRequest(**req))

        assert dummy is None
