import requests
import websocket
import sys
sys.path.insert(0, '/home/pi/rexana/')
import settings

CONVO_ID = None
DIRECT_LINE_SECRET = settings.direct_line_secret


def startConvo():
    start_convo = requests.post("https://directline.botframework.com/v3/directline/conversations",
                                headers={
                                    "Authorization": "Bearer %s" % DIRECT_LINE_SECRET
                                }).json()
    convoId = start_convo["conversationId"]
    convoStream = start_convo["streamUrl"]
    return {"convoId": convoId, "convoStream": convoStream}


def getReply(convoId, watermark):
    responseURL = "https://directline.botframework.com/v3/directline/conversations/%s/activities/?watermark=%s" % (
        convoId, watermark)
    get_msg = requests.get(responseURL,
                           headers={
                               "Authorization": "Bearer %s" % DIRECT_LINE_SECRET
                           }).json()
    print("add speech only response to sources")
    return get_msg['activities'][0]['text']


def sendMessage(convoId, message):
    print("Sending text: " + message)
    responseURL = "https://directline.botframework.com/v3/directline/conversations/%s/activities/" % (
        convoId)
    send_msg = requests.post(responseURL,
                             json={
                                 "type": "message",
                                 "from": {
                                     "id": "dan",
                                 },
                                 "text": message
                             },
                             headers={
                                 "Authorization": "Bearer %s" % DIRECT_LINE_SECRET
                             })
    response = send_msg.json()
    watermark = response['id'].split('|')[1]
    return getReply(convoId, watermark)


def endConvo(convoId):
    print("Add end convo call")


def getActivity(convoStream):
    ws = websocket.WebSocket()
    ws.connect(convoStream)
    result = ws.recv()
    print("Received '%s'" % result)


#reply = sendMessage(convoId, "what day is it?")
# print(reply)
# getActivity(convoStream)
