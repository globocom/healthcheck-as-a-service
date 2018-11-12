# Copyright 2014 healthcheck-as-a-service authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import unittest
import mock
import os

from healthcheck.storage import (HealthCheck, HealthCheckNotFoundError, Item,
                                 Jsonable, MongoStorage, User,
                                 UserNotFoundError, ItemNotFoundError)


class JsonableTest(unittest.TestCase):

    def test_to_json(self):
        jsonable = Jsonable()
        jsonable.id = 1
        self.assertDictEqual(jsonable.to_json(), {"id": 1})


class HealthCheckTest(unittest.TestCase):

    def test_healthcheck(self):
        name = "myhc"
        group_id = "123"
        hc = HealthCheck(name=name, group_id=group_id)
        self.assertEqual(hc.name, name)
        self.assertEqual(hc.group_id, group_id)

    def test_to_json(self):
        hc = HealthCheck("myhc", id=1)
        self.assertDictEqual(hc.to_json(), {"name": "myhc", "host_groups": [], "id": 1})


class UserTest(unittest.TestCase):

    def test_user(self):
        id = "someid"
        email = "watcher@watcher.com"
        group_id = "anotherid"
        user = User(id, email, group_id)
        self.assertEqual(user.id, id)
        self.assertEqual(user.email, email)
        self.assertEqual(user.groups_id, (group_id,))

    def test_to_json(self):
        user = User("someid", "w@w.com", "id")
        expected = {"id": "someid", "email": "w@w.com", "groups_id": ("id",)}
        self.assertDictEqual(expected, user.to_json())


class ItemTest(unittest.TestCase):

    def test_item(self):
        item = Item("http://teste.com", item_id=1)
        self.assertEqual(item.url, "http://teste.com")
        self.assertEqual(item.item_id, 1)

    def test_to_json(self):
        item = Item("http://teste.com", id=1)
        self.assertDictEqual(
            item.to_json(), {"url": "http://teste.com", "id": 1})


