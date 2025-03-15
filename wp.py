# from pywa import WhatsApp

# wa = WhatsApp(
#     phone_id="610049645522741",
#     token="EAAQk9oWUtpoBO8isq8azFhQxsKTWOI8Bzr91MoC913X0yHCm7ebjrtkhAyUwMLZBsON4Qub01GTHOpDvZBhvlkWnWBnZBSHkvH7ZAmSu4FhJyiutPBUBDnVRbCiZBZBvDLPfmOjDv2CtWENZCJstgfA9y4ebShumzjZBH8r1qYvRqoGfi19HEmzcTk0cPOPmlXFqIaO5g3m2CqNGSEwdhRP4fpo1KRWrRMBIwuoZD"
# )

# message = wa.send_message(
#     to="787064008065",
#     text="Hello from PyWa!"
# )
# print(message)


import aiohttp
import json
import ssl
import certifi  # You may need to install this: pip install certifi

async def send_message(data, verify_ssl=True):
  headers = {
    "Content-type": "application/json",
    "Authorization": f"Bearer EAAQk9oWUtpoBO8isq8azFhQxsKTWOI8Bzr91MoC913X0yHCm7ebjrtkhAyUwMLZBsON4Qub01GTHOpDvZBhvlkWnWBnZBSHkvH7ZAmSu4FhJyiutPBUBDnVRbCiZBZBvDLPfmOjDv2CtWENZCJstgfA9y4ebShumzjZBH8r1qYvRqoGfi19HEmzcTk0cPOPmlXFqIaO5g3m2CqNGSEwdhRP4fpo1KRWrRMBIwuoZD",
    }
  
  # Configure SSL context with certificate verification if requested
  if verify_ssl:
    ssl_context = ssl.create_default_context(cafile=certifi.where())
  else:
    # Warning: This disables SSL verification and is NOT secure for production
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    print("WARNING: SSL verification disabled! Not secure for production use.")
  
  async with aiohttp.ClientSession() as session:
    url = "https://graph.facebook.com/v22.0/610049645522741/messages"
    try:
      async with session.post(url, data=data, headers=headers, ssl=ssl_context) as response:
        if response.status == 200:
          print("Status:", response.status)
          print("Content-type:", response.headers['content-type'])

          html = await response.text()
          print("Body:", html)
        else:
          print(f"Error status: {response.status}")
          error_text = await response.text()
          print(f"Error response: {error_text}")
    except aiohttp.ClientConnectorError as e:
      print('Connection Error', str(e))
    except Exception as e:
      print(f"Unexpected error: {str(e)}")

def get_text_message_input(recipient, text):
  return json.dumps({
    "messaging_product": "whatsapp",
    "preview_url": False,
    "recipient_type": "individual",
    "to": recipient,
    "type": "text",
    "text": {
        "body": text
    }
  })

import asyncio

data = get_text_message_input("787064008065", "Hello from PyWa!")
asyncio.run(send_message(data, verify_ssl=True))

# If using certifi doesn't work, you can try with verification disabled (for testing only)
# asyncio.run(send_message(data, verify_ssl=False))