# Copyright 2014 healthcheck-as-a-service authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import mock
import json
import os
import unittest

from healthcheck.plugin import (add_url, add_watcher, list_urls, command, main,
                                remove_watcher, remove_url, list_watchers, show_help,
                                add_group, remove_group, list_groups, list_service_groups)


class PluginTest(unittest.TestCase):

    def set_envs(self):
        os.environ["TSURU_TARGET"] = self.target = "https://cloud.tsuru.io/"
        os.environ["TSURU_TOKEN"] = self.token = "abc123"
        os.environ["TSURU_PLUGIN_NAME"] = self.plugin_name = "hc"

    def delete_envs(self):
        del os.environ["TSURU_TARGET"], os.environ["TSURU_TOKEN"], \
            os.environ["TSURU_PLUGIN_NAME"]

    def setUp(self):
        self.set_envs()

    def tearDown(self):
        self.delete_envs()

    @mock.patch("healthcheck.plugin.urlopen")
    @mock.patch("healthcheck.plugin.Request")
    def test_add_url(self, Request, urlopen):
        request = mock.Mock()
        Request.return_value = request

        result = mock.Mock()
        result.getcode.return_value = 201
        urlopen.return_value = result

        add_url("service_name", "name", "http://example.com/hc")

        Request.assert_called_with(
            self.target + 'services/service_name/proxy/name?callback=/resources/name/url',
        )
        request.add_data.assert_called_with(json.dumps({'url': 'http://example.com/hc'}))
        self.assertEqual(request.get_method(), 'POST')

        calls = [
            mock.call("Authorization", "bearer {}".format(self.token)),
            mock.call("Content-Type", "application/json"),
            mock.call("Accept", "text/plain"),
        ]
        self.assertEqual(calls, request.add_header.call_args_list)
        urlopen.assert_called_with(request, timeout=30)

    @mock.patch("healthcheck.plugin.urlopen")
    @mock.patch("healthcheck.plugin.Request")
    def test_add_url_with_expected_string_args(self, Request, urlopen):
        request = mock.Mock()
        Request.return_value = request

        result = mock.Mock()
        result.getcode.return_value = 201
        urlopen.return_value = result

        add_url("service_name", "name", "http://example.com/hc", "WORKING")

        Request.assert_called_with(
            self.target + 'services/service_name/proxy/name?callback=/resources/name/url',
        )
        request.add_data.assert_called_with(json.dumps({'url': 'http://example.com/hc',
                                                        'expected_string': 'WORKING'}))
        self.assertEqual(request.get_method(), 'POST')

        calls = [
            mock.call("Authorization", "bearer {}".format(self.token)),
            mock.call("Content-Type", "application/json"),
            mock.call("Accept", "text/plain"),
        ]
        self.assertEqual(calls, request.add_header.call_args_list)
        urlopen.assert_called_with(request, timeout=30)

    @mock.patch("healthcheck.plugin.urlopen")
    @mock.patch("healthcheck.plugin.Request")
    def test_add_url_with_comment_args(self, Request, urlopen):
        request = mock.Mock()
        Request.return_value = request

        result = mock.Mock()
        result.getcode.return_value = 201
        urlopen.return_value = result

        add_url("service_name", "name", "http://example.com/hc", comment="http://test.com")

        Request.assert_called_with(
            self.target + 'services/service_name/proxy/name?callback=/resources/name/url',
        )
        request.add_data.assert_called_with(json.dumps({'url': 'http://example.com/hc',
                                                        'comment': 'http://test.com'}))
        self.assertEqual(request.get_method(), 'POST')

        calls = [
            mock.call("Authorization", "bearer {}".format(self.token)),
            mock.call("Content-Type", "application/json"),
            mock.call("Accept", "text/plain"),
        ]
        self.assertEqual(calls, request.add_header.call_args_list)
        urlopen.assert_called_with(request, timeout=30)

    @mock.patch("healthcheck.plugin.urlopen")
    @mock.patch("healthcheck.plugin.Request")
    def test_list_urls(self, Request, urlopen):
        request = mock.Mock()
        Request.return_value = request

        response = mock.Mock()
        response.read.return_value = json.dumps([['http://test.com', ""]])
        response.getcode.return_value = 200
        urlopen.return_value = response

        list_urls("service_name", "name")

        Request.assert_called_with(
            self.target + 'services/service_name/proxy/name?callback=/resources/name/url',
        )
        request.add_data.assert_not_called()
        self.assertEqual(request.get_method(), 'GET')

        calls = [
            mock.call("Authorization", "bearer {}".format(self.token)),
            mock.call("Content-Type", "application/json"),
        ]
        self.assertEqual(calls, request.add_header.call_args_list)
        urlopen.assert_called_with(request, timeout=30)

    @mock.patch("healthcheck.plugin.urlopen")
    @mock.patch("healthcheck.plugin.Request")
    def test_remove_url(self, Request, urlopen):
        request = mock.Mock()
        Request.return_value = request

        result = mock.Mock()
        result.getcode.return_value = 204
        urlopen.return_value = result

        remove_url("service_name", "name", "url")

        Request.assert_called_with(
            self.target + 'services/service_name/proxy/name?callback=/resources/name/url',
        )
        request.add_data.assert_called_with(json.dumps({"url": "url"}))
        self.assertEqual(request.get_method(), 'DELETE')

        calls = [
            mock.call("Authorization", "bearer " + self.token),
            mock.call("Content-Type", "application/json"),
        ]
        self.assertEqual(calls, request.add_header.call_args_list)
        urlopen.assert_called_with(request, timeout=30)

    @mock.patch("healthcheck.plugin.urlopen")
    @mock.patch("healthcheck.plugin.Request")
    def test_add_watcher(self, Request, urlopen):
        request = mock.Mock()
        Request.return_value = request

        result = mock.Mock()
        result.getcode.return_value = 201
        urlopen.return_value = result

        add_watcher("service_name", "name", "watcher@watcher.com")

        Request.assert_called_with(
            self.target + 'services/service_name/proxy/name?callback=/resources/name/watcher',
        )
        request.add_data.assert_called_with(json.dumps({'watcher': 'watcher@watcher.com'}))
        self.assertEqual(request.get_method(), 'POST')

        calls = [
            mock.call("Authorization", "bearer " + self.token),
            mock.call("Content-Type", "application/json"),
            mock.call("Accept", "text/plain"),
        ]
        request.add_header.has_calls(calls)
        urlopen.assert_called_with(request, timeout=30)

    @mock.patch("healthcheck.plugin.urlopen")
    @mock.patch("healthcheck.plugin.Request")
    def test_add_watcher_with_password(self, Request, urlopen):
        request = mock.Mock()
        Request.return_value = request

        result = mock.Mock()
        result.getcode.return_value = 201
        urlopen.return_value = result

        add_watcher("service_name", "name", "watcher@watcher.com", "teste")

        Request.assert_called_with(
            self.target + 'services/service_name/proxy/name?callback=/resources/name/watcher',
        )
        request.add_data.assert_called_with(json.dumps({'watcher': 'watcher@watcher.com', 'password': 'teste'}))
        self.assertEqual(request.get_method(), 'POST')

        calls = [
            mock.call("Authorization", "bearer " + self.token),
            mock.call("Content-Type", "application/json"),
            mock.call("Accept", "text/plain"),
        ]
        request.add_header.has_calls(calls)
        urlopen.assert_called_with(request, timeout=30)

    @mock.patch("healthcheck.plugin.urlopen")
    @mock.patch("healthcheck.plugin.Request")
    def test_remove_watcher(self, Request, urlopen):
        request = mock.Mock()
        Request.return_value = request

        result = mock.Mock()
        result.getcode.return_value = 204
        urlopen.return_value = result

        remove_watcher("service_name", "name", "watcher@watcher.com")

        uri = 'services/service_name/proxy/name?callback=/resources/name/watcher/watcher@watcher.com'
        Request.assert_called_with(
            self.target + uri,
        )
        request.add_data.assert_not_called()
        self.assertEqual(request.get_method(), 'DELETE')
        request.add_header.assert_called_with("Authorization",
                                              "bearer " + self.token)
        urlopen.assert_called_with(request, timeout=30)

    @mock.patch("healthcheck.plugin.urlopen")
    @mock.patch("healthcheck.plugin.Request")
    def test_list_watchers(self, Request, urlopen):
        request = mock.Mock()
        Request.return_value = request

        response = mock.Mock()
        response.read.return_value = json.dumps(['bla@test.com'])
        response.getcode.return_value = 200
        urlopen.return_value = response

        list_watchers("service_name", "name")

        Request.assert_called_with(
            self.target + 'services/service_name/proxy/name?callback=/resources/name/watcher',
        )
        request.add_data.assert_not_called()
        self.assertEqual(request.get_method(), 'GET')

        calls = [
            mock.call("Authorization", "bearer {}".format(self.token)),
            mock.call("Content-Type", "application/json"),
        ]
        self.assertEqual(calls, request.add_header.call_args_list)
        urlopen.assert_called_with(request, timeout=30)

    @mock.patch("healthcheck.plugin.urlopen")
    @mock.patch("healthcheck.plugin.Request")
    def test_add_group(self, Request, urlopen):
        request = mock.Mock()
        Request.return_value = request

        result = mock.Mock()
        result.getcode.return_value = 201
        urlopen.return_value = result

        add_group("service_name", "name", "group")

        Request.assert_called_with(
            self.target + 'services/service_name/proxy/name?callback=/resources/name/groups',
        )
        request.add_data.assert_called_with(json.dumps({"group": "group"}))
        self.assertEqual(request.get_method(), 'POST')

        calls = [
            mock.call("Authorization", "bearer " + self.token),
            mock.call("Content-Type", "application/json"),
            mock.call("Accept", "text/plain"),
        ]
        request.add_header.has_calls(calls)
        urlopen.assert_called_with(request, timeout=30)

    @mock.patch("healthcheck.plugin.urlopen")
    @mock.patch("healthcheck.plugin.Request")
    def test_remove_group(self, Request, urlopen):
        request = mock.Mock()
        Request.return_value = request

        result = mock.Mock()
        result.getcode.return_value = 204
        urlopen.return_value = result

        remove_group("service_name", "name", "group")

        uri = 'services/service_name/proxy/name?callback=/resources/name/groups'
        Request.assert_called_with(
            self.target + uri,
        )
        request.add_data.assert_called_with(json.dumps({"group": "group"}))
        self.assertEqual(request.get_method(), 'DELETE')

        calls = [
            mock.call("Authorization", "bearer " + self.token),
            mock.call("Content-Type", "application/json"),
        ]
        self.assertEqual(calls, request.add_header.call_args_list)
        urlopen.assert_called_with(request, timeout=30)

    @mock.patch("healthcheck.plugin.urlopen")
    @mock.patch("healthcheck.plugin.Request")
    def test_list_groups(self, Request, urlopen):
        request = mock.Mock()
        Request.return_value = request

        response = mock.Mock()
        response.read.return_value = json.dumps(['group'])
        response.getcode.return_value = 200
        urlopen.return_value = response

        list_groups("service_name", "name")

        Request.assert_called_with(
            self.target + 'services/service_name/proxy/name?callback=/resources/name/groups',
        )
        request.add_data.assert_not_called()
        self.assertEqual(request.get_method(), 'GET')

        calls = [
            mock.call("Authorization", "bearer {}".format(self.token)),
            mock.call("Content-Type", "application/json"),
        ]
        self.assertEqual(calls, request.add_header.call_args_list)
        urlopen.assert_called_with(request, timeout=30)

    @mock.patch("healthcheck.plugin.urlopen")
    @mock.patch("healthcheck.plugin.Request")
    def test_list_service_groups(self, Request, urlopen):
        request = mock.Mock()
        Request.return_value = request

        response = mock.Mock()
        response.read.return_value = json.dumps(['group', 'othergroup'])
        response.getcode.return_value = 200
        urlopen.return_value = response

        list_service_groups("service_name", "name")

        Request.assert_called_with(
            self.target + 'services/service_name/proxy/name?callback=/resources/name/servicegroups',
        )
        request.add_data.assert_not_called()
        self.assertEqual(request.get_method(), 'GET')

        calls = [
            mock.call("Authorization", "bearer {}".format(self.token)),
            mock.call("Content-Type", "application/json"),
        ]
        self.assertEqual(calls, request.add_header.call_args_list)
        urlopen.assert_called_with(request, timeout=30)

    @mock.patch("healthcheck.plugin.urlopen")
    @mock.patch("healthcheck.plugin.Request")
    def test_list_service_groups_keyword(self, Request, urlopen):
        request = mock.Mock()
        Request.return_value = request

        response = mock.Mock()
        response.read.return_value = json.dumps(['group', 'othergroup'])
        response.getcode.return_value = 200
        urlopen.return_value = response

        list_service_groups("service_name", "name", "other")

        Request.assert_called_with(
            self.target + 'services/service_name/proxy/name?callback=/resources/name/servicegroups?keyword=other',
        )
        request.add_data.assert_not_called()
        self.assertEqual(request.get_method(), 'GET')

        calls = [
            mock.call("Authorization", "bearer {}".format(self.token)),
            mock.call("Content-Type", "application/json"),
        ]
        self.assertEqual(calls, request.add_header.call_args_list)
        urlopen.assert_called_with(request, timeout=30)

    @mock.patch("sys.stderr")
    def test_help(self, stderr):
        with self.assertRaises(SystemExit) as cm:
            show_help("add-url")
        exc = cm.exception
        self.assertEqual(0, exc.code)
        doc = add_url.__doc__.format(plugin_name="hc")
        stderr.write.assert_called_with(doc.rstrip() + "\n")

    @mock.patch("sys.stderr")
    def test_help_with_exit_code(self, stderr):
        with self.assertRaises(SystemExit) as cm:
            show_help("add-watcher", exit=2)
        exc = cm.exception
        self.assertEqual(2, exc.code)
        doc = add_watcher.__doc__.format(plugin_name="hc")
        stderr.write.assert_called_with(doc.rstrip() + "\n")

    def test_commands(self):
        expected_commands = {
            "add-url": add_url,
            "add-watcher": add_watcher,
            "remove-url": remove_url,
            "remove-watcher": remove_watcher,
        }
        for key, cmd in expected_commands.items():
            self.assertEqual(command(key), cmd)

    @mock.patch("sys.stderr")
    def test_command_not_found(self, stderr):
        with self.assertRaises(SystemExit) as cm:
            command("waaaat")
        exc = cm.exception
        self.assertEqual(2, exc.code)
        calls = [
            mock.call("Usage: tsuru hc command [args]\n\n"),
            mock.call("Available commands:\n"),
            mock.call("  add-group\n"),
            mock.call("  add-url\n"),
            mock.call("  add-watcher\n"),
            mock.call("  list-groups\n"),
            mock.call("  list-service-groups\n"),
            mock.call("  list-urls\n"),
            mock.call("  list-watchers\n"),
            mock.call("  remove-group\n"),
            mock.call("  remove-url\n"),
            mock.call("  remove-watcher\n"),
            mock.call("  help\n"),
            mock.call("\nUse tsuru hc help <commandname> to"
                      " get more details.\n"),
        ]
        self.assertEqual(calls, stderr.write.call_args_list)

    @mock.patch("healthcheck.plugin.add_url")
    def test_main(self, add_url_mock):
        main("add-url", "myhc", "http://tsuru.io")
        add_url_mock.assert_called_with("myhc", "http://tsuru.io")

    @mock.patch("healthcheck.plugin.show_help")
    def test_main_wrong_params(self, show_help_mock):
        main("add-url name")
        show_help_mock.assert_called_with("add-url name", exit=2)
