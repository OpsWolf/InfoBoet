# coding=utf-8
import string

from google.appengine.ext import ndb

import main
bitcoin = main.load_code_as_module('bitcoin')

watchedCommandName = 'bitcoin'


class BitcoinWatchValue(ndb.Model):
    # key name: str(chat_id)
    currentValue = ndb.StringProperty(indexed=False, default='')
    all_chat_ids = ndb.StringProperty(indexed=False, default='')


# ================================

def setWatchValue(chat_id, request_text, NewValue):
    es = BitcoinWatchValue.get_or_insert(watchedCommandName + ':' + str(chat_id))
    es.currentValue = NewValue + (':' + str(request_text) if str(request_text) != '' else '')
    es.put()


def getWatchValue(chat_id):
    es = BitcoinWatchValue.get_by_id(watchedCommandName + ':' + str(chat_id))
    if es:
        return es.currentValue
    return ''

def addToAllWatches(chat_id):
    es = BitcoinWatchValue.get_or_insert(watchedCommandName + ':' + 'AllWatchers')
    es.all_chat_ids += ',' + str(chat_id)
    es.put()

def AllWatchesContains(chat_id):
    es = BitcoinWatchValue.get_by_id(watchedCommandName + ':' + 'AllWatchers')
    if es:
        return (',' + str(chat_id)) in str(es.all_chat_ids) or \
               (str(chat_id) + ',') in str(es.all_chat_ids)
    return False

def setAllWatchesValue(NewValue):
    es = BitcoinWatchValue.get_or_insert(watchedCommandName + ':' + 'AllWatchers')
    es.all_chat_ids = NewValue
    es.put()

def getAllWatches():
    es = BitcoinWatchValue.get_by_id(watchedCommandName + ':' + 'AllWatchers')
    if es:
        return es.all_chat_ids
    return ''

def removeFromAllWatches(watch):
    setAllWatchesValue(getAllWatches().replace(',' + watch + ',', ',')
                       .replace(',' + watch, '')
                       .replace(watch + ',', ''))


def run(bot, chat_id, user, keyConfig, message, totalResults=1):
    requestText = str(message).replace(bot.name, '')
    if requestText:
        priceGB, priceUS, new_price, updateTime = bitcoin.get_bitcoin_prices()
        if new_price:
            OldValue = getWatchValue(chat_id)
            float_ready_new_price = new_price.replace(',', '')
            new_price_float = float(float_ready_new_price)
            OldValue, old_price_float = parse_old_price_float(OldValue, bot, chat_id, requestText)
            price_diff = new_price_float - old_price_float
            setWatchValue(chat_id, requestText, new_price)
            formatted_price = 'The Current Price of 1 Bitcoin:\n\n' + priceUS + ' USD\n' + priceGB + ' GBP\n' + new_price + ' ZAR' + '\n\nTime Updated: ' + updateTime
            if OldValue == '' and requestText == '' and user != 'Watcher':
                bot.sendMessage(chat_id=chat_id,
                                text='Now watching /' + watchedCommandName + ' ' + requestText + '\n' + formatted_price)
            elif OldValue == '' and (requestText[:1] == '+' or requestText[:1] == '-') and user != 'Watcher':
                bot.sendMessage(chat_id=chat_id,
                                text='Now watching /' + watchedCommandName + ' changes by ' + requestText + '\n' + formatted_price)
            elif OldValue == '' and requestText[:1] != '+' and requestText[:1] != '-' and user != 'Watcher':
                bot.sendMessage(chat_id=chat_id,
                                text='Now watching /' + watchedCommandName + ' drops below threshold of ' + requestText + '\n' + formatted_price)
            elif old_price_float != new_price_float and requestText == '' and user != 'Watcher':
                if OldValue != '':
                    bot.sendMessage(chat_id=chat_id,
                                    text='Watch for /' + watchedCommandName + ' ' + requestText + ' has changed by ' + str(price_diff) + ' ZAR:\n' + formatted_price)
            elif old_price_float != new_price_float and requestText == '':
                    bot.sendMessage(chat_id=chat_id,
                                    text='Watched /' + watchedCommandName + ' ' + requestText + ' changed by ' + str(price_diff) + ' ZAR:\n' + formatted_price)
            elif price_diff > float(requestText) and requestText[:1] == '+':
                bot.sendMessage(chat_id=chat_id,
                                text='Watch for /' + watchedCommandName + ' has jumped by ' + str(price_diff) +
                                     ' ZAR. Which is higher than the tolerance of ' + requestText + ':\n' + formatted_price)
            elif price_diff < float(requestText) and requestText[:1] == '-':
                bot.sendMessage(chat_id=chat_id,
                                text='Watch for /' + watchedCommandName + ' has dropped by ' + str(price_diff) +
                                     ' ZAR. Which is lower than the tolerance of ' + requestText + ':\n' + formatted_price)
            elif new_price_float < float(requestText) and (requestText[:1] != '+' and requestText[:1] != '-'):
                bot.sendMessage(chat_id=chat_id,
                                text='Watch for /' + watchedCommandName + ' has dropped below ' + requestText + ' ZAR:\n' + formatted_price)
            else:
                if user != 'Watcher':
                    if requestText == '':
                        bot.sendMessage(chat_id=chat_id,
                                        text='Watch for /' + watchedCommandName + ' has not changed.\n' + formatted_price)
                    elif requestText[:1] == '+' or requestText[:1] == '-':
                        bot.sendMessage(chat_id=chat_id,
                                        text='Watch for /' + watchedCommandName + ' has changed by ' + str(price_diff) +
                                             ' ZAR. Which is not ' + ('higher' if requestText[:1] == '+' else 'lower') + ' than the tolerance of ' + requestText + ':\n' + formatted_price)
                    elif requestText[:1] != '+' and requestText[:1] != '-':
                        bot.sendMessage(chat_id=chat_id,
                                        text='Watch for /' + watchedCommandName + ' has not dropped below ' + requestText + ' ZAR:\n' + formatted_price)
            if not AllWatchesContains(chat_id):
                addToAllWatches(chat_id)
        else:
            bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                  ', I\'m afraid I can\'t watch ' +
                                                  'because I did not find any results from /bitcoin')
    else:
        bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                              ', I\'m afraid I can\'t watch ' +
                                              'because you need to provide a threshold. E.g.: /watchbitcoin 30000')


def parse_old_price_float(OldValue, bot, chat_id, message):
    if OldValue != '':
        split_OldValue = OldValue.split(':')
        old_price = split_OldValue[0] if len(split_OldValue) == 2 else OldValue
        float_ready_old_price = old_price.replace(',', '')
        old_request_text = split_OldValue[1] if len(split_OldValue) == 2 else ''
        if old_request_text != message:
            unwatch(bot, chat_id, old_request_text)
            OldValue = ''
    else:
        float_ready_old_price = '0.0'
    old_price_float = float(float_ready_old_price)
    return OldValue, old_price_float


def unwatch(bot, chat_id, message, sendmessage=False):
    if AllWatchesContains(chat_id):
        removeFromAllWatches(chat_id)
        if sendmessage:
            bot.sendMessage(chat_id=chat_id, text='Watch for /' + watchedCommandName + ' ' + message + ' has been removed.')
    else:
        if sendmessage:
            bot.sendMessage(chat_id=chat_id, text='Watch for /' + watchedCommandName + ' ' + message + ' not found.')
    if getWatchValue(chat_id) != '':
        setWatchValue(chat_id, '', '')
