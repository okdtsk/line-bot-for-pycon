#!/usr/bin/env python

import logging
import os
import random
from urllib.parse import parse_qs

from chalice import Chalice
from chalice import Response

from linebot import LineBotApi
from linebot import WebhookHandler

from linebot.models import MessageEvent
from linebot.models import PostbackEvent
from linebot.models import TextMessage
from linebot.models import ImageMessage
from linebot.models import AudioMessage
from linebot.models import VideoMessage
from linebot.models import LocationMessage
from linebot.models import StickerMessage
from linebot.models import TextSendMessage
from linebot.models import StickerSendMessage
from linebot.models import TemplateSendMessage

from linebot.models import ButtonsTemplate
from linebot.models import PostbackTemplateAction
from linebot.models import MessageTemplateAction
from linebot.models import URITemplateAction

from linebot.exceptions import InvalidSignatureError
from linebot.exceptions import LineBotApiError

app = Chalice(app_name='line-bot')
app.log.setLevel(logging.DEBUG)

line_bot_api = LineBotApi(os.environ['LINEBOT_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINEBOT_CHANNEL_SECRET'])


@app.route('/')
def index():
    return {'running': 'ok'}


@app.route('/callback', methods=['POST'])
def callback():
    try:
        signature = app.current_request.headers['X-Line-Signature']
    except KeyError as e:
        app.log.error('Missing X-Line-Signature header')
        return Response({'ok': False, 'error': 'Missing X-Line-Signature header'}, status_code=500)
    body = app.current_request.raw_body.decode('utf-8')
    app.log.debug('Request body: {}'.format(body))
    try:
        handler.handle(body, signature)
    except InvalidSignatureError as e:
        app.log.error(e.message)
        return Response({'ok': False, 'error': e.message}, status_code=400)
    except LineBotApiError as e:
        app.log.error('Failed to call line bot api {}'.format(e))
        return Response({'ok': False, 'error': 'Failed to call line bot api {}'.format(e)}, status_code=500)
    except Exception as e:
        app.log.error(e)
        return Response({'ok': False, 'error': e}, status_code=500)

    return Response({'ok': True})


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    if event.reply_token in ('00000000000000000000000000000000', 'ffffffffffffffffffffffffffffffff'):
        # Ignore a request for verification (when pressing 'VERIFY' button in developers console)
        return
    if event.message.text == 'a':
        reply_event = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                thumbnail_image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Tel_aviv_long_exposure_public_domain_3.jpg/1024px-Tel_aviv_long_exposure_public_domain_3.jpg',
                title='Menu',
                text='Please select',
                actions=[
                    PostbackTemplateAction(
                        label='postback',
                        data='action=buy&itemid=1'
                    ),
                    MessageTemplateAction(
                        label='message',
                        text='message text'
                    ),
                    URITemplateAction(
                        label='uri',
                        uri='http://okdtsk.info'
                    )
                ]
            )
        )
    else:
        reply_event = TextSendMessage(text='Reply to {}'.format(event.message.text))
    line_bot_api.reply_message(
        event.reply_token,
        reply_event
    )


@handler.add(PostbackEvent)
def handle_postback(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Postback {}'.format(parse_qs(event.postback.data)))
    )


STICKERS = [(2, 18),
            (1, 17),
            (1, 424),
            (2, 165),
            (2, 39)]


@handler.add(MessageEvent, message=StickerMessage)
@handler.add(MessageEvent, message=LocationMessage)
@handler.add(MessageEvent, message=ImageMessage)
@handler.add(MessageEvent, message=VideoMessage)
@handler.add(MessageEvent, message=AudioMessage)
def handle_default(event):
    sticker = random.choice(STICKERS)
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(package_id=sticker[0], sticker_id=sticker[1])
    )
