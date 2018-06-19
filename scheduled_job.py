import os
from pymongo import MongoClient
from pywebpush import webpush, WebPushException
from pyfcm import FCMNotification
import json
import datetime
import sys
from bson.json_util import loads

push_service = None
connection = None
VAPID_PRIVATE_KEY = None
VAPID_PUBLIC_KEY = None
VAPID_CLAIMS = None
ADMIN_PASSWORD = None

if len(sys.argv) > 1 and sys.argv[1] == 'local':
    import LocalHostConst
    push_service = FCMNotification(api_key=LocalHostConst.FCM_API_KEY)
    connection = MongoClient(LocalHostConst.MONGO_URL)
    VAPID_PRIVATE_KEY = LocalHostConst.VAPID_PRIVATE_KEY
    VAPID_PUBLIC_KEY = LocalHostConst.VAPID_PUBLIC_KEY
    VAPID_CLAIMS = LocalHostConst.VAPID_CLAIMS
    ADMIN_PASSWORD = LocalHostConst.ADMIN_PASSWORD
else:
    push_service = FCMNotification(api_key=os.environ.get('FCM_API_KEY'))
    connection = MongoClient(os.environ.get('MONGODB_URI'))
    VAPID_PRIVATE_KEY = os.environ.get('VAPID_PRIVATE_KEY')
    VAPID_PUBLIC_KEY = os.environ.get('VAPID_PUBLIC_KEY')
    VAPID_CLAIMS = loads(os.environ.get('VAPID_CLAIMS'))
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

if datetime.datetime.today().weekday() == 5 or datetime.datetime.today().weekday() == 4:
    print("Wrong weekday: " + str(datetime.datetime.today().weekday()))
else:
    db = connection['flex-app']
    members = db.Members.find({})
    if members and members.count() > 0:
        for doc in members:
            if len(doc["subscription"])> 0:
                data_message = {
                    "title": "Morning Report",
                    "body": "Morning, What are u up to today?",
                }
                for sub in doc["subscription"]:
                    try:
                        webpush(sub, json.dumps(data_message), vapid_private_key=VAPID_PRIVATE_KEY,vapid_claims=VAPID_CLAIMS, timeout=10)
                    except WebPushException as ex:
                        print("subscription is offline")
                        db.Members.find_one_and_update({'name': doc['name'], 'email': doc['email']},
                                                        {"$pull": {"subscription": sub}})