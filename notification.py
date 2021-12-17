import http.client, urllib
def notify():
  conn = http.client.HTTPSConnection("api.pushover.net:443")
  conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
      "token": "APP_TOKEN",
      "user": "USER_KEY",
      "message": "Bullotrons Soap Level is low",
    }), { "Content-type": "application/x-www-form-urlencoded" })
  conn.getresponse()
