# -*- coding: utf-8 -*-
from typing import Any, Type, TypeVar, Generic
from uiclasses import Model
from uiclasses.typing import Property

from humanfriendly.tables import format_robust_table, format_pretty_table

from .helpers import AlmostDict


T = TypeVar("T")


class Config(Model):
    data: Any
    type: Type
    generic: Generic[T]


class User(Model):
    __visible_attributes__ = ["id", "username", "email"]
    id: int
    username: str


class Person(Model):
    name: str
    age: int
    email: Property[str]


def test_casting_generics_and_special_types():
    conf1 = Config({"data": {}, "type": str, "generic": [None]})

    conf1.to_dict().should.equal({"data": {}, "type": str, "generic": [None]})


def test_construct_with_dict_like_object():
    # Given an object that is not a dict but behaves like one
    almost = AlmostDict(
        dict(id=1, username="chucknorris", email="root@chucknorris.com")
    )

    # When I instantiate a model with it
    chuck = User(almost)

    # Then it should work
    chuck.to_dict().should.equal(
        {"id": 1, "username": "chucknorris", "email": "root@chucknorris.com"}
    )


def test_getters():
    chuck = User(id=1, username="chucknorris", github_token="roundhousekick")
    chuck.id.should.equal(1)
    chuck.username.should.equal("chucknorris")

    getattr.when.called_with(chuck, "github_token").should.have.raised(
        AttributeError, "'User' object has no attribute 'github_token'"
    )


def test_setters():
    chuck = User(username="johndoe", github_token="foobar")

    chuck.username.should.equal("johndoe")
    chuck.to_dict().should.equal(
        {"username": "johndoe", "github_token": "foobar"}
    )

    chuck.username = "chucknorris"
    chuck.github_token = "roundhousekick"

    chuck.username.should.equal("chucknorris")
    chuck.to_dict().should.equal(
        {"username": "chucknorris", "github_token": "foobar"}
    )
    chuck.should.have.property("github_token").being.equal("roundhousekick")


def test_construct_with_kwargs():
    chuck = User(id=1, username="chucknorris", email="root@chucknorris.com")
    chuck.to_dict().should.equal(
        {"id": 1, "username": "chucknorris", "email": "root@chucknorris.com"}
    )


def test_getbool():
    User(dict(verified="yes")).getbool("verified").should.equal(True)
    User(dict(verified="t")).getbool("verified").should.equal(True)
    User(dict(verified="true")).getbool("verified").should.equal(True)
    User(dict(verified="True")).getbool("verified").should.equal(True)

    User(dict(verified="no")).getbool("verified").should.equal(False)
    User(dict(verified="")).getbool("verified").should.equal(False)
    User(dict(verified="false")).getbool("verified").should.equal(False)
    User(dict(verified="False")).getbool("verified").should.equal(False)

    # non-strings
    User(dict(verified=True)).getbool("verified").should.equal(True)
    User(dict(verified={"some": "dict"})).getbool("verified").should.equal(True)

    User(dict(verified=False)).getbool("verified").should.equal(False)
    User(dict(verified={})).getbool("verified").should.equal(False)


def test_construct_with_dict():
    chuck = User(
        {"id": 1, "username": "chucknorris", "email": "root@chucknorris.com"}
    )
    chuck.to_dict().should.equal(
        {"id": 1, "username": "chucknorris", "email": "root@chucknorris.com"}
    )


def test_nonzero():
    empty = User()
    full = User(id=2)
    bool(empty).should.equal(False)
    bool(full).should.equal(True)


def test_hashing():
    chuck1 = User(
        {
            "id": 10000,
            "username": "chucknorris",
            "email": "root@chucknorris.com",
        }
    )
    chuck2 = User(
        {
            "id": 10000,
            "username": "chucknorris",
            "email": "root@chucknorris.com",
        }
    )
    chuck3 = User(
        {"id": 2, "username": "chucknorris", "email": "root@chucknorris.com"}
    )

    hash(chuck1).should.equal(1321482623931622270)
    hash(chuck2).should.equal(1321482623931622270)
    hash(chuck3).should.equal(614150061375549557)


def test_equals():
    chuck1 = User(
        {"id": 1, "username": "chucknorris", "email": "root@chucknorris.com"}
    )
    chuck2 = User(
        {"id": 1, "username": "chucknorris", "email": "root@chucknorris.com"}
    )

    chuck1.should.equal(chuck2)

    # cannot be compared to a dict
    chuck1.should_not.equal(chuck1.to_dict())

    # cannot be compared to a list
    chuck1.should_not.equal([1, 2])


def test_format_pretty_table():
    chuck = User(
        {"id": 1, "username": "chucknorris", "email": "root@chucknorris.com"}
    )
    chuck.get_table_columns().should.equal(["id", "username", "email"])
    chuck.get_table_rows().should.equal([[1, "chucknorris", "root@chucknorris.com"]])

    chuck.format_pretty_table().should.equal(
        format_pretty_table(
            [[1, "chucknorris", "root@chucknorris.com"]],
            ["id", "username", "email"],
        )
    )


def test_format_pretty_table_without_explicit_visible_attributes():
    chuck = Person(
        {"age": 42, "name": "Chuck Norris", "email": "root@chucknorris.com"}
    )
    chuck.get_table_columns().should.equal(["name", "age"])
    chuck.get_table_rows().should.equal([["Chuck Norris", 42]])

    chuck.format_pretty_table().should.equal(
        format_pretty_table(
            [["Chuck Norris", 42]],
            ["name", "age"],
        )
    )


def test_format_robust_table():
    chuck = User(
        {"id": 1, "username": "chucknorris", "email": "root@chucknorris.com"}
    )
    chuck.format_robust_table().should.equal(
        format_robust_table(
            [[1, "chucknorris", "root@chucknorris.com"]],
            ["id", "username", "email"],
        )
    )


def test_create_model_with_nondict_data():

    when_created = User.when.called_with(["this is a list", "not a dict"])

    when_created.should.have.raised(
        TypeError,
        "User received a non-dict __data__ argument: ['this is a list', 'not a dict']",
    )


def test_create_model_with_kwarg_type_mismatching_field_declaration():
    when_created = User.when.called_with(id=1, username={"a set, not a string"})

    when_created.should.have.raised(
        TypeError, "username is not a <class 'str'>: {'a set, not a string'}"
    )
