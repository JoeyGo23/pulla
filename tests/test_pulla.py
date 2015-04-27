#!/usr/bin/env python

from __future__ import print_function
from itertools import chain

try:
    import unittest
    import unittest.mock
    from unittest.mock import patch
    from unittest.mock import call
except ImportError as e:
    import mock
    from mock import patch
    from mock import call

from pulla.pulla import Pulla

@patch('os.walk')
@patch('pulla.pulla.is_this_a_git_dir')
@patch('multiprocessing.Process')
class test_pull_all(unittest.TestCase):

    def setUp(self):
        self.directories_folder = ('a', 'b', 'c')
        self.directory_sub_folder = ('d', 'e', 'f')

    def test_pull_all_starts_process_for_folders_in_passed_directory_when_not_recursive(self, mock_multiprocess, mock_is_git, mock_walk):
        mock_walk.return_value = [
            ('/foo', self.directories_folder, ('baz',)),
            ('/foo/bar', ('d', 'e', 'f'), ('spam', 'eggs')),
            ]
        mock_is_git.return_value = True

        puller = Pulla()
        puller.pull_all('foo')

        calls = [call('a'), call('b'), call('c')]
        mock_is_git.assert_has_calls(calls)

        calls_for_process_creation = self.get_calls_for_process_creation(
            self.directories_folder,
            puller
        )
        mock_multiprocess.assert_has_calls(calls_for_process_creation)

    def test_pull_all_starts_process_for_all_folders_when_recursive(self, mock_multiprocess, mock_is_git, mock_walk):
        mock_walk.return_value = [
            ('/foo', self.directories_folder, ('baz',)),
            ('/foo/bar', self.directory_sub_folder, ('spam', 'eggs')),
            ]
        mock_is_git.return_value = True

        puller = Pulla(recursive=True)
        puller.pull_all('foo')

        directories_to_be_pulled = self.directories_folder + self.directory_sub_folder

        calls_for_process_creation = self.get_calls_for_process_creation(
            directories_to_be_pulled,
            puller
        )
        mock_multiprocess.assert_has_calls(calls_for_process_creation)

    def get_calls_for_process_creation(self, directories_to_be_pulled, puller):
        '''
        :return: list with format
        [
            call(args=['dir1'], target=puller.do_pull_in),
            call().start(),
            call(args=['dir2'], target=puller.do_pull_in),
            call().start(),
        ]
        '''
        calls_for_process_creation = list(chain.from_iterable(
            (
                call(args=[dir], target=puller.do_pull_in),
                call().start()
            ) for dir in directories_to_be_pulled
        ))
        return calls_for_process_creation


@patch('pulla.pulla.Pulla.perform_git_pull')
class test_do_pull_in(unittest.TestCase):

    def setUp(self):
        self.directory = 'foo'
        self.puller = Pulla()

    def test_perform_git_pull_called_for_passed_directory(self, mock_perform_git_pull):
        self.puller.do_pull_in(self.directory)

        mock_perform_git_pull.assert_called_once_with(self.directory)

    @patch('pulla.pulla.Pulla.get_formatted_status_message')
    def test_status_success_when_git_command_successful(self, mock_get_formatted_status_message, mock_perform_git_pull):
        mock_perform_git_pull.return_value = 0

        self.puller.do_pull_in(self.directory)

        mock_get_formatted_status_message.assert_called_once_with(self.directory, 'Success')

    @patch('pulla.pulla.Pulla.get_formatted_status_message')
    def test_status_fail_when_git_command_successful(self, mock_get_formatted_status_message, mock_perform_git_pull):
        mock_perform_git_pull.return_value = 128

        self.puller.do_pull_in(self.directory)

        mock_get_formatted_status_message.assert_called_once_with(self.directory, 'Fail')


class test_perform_git_pull(unittest.TestCase):
    def setUp(self):
        self.directory = 'foo'
        self.puller = Pulla()

    @patch('os.system')
    def test_pull_done_silently_when_no_verbosity(self, mock_os_system_cmd):
        expected_status = 128
        mock_os_system_cmd.return_value = expected_status
        expected_cmd = 'git -C foo pull &> /dev/null'

        status = self.puller.perform_git_pull(self.directory)

        mock_os_system_cmd.assert_called_once_with(expected_cmd)
        self.assertEqual(status, expected_status)


class test_get_git_version(unittest.TestCase):
    def setUp(self):
        self.GIT_VERSION_RESPONSE = 'git version 2.2.2'
        self.puller = Pulla()

    @unittest.skip
    @patch.object('os.popen', 'read')
    def test_correct_git_version_returned(self, mock_popen):
        mock_popen.return_value = self.GIT_VERSION_RESPONSE

        git_version = self.puller.get_git_version()

        self.assertEqual(git_version, '2.2.2')

    @patch('os.popen')
    def test_opened_stream_is_closed(self, mock_popen):
        self.puller.get_git_version()

        calls = [
            call('git --version'),
            call().read(),
            call().close(),
        ]
        mock_popen.assert_has_calls(calls)


if __name__ == '__main__':
    unittest.main()