import pytest
import mock
import curb_challenge as cc

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
  assert cc.dict_keys_to_lower(input) == expected

@pytest.mark.parametrize("input,expected", [
  (None, [None]),
  ([], []),
  ('x', ['x']),
  (1, [1]),
  ({}, [{}]),
])
def test_listify(input, expected):
  assert cc.listify(input) == expected

class TestCurbApi:
  def setup(self):
    response = mock.Mock()
    cc.requests.get = mock.Mock(return_value = response)

  def test_endpoint(self):
    cc.curb_api('any_endpoint')
    cc.requests.get.assert_called_once_with(
      'http://challenge.shopcurbside.com/any_endpoint',
      headers = {}
    )

  def test_endpoint_headers(self):
    headers = {'header_name': 'header_value'}
    cc.curb_api('any_endpoint', headers)
    cc.requests.get.assert_called_once_with(
      'http://challenge.shopcurbside.com/any_endpoint',
      headers = headers
    )

class TestSessionGenerator:
  def setup(self):
    cc.curb_api = mock.Mock(side_effect = ['session1-10', 'session11-20', 'session21-30'])

  def setup_method(self, method):
    self.sessions = cc.session_generator()

  def test_get_session(self):
    next(self.sessions)
    cc.curb_api.assert_called_once_with('get-session')

  def test_first_session(self):
    assert next(self.sessions) == 'session1-10'

  def test_persist_session(self):
    for i in range(10):
      assert next(self.sessions) == 'session1-10'

  def test_get_new_session(self):
    for i in range(10):
      next(self.sessions)
    assert next(self.sessions) == 'session11-20'

  def test_get_many_sessions(self):
    for i in range(10):
      assert next(self.sessions) == 'session1-10'
    for i in range(10):
      assert next(self.sessions) == 'session11-20'
    for i in range(10):
      assert next(self.sessions) == 'session21-30'

class TestGetResponse:
  def setup(self):
    self.example_response = '{"Any": "Response"}'
    self.example_result = {'any': 'Response'}
    cc.curb_api = mock.Mock(return_value = self.example_response)
    cc.sessions = mock.Mock()
    cc.sessions.__next__ = mock.Mock(return_value = 'session_id')

  def test_makes_curb_api_request(self):
    cc.get_response('endpoint_with_session')
    cc.curb_api.assert_called_with('endpoint_with_session', {'session': 'session_id'})

  def test_dict_response(self):
    assert type(cc.get_response('endpoint_with_session')) == dict

  def test_returned_value(self):
    assert cc.get_response('endpoint_with_session') == self.example_result
