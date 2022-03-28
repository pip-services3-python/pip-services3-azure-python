# -*- coding: utf-8 -*-
import json

import azure.functions as func
from pip_services3_commons.convert import JsonConverter

from pip_services3_azure.containers import AzureFunction
from test.Dummy import Dummy


class DummyAzureFunctionFixture:
    _function: AzureFunction

    def __init__(self, function: AzureFunction):
        self._function = function

        self.DUMMY1 = Dummy(None, 'Key 1', 'Content 1')
        self.DUMMY2 = Dummy(None, 'Key 2', 'Content 2')

    def test_crud_operations(self):
        # Create one dummy
        req = {'method': 'post', 'url': '', 'body_type': '', 'params': {}, 'route_params': {}, 'headers': {},
               'body': JsonConverter.to_json(
                   {
                       'cmd': 'create_dummy',
                       'dummy': self.DUMMY1
                   }
               )}

        response = self._function.act(func.http.HttpRequest(**req))

        dummy1 = Dummy(**json.loads(response.get_body()))
        assert dummy1 is not None
        assert dummy1.content, self.DUMMY1.content
        assert dummy1.key, self.DUMMY1.key

        # Create another dummy
        req['body'] = JsonConverter.to_json(
            {
                'cmd': 'create_dummy',
                'dummy': self.DUMMY1
            }
        )
        response = self._function.act(func.http.HttpRequest(**req))

        dummy2 = Dummy(**json.loads(response.get_body()))
        assert dummy2 is not None
        assert dummy2.content, self.DUMMY1.content
        assert dummy2.key, self.DUMMY1.key

        # Update the dummy
        req['body'] = JsonConverter.to_json(
            {
                'cmd': 'update_dummy',
                'dummy': dummy1
            }
        )

        dummy1.content = 'Updated Content 1'
        response = self._function.act(func.http.HttpRequest(**req))

        updated_dummy1 = Dummy(**json.loads(response.get_body()))
        assert updated_dummy1 is not None
        assert updated_dummy1.id, dummy1.id
        assert updated_dummy1.content, dummy1.content
        assert updated_dummy1.key, dummy1.key

        # Delete dummy
        req['body'] = JsonConverter.to_json(
            {
                'cmd': 'delete_dummy',
                'dummy_id': dummy1.id
            }
        )
        self._function.act(func.http.HttpRequest(**req))

        # Failed data test
        req['body'] = JsonConverter.to_json(
            {
                'cmd': 'create_dummy',
                'dummy': None
            }
        )

        response = self._function.act(func.http.HttpRequest(**req))

        assert json.loads(response.get_body())['code'] == 'INVALID_DATA'
