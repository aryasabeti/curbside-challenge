import pytest
import mock

import curbside_challenge
from curbside_challenge import dict_keys_to_lower
from curbside_challenge import listify
from curbside_challenge import curb_api
from curbside_challenge import session_generator
from curbside_challenge import get_response
from curbside_challenge import get_secret

#helpers
@pytest.mark.parametrize("input,expected", [
  ({}, {}),
  ({'abc': 123}, {'abc': 123}),
  ({'ABC': 123}, {'abc': 123}),
  (
    {'CaT':'mEoW', 'dOG': 'WOOf', 555: 555, '12!@$A%#*@(7': 555},
    {'cat':'mEoW', 'dog': 'WOOf', '555': 555, '12!@$a%#*@(7': 555}
  ),
])
def test_dict_keys_to_lower(input, expected):
  assert dict_keys_to_lower(input) == expected

@pytest.mark.parametrize("input,expected", [
  (None, [None]),
  ([], []),
  ('x', ['x']),
  (1, [1]),
  ({}, [{}]),
])
def test_listify(input, expected):
  assert listify(input) == expected


class TestCurbApi:
  @mock.patch('curbside_challenge.requests')
  def test_endpoint(self, requests_):
    curb_api('any_endpoint')
    curbside_challenge.requests.get.assert_called_once_with(
      'http://challenge.shopcurbside.com/any_endpoint',
      headers = {}
    )

  @mock.patch('curbside_challenge.requests')
  def test_endpoint_headers(self, requests_mock):
    headers = {'header_name': 'header_value'}
    curb_api('any_endpoint', headers)
    requests_mock.get.assert_called_once_with(
      'http://challenge.shopcurbside.com/any_endpoint',
      headers = headers
    )

class TestSessionGenerator:
  def setup_method(self, method):
    self.sessions = session_generator()

  @mock.patch('curbside_challenge.curb_api')
  def test_get_session(self, curb_api_mock):
    next(self.sessions)
    curb_api_mock.assert_called_once_with('get-session')

  @mock.patch('curbside_challenge.curb_api', side_effect = ['session1-10', 'session11-20', 'session21-30'])
  def test_first_session(self, curb_api_mock):
    assert next(self.sessions) == 'session1-10'

  @mock.patch('curbside_challenge.curb_api', side_effect = ['session1-10', 'session11-20', 'session21-30'])
  def test_persist_session(self, curb_api_mock):
    for i in range(10):
      assert next(self.sessions) == 'session1-10'

  @mock.patch('curbside_challenge.curb_api', side_effect = ['session1-10', 'session11-20', 'session21-30'])
  def test_get_new_session(self, curb_api_mock):
    for i in range(10):
      next(self.sessions)
    assert next(self.sessions) == 'session11-20'

  @mock.patch('curbside_challenge.curb_api', side_effect = ['session1-10', 'session11-20', 'session21-30'])
  def test_get_many_sessions(self, curb_api_mock):
    for i in range(10):
      assert next(self.sessions) == 'session1-10'
    for i in range(10):
      assert next(self.sessions) == 'session11-20'
    for i in range(10):
      assert next(self.sessions) == 'session21-30'

class TestGetResponse:
  @mock.patch('curbside_challenge.sessions')
  @mock.patch('curbside_challenge.curb_api', return_value = '{"Any": "Response"}')
  def test_makes_curb_api_request(self, curb_api_mock, sessions_mock):
    sessions_mock.__next__ = mock.Mock(return_value = 'session_id')
    get_response('endpoint_with_session')
    curb_api_mock.assert_called_with('endpoint_with_session', {'session': 'session_id'})

  @mock.patch('curbside_challenge.sessions')
  @mock.patch('curbside_challenge.curb_api', return_value = '{"Any": "Response"}')
  def test_dict_response(self, curb_api_mock, sessions_mock):
    sessions_mock.__next__ = mock.Mock(return_value = 'session_id')
    assert type(get_response('endpoint_with_session')) == dict

  @mock.patch('curbside_challenge.sessions')
  @mock.patch('curbside_challenge.curb_api', return_value = '{"Any": "Response"}')
  def test_returned_value(self, curb_api_mock, sessions_mock):
    sessions_mock.__next__ = mock.Mock(return_value = 'session_id')
    assert get_response('endpoint_with_session') == {'any': 'Response'}

@pytest.mark.parametrize("api_response,expected", [
  (
    [
      {'secret': 'asecret'}
    ],
    'asecret'
  ),

  (
    [
      {'next': 'next_endpoint1'},
      {'secret': 'anothersecret'}
    ],
    'anothersecret'
  ),

  (
    [
      {'next': ['next_endpoint2', 'next_endpoint3']},
      {'secret': 'yetagainsecret'}
    ],
    'yetagainsecret'
  ),
])
def test_get_secret(api_response, expected):
  with mock.patch('curbside_challenge.get_response', side_effect = api_response) as get_response_mock:
    assert get_secret('any_endpoint') == expected
