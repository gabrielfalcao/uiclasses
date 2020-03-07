# -*- coding: utf-8 -*-
from uiclasses import Model

from humanfriendly.tables import (
    format_robust_table,
    format_pretty_table,
)


class User(Model):
    id: str
    username: str
    email: str


def test_construct_with_kwargs():

    chuck = User(
        id='1',
        username='chucknorris',
        email='root@chucknorris.com'
    )
    chuck.to_dict().should.equal({'id': '1', 'username': 'chucknorris', 'email': 'root@chucknorris.com'})


def test_getbool():

    User(dict(verified='yes')).getbool('verified').should.equal(True)
    User(dict(verified='t')).getbool('verified').should.equal(True)
    User(dict(verified='true')).getbool('verified').should.equal(True)
    User(dict(verified='True')).getbool('verified').should.equal(True)

    User(dict(verified='no')).getbool('verified').should.equal(False)
    User(dict(verified='')).getbool('verified').should.equal(False)
    User(dict(verified='false')).getbool('verified').should.equal(False)
    User(dict(verified='False')).getbool('verified').should.equal(False)


def test_construct_with_dict():
    chuck = User({'id': '1', 'username': 'chucknorris', 'email': 'root@chucknorris.com'})
    chuck.to_dict().should.equal({'id': '1', 'username': 'chucknorris', 'email': 'root@chucknorris.com'})


def test_format_pretty_table():
    chuck = User({'id': '1', 'username': 'chucknorris', 'email': 'root@chucknorris.com'})
    chuck.format_pretty_table().should.equal(format_pretty_table(
        [
            [1, 'chucknorris', 'root@chucknorris.com'],
        ],
        ['id', 'username', 'email'],
    ))


def test_format_robust_table():
    chuck = User({'id': '1', 'username': 'chucknorris', 'email': 'root@chucknorris.com'})
    chuck.format_robust_table().should.equal(format_robust_table(
        [
            [1, 'chucknorris', 'root@chucknorris.com'],
        ],
        ['id', 'username', 'email'],
    ))
