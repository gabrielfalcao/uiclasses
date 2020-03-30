# -*- coding: utf-8 -*-
from uiclasses import ModelList, Model
from humanfriendly.tables import format_robust_table, format_pretty_table


class BlogPost(Model):
    id: int
    title: str
    body: str


def test_from_generator():
    generator = (
        BlogPost(id=x, title=f"title {x}", body=f"body {x}")
        for x in range(100)
    )
    result = BlogPost.List(generator)
    result.should.be.a(ModelList)
    result.should.have.length_of(100)


def test_to_dict():

    post1 = BlogPost(dict(id=1, title="title 1", body="body 1"))

    post2 = BlogPost(dict(id=2, title="title 2", body="body 2"))

    posts = BlogPost.List([post1, post2])

    posts.should.be.a(ModelList)

    posts.to_dict().should.equal(
        [
            {"id": 1, "title": "title 1", "body": "body 1"},
            {"id": 2, "title": "title 2", "body": "body 2"},
        ]
    )

    repr(posts).should.equal(
        "[<BlogPost id=1 title='title 1' body='body 1'>, <BlogPost id=2 title='title 2' body='body 2'>]"
    )
    str(posts).should.equal("BlogPost.List[length=2]")

    second_list = BlogPost.List(posts.to_dict())
    second_list.should.equal(posts)

    third_list = BlogPost.List([post1, post2, post1, post2]).unique()
    third_list.should.be.a(BlogPost.Set)
    third_list.should.have.length_of(2)


def test_sorted_by():

    post1 = BlogPost(dict(id=1, title="title 1", body="body 1"))

    post2 = BlogPost(dict(id=2, title="title 2", body="body 2"))

    posts = BlogPost.List([post1, post2]).sorted_by("title", reverse=True)

    posts.should.be.a(ModelList)
    posts.should.have.property("__of_model__").being.equal(BlogPost)

    posts.to_dict().should.equal(
        [
            {"id": 2, "title": "title 2", "body": "body 2"},
            {"id": 1, "title": "title 1", "body": "body 1"},
        ]
    )


def test_filter_by_glob():

    post1 = BlogPost(dict(id=1, title="foo bar", body="body 1"))

    post2 = BlogPost(dict(id=2, title="chuck norris", body="body 2"))

    posts = BlogPost.List([post1, post2]).filter_by("title", "*uck*")

    posts.should.be.a(ModelList)
    posts.should.have.property("__of_model__").being.equal(BlogPost)

    posts.to_dict().should.equal(
        [{"id": 2, "title": "chuck norris", "body": "body 2"}]
    )


def test_filter_by_exact_match():

    post1 = BlogPost(dict(id=1, title="foo bar", body="body 1"))

    post2 = BlogPost(dict(id=2, title="chuck norris", body="body 2"))

    posts = BlogPost.List([post1, post2]).filter_by("id", 1)

    posts.should.be.a(ModelList)
    posts.should.be.a(BlogPost.List)
    posts.should.have.property("__of_model__").being.equal(BlogPost)

    posts.to_dict().should.equal(
        [{"id": 1, "title": "foo bar", "body": "body 1"}]
    )


def test_list_with_invalid_model():

    post1 = BlogPost(dict(id=1, title="foo bar", body="body 1"))

    post2 = BlogPost(dict(id=2, title="chuck norris", body="body 2"))

    when_called = BlogPost.List.when.called_with([post1, post2, "not a model"])

    when_called.should.have.raised(
        TypeError,
        "cannot create BlogPost.List because value at index [2] is not a <class 'tests.unit.test_list.BlogPost'>: 'not a model' <class 'str'>",
    )


def test_format_pretty_table():

    post1 = BlogPost(dict(id=1, title="title 1", body="body 1"))

    post2 = BlogPost(dict(id=2, title="title 2", body="body 2"))

    posts = BlogPost.List([post1, post2])

    posts.should.be.a(ModelList)

    posts.format_pretty_table().should.equal(
        format_pretty_table(
            [[1, "title 1", "body 1"], [2, "title 2", "body 2"]],
            ["id", "title", "body"],
        )
    )

    posts.format_pretty_table(["title"]).should.equal(
        format_pretty_table([["title 1"], ["title 2"]], ["title"])
    )

    when_called = posts.format_pretty_table.when.called_with(["inexistent"])
    when_called.should.have.raised(
        ValueError,
        "the following columns are not available for <class 'tests.unit.test_list.BlogPost'>: {'inexistent'}",
    )


def test_format_robust_table():

    post1 = BlogPost(dict(id=1, title="title 1", body="body 1"))

    post2 = BlogPost(dict(id=2, title="title 2", body="body 2"))

    posts = BlogPost.List([post1, post2])

    posts.should.be.a(ModelList)

    posts.format_robust_table().should.equal(
        format_robust_table(
            [[1, "title 1", "body 1"], [2, "title 2", "body 2"]],
            ["id", "title", "body"],
        )
    )

    posts.format_robust_table(["title"]).should.equal(
        format_robust_table([["title 1"], ["title 2"]], ["title"])
    )

    when_called = posts.format_robust_table.when.called_with(["inexistent"])
    when_called.should.have.raised(
        ValueError,
        "the following columns are not available for <class 'tests.unit.test_list.BlogPost'>: {'inexistent'}",
    )


def test_model_list_not_iterable():
    when_called = BlogPost.List.when.called_with(None)
    when_called.should.have.raised(
        TypeError,
        "BlogPost.List requires the 'children' attribute to be a valid iterable, got None <class 'NoneType'> instead",
    )
