from uiclasses import UserFriendlyObject, basic_dataclass


def test_ui_attributes():
    @basic_dataclass
    class Dummy(UserFriendlyObject):
        number: int
        string: str
        data: dict

    state1 = Dummy()
    state1.__ui_attributes__().should.equal({
        'number': 0,
        'string': '',
        'data': {}
    })

    state2 = Dummy()
    state2.number = 42
    state2.string = 'wat'
    state2.data = {'foo': 'bar'}
    state2.__ui_attributes__().should.equal({
        'data': {'foo': 'bar'},
        'number': 42,
        'string': 'wat'
    })
