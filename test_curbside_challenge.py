import pytest
import mock
import curb_challenge as cc

class TestDictKeysToLower:
  def test_empty(self):
    assert cc.dict_keys_to_lower({}) == {}

  def test_single_value(self):
    same = {'abc': 123}
    assert cc.dict_keys_to_lower(same) == same

  def test_single_uppercase_value(self):
    assert cc.dict_keys_to_lower({'ABC': 123}) == {'abc': 123}

  def test_lots(self):
    given = {'CaT':'mEoW', 'dOG': 'WOOf', 555: 324, '12!@$A%#*@(7': 555}
    expected = {'cat':'mEoW', 'dog': 'WOOf', '555': 324, '12!@$a%#*@(7': 555}
    assert cc.dict_keys_to_lower(given) == expected

class TestListify:
  def test_none(self):
    assert cc.listify(None) == [None]

  def test_empty(self):
    assert cc.listify([]) == []

  def test_single_str(self):
    assert cc.listify('x') == ['x']

  def test_single_num(self):
    assert cc.listify(1) == [1]

  def test_dict(self):
    assert cc.listify({}) == [{}]

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
    self.sessions.next()
    cc.curb_api.assert_called_once_with('get-session')

  def test_first_session(self):
    assert self.sessions.next() == 'session1-10'

  def test_persist_session(self):
    for i in xrange(10):
      assert self.sessions.next() == 'session1-10'

  def test_obtain_new_session(self):
    for i in xrange(10):
      self.sessions.next()
    assert self.sessions.next() == 'session11-20'

  def test_many_sessions(self):
    for i in xrange(10):
      assert self.sessions.next() == 'session1-10'
    for i in xrange(10):
      assert self.sessions.next() == 'session11-20'
    for i in xrange(10):
      assert self.sessions.next() == 'session21-30'

class TestGetResponse:
  def setup(self):
    self.example_response = '{"Any": "response"}'
    self.example_result = {'any': 'response'}
    cc.curb_api = mock.Mock(return_value = self.example_response)
    cc.sessions = mock.Mock()
    cc.sessions.next = mock.Mock(return_value = "session_id")

  def test_makes_curb_api_request(self):
    cc.get_response('endpoint_with_session')
    cc.curb_api.assert_called_with('endpoint_with_session', {'session': 'session_id'})

  def test_dict_response(self):
    assert type(cc.get_response('endpoint_with_session')) == dict

  def test_returned_value(self):
    assert cc.get_response('endpoint_with_session') == self.example_result
