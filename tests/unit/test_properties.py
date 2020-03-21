# -*- coding: utf-8 -*-
from uiclasses import Model
from uiclasses.typing import Getter
from uiclasses.typing import Setter
from uiclasses.typing import Property


class Account(Model):
    __visible_attributes__ = ["id", "username", "email"]
    id: int
    username: str
    slack_username: Getter[str]
    jira_token: Setter[str]
    verified: Property[bool]


def test_getters():
    chuck = Account(
        id=1,
        username="chucknorris",
        email='chuck@norris.com',
        github_token="roundhousekick",
        slack_username='@chuck',
        jira_token='basecampforever<3',
        verified=True,
    )

    chuck.get_table_columns().should.equal(['id', 'username', 'email'])
    chuck.get_table_rows().should.equal(
        [
            [1, 'chucknorris', 'chuck@norris.com']
        ]
    )


def test_setters():
    chuck = Account(username="johndoe", github_token="foobar")

    chuck.username.should.equal('johndoe')
    chuck.to_dict().should.equal({
        "username": "johndoe",
        "github_token": "foobar",
    })

    chuck.username = 'chucknorris'
    chuck.jira_token = 'basecampforever<3'
    chuck.verified = 'yes'
    setattr.when.called_with(chuck, 'github_token', 'roundhousekick').should.have.raised(
        AttributeError, "'Account' object has no attribute 'github_token'"
    )

    chuck.username.should.equal('chucknorris')
    chuck.to_dict().should.equal({
        "username": "chucknorris",
        "github_token": "foobar",
        "jira_token": "basecampforever<3",
        "verified": True
    })
    getattr.when.called_with(chuck, 'github_token').should.have.raised(
        AttributeError, "'Account' object has no attribute 'github_token'"
    )
    getattr.when.called_with(chuck, 'jira_token').should.have.raised(
        AttributeError, "'Account' object has no attribute 'jira_token'"
    )


def test_construct_with_kwargs():
    chuck = Account(id=1, username="chucknorris", email="root@chucknorris.com")
    chuck.to_dict().should.equal(
        {"id": 1, "username": "chucknorris", "email": "root@chucknorris.com"}
    )


def test_getbool():
    Account(dict(verified="yes")).verified.should.equal(True)
    Account(dict(verified="t")).verified.should.equal(True)
    Account(dict(verified="true")).verified.should.equal(True)
    Account(dict(verified="True")).verified.should.equal(True)

    Account(dict(verified="no")).verified.should.equal(False)
    Account(dict(verified="")).verified.should.equal(False)
    Account(dict(verified="false")).verified.should.equal(False)
    Account(dict(verified="False")).verified.should.equal(False)

    # non-strings
    Account(dict(verified=True)).verified.should.equal(True)
    Account(dict(verified={"some": "dict"})).verified.should.equal(True)

    Account(dict(verified=False)).verified.should.equal(False)
    Account(dict(verified={})).verified.should.equal(False)


def test_construct_with_dict():
    chuck = Account({"id": 1, "username": "chucknorris", "email": "root@chucknorris.com"})
    chuck.to_dict().should.equal(
        {"id": 1, "username": "chucknorris", "email": "root@chucknorris.com"}
    )


def test_nonzero():
    empty = Account()
    full = Account(id=2)
    bool(empty).should.equal(False)
    bool(full).should.equal(True)


def test_hashing():
    chuck1 = Account(
        **{"id": 10000, "username": "chucknorris", "email": "root@chucknorris.com"}
    )
    chuck2 = Account(
        **{"id": 10000, "username": "chucknorris", "email": "root@chucknorris.com"}
    )
    chuck3 = Account(**{"id": 2, "username": "chucknorris", "email": "root@chucknorris.com"})

    hash(chuck1).should.equal(2003873043500067927)
    hash(chuck2).should.equal(2003873043500067927)
    hash(chuck3).should.equal(921033703088125588)


def test_equals():
    chuck1 = Account({"id": 1, "username": "chucknorris", "email": "root@chucknorris.com"})
    chuck2 = Account({"id": 1, "username": "chucknorris", "email": "root@chucknorris.com"})

    chuck1.should.equal(chuck2)

    # cannot be compared to a dict
    chuck1.should_not.equal(chuck1.to_dict())

    # cannot be compared to a list
    chuck1.should_not.equal([1, 2])
