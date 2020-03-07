# -*- coding: utf-8 -*-
import json
from dataclasses import dataclass, field
from uiclasses import Model


class User(Model):
    id: str
    username: str
    email: str
    verified: bool = field(repr=False)


def test_from_json():
    data = {'id': '1', 'username': 'chucknorris', 'email': 'root@chucknorris.com', 'verified': 'yes'}
    raw_json = json.dumps(data)
    model = User.from_json(raw_json)

    model.should.be.a(User)
    model.to_dict().should.equal({'id': '1', 'username': 'chucknorris', 'email': 'root@chucknorris.com', 'verified': True})


def test_from_json_invalid():
    when_called = User.from_json.when.called_with('@not a valid json$')

    when_called.should.have.raised('Expecting value: line 1 column 1 (char 0)')
