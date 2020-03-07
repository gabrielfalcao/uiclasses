# -*- coding: utf-8 -*-
import json
from dataclasses import field
from uiclasses import Model, errors


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

    model.to_json().should.equal(json.dumps(model.to_dict()))


def test_from_json_invalid():
    when_called = User.from_json.when.called_with('@not a valid json$')

    when_called.should.have.raised(errors.InvalidJSON, "'@not a valid json$' cannot be parsed as a dict")
