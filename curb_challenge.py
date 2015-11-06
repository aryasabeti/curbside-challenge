import requests
import json
import itertools

def dict_keys_to_lower(d):
  return {str(key).lower():value for key, value in d.iteritems()}

def listify(list_or_single):
  is_list = isinstance(list_or_single, list)
  return list_or_single if is_list else [list_or_single]

def curb_api(endpoint, curb_headers = {}):
  return requests.get('http://challenge.shopcurbside.com/' + endpoint, headers = curb_headers).text

def session_generator():
  for i in itertools.count():
    if(i % 10 == 0):
      session = curb_api('get-session')
    yield session

sessions = session_generator()

def get_response(endpoint):
  response_text = curb_api(endpoint, {'session': sessions.next()})
  return dict_keys_to_lower(json.loads(response_text))

def get_secret(endpoint):
  response = get_response(endpoint)
  if('secret' in response):
    return response['secret']
  else:
    next_endpoints = listify(response['next'])
    return ''.join(map(get_secret, next_endpoints))

if __name__ == '__main__':
  print(get_secret('start'))
