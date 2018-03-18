# Curconvt

Тестовая работа по загрузке курсов валют и их онлайн конвертеру.

```python
import requests
import json
```
POST:
```python
print(requests.post('http://localhost:8764/', data=json.dumps({'from': 'eur', 'to': 'usd', 'amount': 1})).text)
```
GET:
```python
print(requests.get('http://localhost:8764/?from=USD&to=EUR&amount=1').text)
```
