import urllib.request, urllib.error, json
req = urllib.request.Request('http://127.0.0.1:8000/api/auth/signup', data=json.dumps({'email':'user200@example.com','password':'supersecretpassword','first_name':'Test','last_name':'User'}).encode(), headers={'Content-Type':'application/json'})
try:
    urllib.request.urlopen(req)
except urllib.error.HTTPError as e:
    print('STATUS:', e.code, 'BODY:', e.read().decode())
