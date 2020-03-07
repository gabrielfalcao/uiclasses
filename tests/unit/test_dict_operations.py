# -*- coding: utf-8 -*-
from typing import List
from uiclasses import Model

"""
Background: Managing data from a Trello-like application
"""


class User(Model):
    id: str
    username: str
    email: str


class Task(Model):
    id: str
    title: str
    description: str
    owner: User


class TaskList(Model):
    id: str
    name: str
    url: str
    tasks: List[Task]


class TaskBoard(Model):
    id: str
    name: str
    url: str
    lists: List[TaskList]


def test_to_dict():
    model = User(
        {"id": "1", "username": "chucknorris", "email": "root@chucknorris.com"}
    )
    model.to_dict().should.equal(
        {"id": "1", "username": "chucknorris", "email": "root@chucknorris.com"}
    )
