# coding=utf-8
import chess
import chess.svg

def run(bot, chat_id, user, keyConfig, message, totalResults=1):
    return chess.svg.board(chess.Board('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'), coordinates=False)


