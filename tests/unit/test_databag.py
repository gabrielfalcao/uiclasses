# -*- coding: utf-8 -*-
from uiclasses import DataBag


def test_databag_non_dict_raises():
    "DataBag() should raise TypeError when fed with a non-dict parameter"

    when_called = DataBag.when.called_with("not a dict")
    when_called.should.have.raised(
        TypeError,
        "DataBag() requires a dict object, but instead got 'not a dict <class 'str'>'.",
    )


def test_databag_traverse_to_section():
    "DataBag().traverse() should return a config section"

    # Given a databag with nested dicts
    d = DataBag({"section": {"subsection": {"key": "value"}}})

    # When I traverse to a nested dict
    subsection = d.traverse("section", "subsection")

    # Then it returns
    str(d).should.equal("DataBag(section={'subsection': {'key': 'value'}})")
    str(subsection).should.equal(
        "DataBagChild 'section.subsection' of (key='value')"
    )

    # But when accessed with .get() it should be a plain dict
    d.get('section').should.be.a(dict)
    str(d.get('section')).should.equal("{'subsection': {'key': 'value'}}")


def test_databag_traverse_to_value():
    "DataBag().traverse() should return a config section"

    # Given a databag with nested dicts
    d = DataBag({"section": {"subsection": {"key": "value"}}})

    # When I traverse to a nested dict
    value = d.traverse("section", "subsection", "key")

    # Then it returns
    value.should.be.a(str)
    value.should.equal('value')


def test_databag_dict_interface():
    "DataBag() should behave like a dict"

    # Given a databag with some data
    data = DataBag({"chuck": "norris"})

    # When I set a new key
    data["foo"] = "bar"

    # Then it should work have the keys and values
    list(data).should.equal(["chuck", "foo"])
    list(data.keys()).should.equal(["chuck", "foo"])
    list(data.values()).should.equal(["norris", "bar"])
    list(data.items()).should.equal([("chuck", "norris"), ("foo", "bar")])
    data.get('chuck').should.equal('norris')

    # When I get a key
    data["chuck"].should.equal("norris")

    # And update the dict
    data.update({
        'foo': '42',
        'another': 'field'
    })

    # Then it should work have the keys and values
    list(data.keys()).should.equal(["chuck", "foo", "another"])
    list(data.values()).should.equal(["norris", "42", "field"])
    list(data.items()).should.equal([("chuck", "norris"), ("foo", "42"), ("another", "field")])
