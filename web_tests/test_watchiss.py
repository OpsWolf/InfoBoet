import ConfigParser

import telegram

import unittest
from google.appengine.ext import ndb
from google.appengine.ext import testbed

import telegram_commands.watchiss as watchiss

class TestWatchBitcoin(unittest.TestCase):
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

    def test_watchiss(self):
        requestText = '10000'

        keyConfig = ConfigParser.ConfigParser()
        keyConfig.read(["keys.ini", "..\keys.ini"])
        bot = telegram.Bot(keyConfig.get('Telegram', 'TELE_BOT_ID'))
        chatId = keyConfig.get('BotAdministration', 'TESTING_PRIVATE_CHAT_ID')

        #for bot group:
        #chatId = -130436192

        watchiss.run(bot, chatId, 'SalamiArmy', keyConfig, 'Durban')
        watchiss.run(bot, chatId, 'SalamiArmy', keyConfig, 'Mumbi')
        watchiss.unwatch(bot, chatId, 'Durban')
        watchiss.run(bot, chatId, 'SalamiArmy', keyConfig, 'Mumbi')