class MongoStorageTest(unittest.TestCase):

    def remove_env(self, env):
        if env in os.environ:
            del os.environ[env]

    def setUp(self):
        self.storage = MongoStorage()
        self.url = "http://myurl.com"
        self.item = Item(self.url)
        self.user = User("id", "w@w.com", ["group_id"])
        self.healthcheck = HealthCheck("bla")

    @mock.patch("pymongo.MongoClient")
    def test_mongodb_host_environ(self, mongo_mock):
        self.storage.conn()
        mongo_mock.assert_called_with('mongodb://localhost:27017/')

        os.environ["MONGODB_URI"] = "mongodb://myhost:2222/"
        self.addCleanup(self.remove_env, "MONGODB_URI")
        storage = MongoStorage()
        storage.conn()
        mongo_mock.assert_called_with('mongodb://myhost:2222/')

    @mock.patch("pymongo.MongoClient")
    def test_mongodb_port_environ(self, mongo_mock):
        self.storage.conn()
        mongo_mock.assert_called_with('mongodb://localhost:27017/')

        os.environ["MONGODB_URI"] = "mongodb://myhost:2222/"
        self.addCleanup(self.remove_env, "MONGODB_URI")
        storage = MongoStorage()
        storage.conn()
        mongo_mock.assert_called_with('mongodb://myhost:2222/')

    def test_add_item(self):
        self.storage.add_item(self.item)
        result = self.storage.find_item_by_url(self.url)
        self.assertEqual(result.url, self.url)
        self.storage.remove_item(self.item)

    def test_find_item_by_url(self):
        self.storage.add_item(self.item)
        result = self.storage.find_item_by_url(self.item.url)
        for attr, value in result.__dict__.items():
            self.assertEqual(getattr(self.item, attr), value)
        self.storage.remove_item(self.item)

    def test_find_item_by_url_dont_exists(self):
        with self.assertRaises(ItemNotFoundError):
            self.storage.find_item_by_url("url-not-found.com")

    def test_find_url_by_healthcheck_name(self):
        self.healthcheck.group_id = 1
        self.storage.add_healthcheck(self.healthcheck)
        self.item.group_id = self.healthcheck.group_id
        self.storage.add_item(self.item)
        urls = self.storage.find_urls_by_healthcheck_name(
            self.healthcheck.name)
        self.assertEqual(urls[0], self.item.url)
        self.storage.remove_item(self.item)
        self.storage.remove_healthcheck(self.healthcheck)

    def test_find_watcher_by_healthcheck_name(self):
        self.healthcheck.group_id = 1
        self.storage.add_healthcheck(self.healthcheck)
        self.user.groups_id = [1]
        self.storage.add_user(self.user)
        watchers = self.storage.find_watchers_by_healthcheck_name(
            self.healthcheck.name)
        self.assertEqual(watchers[0], self.user.email)
        self.storage.remove_user(self.user)
        self.storage.remove_healthcheck(self.healthcheck)

    def test_remove_item(self):
        self.storage.add_item(self.item)
        result = self.storage.find_item_by_url(self.item.url)
        self.assertEqual(result.url, self.url)
        self.storage.remove_item(self.item)
        length = self.storage.conn()['hcapi']['items'].find(
            {"url": self.url}).count()
        self.assertEqual(length, 0)

    def test_add_user(self):
        self.storage.add_user(self.user)
        result = self.storage.find_user_by_email(self.user.email)
        self.assertEqual(result.email, self.user.email)
        self.storage.remove_user(self.user)

    def test_add_healthcheck(self):
        self.storage.add_healthcheck(self.healthcheck)
        result = self.storage.find_healthcheck_by_name(self.healthcheck.name)
        self.assertEqual(result.name, self.healthcheck.name)
        self.storage.remove_healthcheck(self.healthcheck)

    def test_remove_healthcheck(self):
        self.storage.add_healthcheck(self.healthcheck)
        result = self.storage.find_healthcheck_by_name(self.healthcheck.name)
        self.assertEqual(result.name, self.healthcheck.name)
        self.storage.remove_healthcheck(self.healthcheck)
        length = self.storage.conn()['hcapi']['healthchecks'].find(
            {"name": self.healthcheck.name}).count()
        self.assertEqual(length, 0)

    def test_find_healthcheck_by_name(self):
        self.storage.add_healthcheck(self.healthcheck)
        result = self.storage.find_healthcheck_by_name(self.healthcheck.name)
        self.assertEqual(result.name, self.healthcheck.name)
        self.storage.remove_healthcheck(self.healthcheck)

    def test_find_healthcheck_by_name_not_found(self):
        with self.assertRaises(HealthCheckNotFoundError):
            self.storage.find_healthcheck_by_name("doesn't exist")

    def test_remove_user(self):
        self.storage.add_user(self.user)
        result = self.storage.find_user_by_email(self.user.email)
        self.assertEqual(result.email, self.user.email)
        self.storage.remove_user(self.user)
        length = self.storage.conn()['hcapi']['users'].find(
            {"email": self.user.email}).count()
        self.assertEqual(length, 0)

    def test_find_user_by_email(self):
        self.storage.add_user(self.user)
        result = self.storage.find_user_by_email(self.user.email)
        self.assertEqual(result.email, self.user.email)
        self.storage.remove_user(self.user)

    def test_find_user_by_email_not_found(self):
        with self.assertRaises(UserNotFoundError):
            self.storage.find_user_by_email("something@otherthing.io")

    def test_find_users_by_group(self):
        user1 = User("id1", "w@w.com", "group_id1", "group_id2", "group_id3")
        user2 = User("id2", "e@w.com", "group_id2", "group_id3")
        user3 = User("id3", "f@w.com", "group_id3")
        self.storage.add_user(user1)
        self.addCleanup(self.storage.remove_user, user1)
        self.storage.add_user(user2)
        self.addCleanup(self.storage.remove_user, user2)
        self.storage.add_user(user3)
        self.addCleanup(self.storage.remove_user, user3)
        users = self.storage.find_users_by_group("group_id3")
        self.assertEqual([user1, user2, user3], users)
        users = self.storage.find_users_by_group("group_id2")
        self.assertEqual([user1, user2], users)
        users = self.storage.find_users_by_group("group_id1")
        self.assertEqual([user1], users)

    def test_include_user_in_group(self):
        user = User("userid", "w@w.com", "group1")
        self.storage.add_user(user)
        self.addCleanup(self.storage.remove_user, user)
        self.storage.add_user_to_group(user, "group2")
        self.storage.add_user_to_group(user, "group3")
        self.storage.add_user_to_group(user, "group4")
        self.storage.add_user_to_group(user, "group5")
        user = self.storage.find_user_by_email(user.email)
        self.assertEqual(("group1", "group2", "group3", "group4", "group5"),
                         user.groups_id)

    def test_remove_user_from_group(self):
        user = User("userid", "w@w.com", "group1")
        self.storage.add_user(user)
        self.addCleanup(self.storage.remove_user, user)
        self.storage.add_user_to_group(user, "group2")
        self.storage.add_user_to_group(user, "group3")
        self.storage.add_user_to_group(user, "group4")
        self.storage.add_user_to_group(user, "group5")
        self.storage.remove_user_from_group(user, "group4")
        self.storage.remove_user_from_group(user, "group3")
        user = self.storage.find_user_by_email(user.email)
        self.assertEqual(("group1", "group2", "group5"),
                         user.groups_id)

    def test_add_group_to_instance(self):
        self.storage.add_healthcheck(self.healthcheck)
        self.storage.add_group_to_instance(self.healthcheck, "group1")
        self.storage.add_group_to_instance(self.healthcheck, "group2")
        result = self.storage.find_healthcheck_by_name(self.healthcheck.name)
        self.assertEqual(["group1", "group2"], result.host_groups)
        self.storage.remove_healthcheck(self.healthcheck)

    def test_remove_group_from_instance(self):
        self.storage.add_healthcheck(self.healthcheck)
        self.storage.add_group_to_instance(self.healthcheck, "group1")
        self.storage.add_group_to_instance(self.healthcheck, "group2")
        self.storage.add_group_to_instance(self.healthcheck, "group3")
        self.storage.remove_group_from_instance(self.healthcheck, "group1")
        self.storage.remove_group_from_instance(self.healthcheck, "group2")
        result = self.storage.find_healthcheck_by_name(self.healthcheck.name)
        self.assertEqual(["group3"], result.host_groups)
        self.storage.remove_healthcheck(self.healthcheck)
