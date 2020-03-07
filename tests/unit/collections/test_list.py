# -*- coding: utf-8 -*-
from uiclasses import ModelList, Model


class BlogPost(Model):
    id: str
    title: str
    body: str



def test_to_dict():

    post1 = BlogPost(dict(
        id='1',
        title='title 1',
        body='body 1',
    ))

    post2 = BlogPost(dict(
        id='2',
        title='title 2',
        body='body 2',
    ))

    posts = BlogPost.List(post1, post2)

    posts.should.be.a(ModelList)

    posts.to_dict().should.equal([
        {'id': '1', 'title': 'title 1', 'body': 'body 1'},
        {'id': '2', 'title': 'title 2', 'body': 'body 2'},
    ])

    repr(posts).should.equal("[<BlogPost id='1' title='title 1' body='body 1'>, <BlogPost id='2' title='title 2' body='body 2'>]")
    str(posts).should.equal('ModelList(BlogPost, count=2)')


def test_sorted_by():

    post1 = BlogPost(dict(
        id='1',
        title='title 1',
        body='body 1',
    ))

    post2 = BlogPost(dict(
        id='2',
        title='title 2',
        body='body 2',
    ))

    posts = BlogPost.List(post1, post2).sorted_by('title', reverse=True)

    posts.should.be.a(ModelList)
    posts.should.have.property('model_class').being.equal(BlogPost)

    posts.to_dict().should.equal([
        {'id': '2', 'title': 'title 2', 'body': 'body 2'},
        {'id': '1', 'title': 'title 1', 'body': 'body 1'},
    ])


def test_filter_by():

    post1 = BlogPost(dict(
        id='1',
        title='foo bar',
        body='body 1',
    ))

    post2 = BlogPost(dict(
        id='2',
        title='chuck norris',
        body='body 2',
    ))

    posts = BlogPost.List(post1, post2).filter_by('title', '*uck*')

    posts.should.be.a(ModelList)
    posts.should.have.property('model_class').being.equal(BlogPost)

    posts.to_dict().should.equal([
        {'id': '2', 'title': 'chuck norris', 'body': 'body 2'},
    ])


def test_list_with_invalid_model():

    post1 = BlogPost(dict(
        id='1',
        title='foo bar',
        body='body 1',
    ))

    post2 = BlogPost(dict(
        id='2',
        title='chuck norris',
        body='body 2',
    ))

    when_called = BlogPost.List.when.called_with(post1, post2, 'not a model')

    when_called.should.have.raised(TypeError, "cannot create ModelList because value at index [2] is not a <class 'tests.unit.collections.test_list.BlogPost'>: 'not a model' <class 'str'>")


def test_format_robust_table():

    post1 = BlogPost(dict(
        id='1',
        title='title 1',
        body='body 1',
    ))

    post2 = BlogPost(dict(
        id='2',
        title='title 2',
        body='body 2',
    ))

    posts = BlogPost.List(post1, post2)

    posts.should.be.a(ModelList)

    posts.format_robust_table().should.equal(
        '--------------\n'
        '\x1b[1;32mid:\x1b[0m 1\n'
        '\x1b[1;32mtitle:\x1b[0m title 1\n'
        '\x1b[1;32mbody:\x1b[0m body 1\n'
        '--------------\n'
        '\x1b[1;32mid:\x1b[0m 2\n'
        '\x1b[1;32mtitle:\x1b[0m title 2\n'
        '\x1b[1;32mbody:\x1b[0m body 2\n'
        '--------------'
    )

    posts.format_robust_table(['title']).should.equal(
        '--------------\n'
        '\x1b[1;32mtitle:\x1b[0m title 1\n'
        '--------------\n'
        '\x1b[1;32mtitle:\x1b[0m title 2\n'
        '--------------'
    )


def test_format_pretty_table():

    post1 = BlogPost(dict(
        id='1',
        title='title 1',
        body='body 1',
    ))

    post2 = BlogPost(dict(
        id='2',
        title='title 2',
        body='body 2',
    ))

    posts = BlogPost.List(post1, post2)

    posts.should.be.a(ModelList)

    posts.format_pretty_table().should.equal(
        '-------------------------\n'
        '| \x1b[1;32mid\x1b[0m | \x1b[1;32mtitle\x1b[0m   | \x1b[1;32mbody\x1b[0m   |\n'
        '-------------------------\n'
        '|  1 | title 1 | body 1 |\n'
        '|  2 | title 2 | body 2 |\n'
        '-------------------------'
    )

    posts.format_pretty_table(['title']).should.equal(
        '-----------\n'
        '| \x1b[1;32mtitle\x1b[0m   |\n'
        '-----------\n'
        '| title 1 |\n'
        '| title 2 |\n'
        '-----------'
    )

    when_called = posts.format_pretty_table.when.called_with(['inexistent'])
    when_called.should.have.raised(ValueError, "the following columns are not available for <class 'tests.unit.collections.test_list.BlogPost'>: {'inexistent'}")


def test_model_list_not_iterable():
    when_called = ModelList.when.called_with(BlogPost, None)
    when_called.should.have.raised(TypeError, "ModelList requires the 'children' attribute to be a list, got None <class 'NoneType'> instead")


def test_model_list_not_model():
    when_called = ModelList.when.called_with(dict, None)
    when_called.should.have.raised(TypeError, "ModelList requires the 'model_class' attribute to be a Model subclass, got <class 'dict'> instead")
