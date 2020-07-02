from unittest import skip
from uiclasses import Model


class User(Model):
    fullname: str
    email: str


class Article(Model):
    title: str
    body: str
    author: User


class Resource(Model):
    uri: str
    http_method: str
    cached: int
    auth_type: str
    cross_origin: bool


class Route(Model):
    name: str
    basepath: str
    upstream_protocol: str
    version: int
    resource_set: str
    visibility: str
    resources: Resource.List


inputs = [
    {
        "name": "ping",
        "basepath": "/_/v1",
        "upstream_protocol": "http",
        "version": 1,
        "resource_set": "ping",
        "visibility": "internal",
        "resources": [
            {
                "uri": "ping",
                "http_method": "GET",
                "cached": 0,
                "auth_type": "",
                "cross_origin": False,
            }
        ],
    },
    {
        "name": "ping",
        "basepath": "/_/v0",
        "upstream_protocol": "http",
        "version": 0,
        "resource_set": "ping",
        "visibility": "internal",
        "resources": [
            {
                "uri": "ping",
                "http_method": "GET",
                "cached": 0,
                "auth_type": "",
                "cross_origin": False,
            }
        ],
    },
]


def test_model_with_nested_modellist_auto_cast():
    route1 = Route(
        {
            "name": "ping",
            "basepath": "/_/v1",
            "upstream_protocol": "http",
            "version": 1,
            "resource_set": "ping",
            "visibility": "internal",
            "resources": [
                {
                    "uri": "ping",
                    "http_method": "GET",
                    "cached": 0,
                    "auth_type": "",
                    "cross_origin": False,
                }
            ],
        }
    )

    route1.should.be.a(Route)
    route1.resources.should.be.a(Resource.List)
    route1.to_dict().should.equal(
        {
            "name": "ping",
            "basepath": "/_/v1",
            "upstream_protocol": "http",
            "version": 1,
            "resource_set": "ping",
            "visibility": "internal",
            "resources": [
                {
                    "uri": "ping",
                    "http_method": "GET",
                    "cached": 0,
                    "auth_type": "",
                    "cross_origin": False,
                }
            ],
        }
    )
    route1.serialize_visible().should.equal(
        {
            "name": "ping",
            "basepath": "/_/v1",
            "upstream_protocol": "http",
            "version": 1,
            "resource_set": "ping",
            "visibility": "internal",
            "resources": [
                {
                    "uri": "ping",
                    "http_method": "GET",
                    "cached": 0,
                    "auth_type": "",
                    "cross_origin": False,
                }
            ],
        }
    )


def test_model_with_nested_model_auto_cast():
    blog_post = Article(
        {
            "title": "first blog post",
            "body": "loren ipsum",
            "author": {"email": "foo@bar.com"},
        }
    )
    blog_post.author.should.be.a(User)
    blog_post.to_dict().should.equal(
        {
            "author": {"email": "foo@bar.com"},
            "body": "loren ipsum",
            "title": "first blog post",
        }
    )


def test_empty_nested_model():
    blog_post = Article(
        {"title": "first blog post", "body": "loren ipsum", "author": None}
    )
    blog_post.author.should.be.none
    blog_post.to_dict().should.equal(
        {"title": "first blog post", "body": "loren ipsum", "author": None}
    )


def test_list_with_models_and_nested_models():
    routes = Route.List(inputs)

    routes.should.be.a(Route.List)
    routes.should.have.length_of(2)

    r1, r2 = routes

    r1.to_dict().should.equal(
        {
            "name": "ping",
            "basepath": "/_/v1",
            "upstream_protocol": "http",
            "version": 1,
            "resource_set": "ping",
            "visibility": "internal",
            "resources": [
                {
                    "uri": "ping",
                    "http_method": "GET",
                    "cached": 0,
                    "auth_type": "",
                    "cross_origin": False,
                }
            ],
        }
    )

    r2.to_dict().should.equal(
        {
            "name": "ping",
            "basepath": "/_/v0",
            "upstream_protocol": "http",
            "version": 0,
            "resource_set": "ping",
            "visibility": "internal",
            "resources": [
                {
                    "uri": "ping",
                    "http_method": "GET",
                    "cached": 0,
                    "auth_type": "",
                    "cross_origin": False,
                }
            ],
        }
    )

    # And the route should have resources
    r1.resources.should.be.a(Resource.List)

    r1.resources.should.have.length_of(1)
    r1.resources[0].uri.should.equal("ping")
    r1.resources[0].http_method.should.equal("GET")
