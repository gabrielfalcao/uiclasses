# -*- coding: utf-8 -*-
from uiclasses import ModelSet, Model
from humanfriendly.tables import (
    format_robust_table,
    format_pretty_table,
)


class Essay(Model):
    id: str
    title: str
    body: str


def test_to_dict():

    post1 = Essay(dict(
        id='1',
        title='title 1',
        body='body 1',
    ))

    post2 = Essay(dict(
        id='2',
        title='title 2',
        body='body 2',
    ))

    posts = Essay.Set([post1, post2])

    posts.should.be.a(ModelSet)

    posts.to_dict().should.equal([
        {'id': '1', 'title': 'title 1', 'body': 'body 1'},
        {'id': '2', 'title': 'title 2', 'body': 'body 2'},
    ])

    repr(posts).should.equal("Essay.Set([<Essay id='1' title='title 1' body='body 1'>, <Essay id='2' title='title 2' body='body 2'>])")
    str(posts).should.equal('Essay.Set[length=2]')


def test_sorted_by():

    post1 = Essay(dict(
        id='1',
        title='title 1',
        body='body 1',
    ))

    post2 = Essay(dict(
        id='2',
        title='title 2',
        body='body 2',
    ))

    posts = Essay.Set([post1, post2]).sorted_by('title', reverse=True)

    posts.should.be.a(ModelSet)
    posts.should.have.property('__of_model__').being.equal(Essay)

    posts.to_dict().should.equal([
        {'id': '2', 'title': 'title 2', 'body': 'body 2'},
        {'id': '1', 'title': 'title 1', 'body': 'body 1'},
    ])


def test_filter_by():

    post1 = Essay(dict(
        id='1',
        title='foo bar',
        body='body 1',
    ))

    post2 = Essay(dict(
        id='2',
        title='chuck norris',
        body='body 2',
    ))

    posts = Essay.Set([post1, post2]).filter_by('title', '*uck*')

    posts.should.be.a(ModelSet)
    posts.should.have.property('__of_model__').being.equal(Essay)

    posts.to_dict().should.equal([
        {'id': '2', 'title': 'chuck norris', 'body': 'body 2'},
    ])


def test_set_with_invalid_model():

    post1 = Essay(dict(
        id='1',
        title='foo bar',
        body='body 1',
    ))

    post2 = Essay(dict(
        id='2',
        title='chuck norris',
        body='body 2',
    ))

    when_called = Essay.Set.when.called_with([post1, post2, 'not a model'])
    when_called.should.have.raised(TypeError, "cannot create Essay.Set because value at index [2] is not a <class 'tests.unit.collections.test_set.Essay'>: 'not a model' <class 'str'>")


def test_format_pretty_table():

    post1 = Essay(dict(
        id='1',
        title='title 1',
        body='body 1',
    ))

    post2 = Essay(dict(
        id='2',
        title='title 2',
        body='body 2',
    ))

    posts = Essay.Set([post1, post2])

    posts.should.be.a(ModelSet)

    posts.format_pretty_table().should.equal(format_pretty_table(
        [
            ['1', 'title 1', 'body 1'],
            ['2', 'title 2', 'body 2'],
        ],
        ['id', 'title', 'body']
    ))

    posts.format_pretty_table(['title']).should.equal(format_pretty_table(
        [
            ['title 1'],
            ['title 2'],
        ],
        ['title']
    ))

    when_called = posts.format_pretty_table.when.called_with(['inexistent'])
    when_called.should.have.raised(ValueError, "the following columns are not available for <class 'tests.unit.collections.test_set.Essay'>: {'inexistent'}")


def test_format_robust_table():

    post1 = Essay(dict(
        id='1',
        title='title 1',
        body='body 1',
    ))
    post1_copy = Essay(dict(
        id='1',
        title='title 1',
        body='body 1',
    ))

    post2 = Essay(dict(
        id='2',
        title='title 2',
        body='body 2',
    ))

    posts = Essay.Set([post1, post2, post1_copy])

    posts.should.be.a(ModelSet)

    posts.format_robust_table().should.equal(format_robust_table(
        [
            ['1', 'title 1', 'body 1'],
            ['2', 'title 2', 'body 2'],
        ],
        ['id', 'title', 'body']
    ))

    posts.format_robust_table(['title']).should.equal(format_robust_table(
        [
            ['title 1'],
            ['title 2'],
        ],
        ['title']
    ))

    when_called = posts.format_robust_table.when.called_with(['inexistent'])
    when_called.should.have.raised(ValueError, "the following columns are not available for <class 'tests.unit.collections.test_set.Essay'>: {'inexistent'}")


def test_model_set_not_iterable():
    when_called = Essay.Set.when.called_with(None)
    when_called.should.have.raised(TypeError, "Essay.Set requires the 'children' attribute to be a valid iterable, got None <class 'NoneType'> instead")
