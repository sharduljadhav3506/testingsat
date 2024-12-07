from twilio.rest import Client
account_sid = 'AC4a4162cbb61436f7b36897ba1f150655'
auth_token = '97a1206c35505052d740bd056bf083d4'
client = Client(account_sid, auth_token)
message = client.messages.create(
  from_='+13345186487',
  body='hi',
  to='+818037023521'
)
print(message.sid)