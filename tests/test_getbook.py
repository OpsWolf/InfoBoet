# coding=utf-8
import ConfigParser
import unittest

import telegram

import telegram_commands.getbook as getbook
from google.appengine.ext import ndb
from google.appengine.ext import testbed

class TestGetBook(unittest.TestCase):
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_user_stub()
        # Clear ndb's in-context cache between tests.
        # This prevents data from leaking between tests.
        # Alternatively, you could disable caching by
        # using ndb.get_context().set_cache_policy(False)
        ndb.get_context().clear_cache()

    def test_getbook(self):
        requestText = u'dreamweaver'
        keyConfig = ConfigParser.ConfigParser()
        keyConfig.read(["keys.ini", "..\keys.ini"])
        bot = telegram.Bot(keyConfig.get('BotIDs', 'TELEGRAM_BOT_ID'))
        chatId = keyConfig.get('BotAdministration', 'TESTING_PRIVATE_CHAT_ID')

        bot.sendMessage(chat_id=chatId, text=getbook.run('Admin', requestText, chatId))

    def test_getbook_group(self):
        requestText = u'when balls do touch'
        keyConfig = ConfigParser.ConfigParser()
        keyConfig.read(["keys.ini", "..\keys.ini"])
        bot = telegram.Bot(keyConfig.get('Telegram', 'TELE_BOT_ID'))
        chatId = keyConfig.get('BotAdministration', 'TESTING_ALT_GROUP_CHAT_ID')

        bot.sendMessage(chat_id=chatId, text=getbook.run('Admin', requestText, chatId))
