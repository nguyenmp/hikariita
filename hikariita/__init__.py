# -*- coding: utf-8 -*-

'''
This module is an application for flashcarding Japanese.
'''

from __future__ import unicode_literals

import sqlite3

from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    g,
)

from . import db


APP = Flask(__name__)


def get_db():
    '''
    Returns the cached database connection
    '''
    if 'db' not in g:
        g.db = sqlite3.connect('example.db')
    return g.db



@APP.route('/', methods=['GET'])
def index():
    '''
    Home page
    '''
    return "Welcome!"


@APP.route('/cards/', methods=['GET'])
def cards():
    '''
    The index of cards, redirects to an instance of a random card
    '''
    card_id = db.get_random_card_id(get_db().cursor())
    APP.logger.debug('Type 1: %s', type(card_id))
    return redirect(url_for('card', card_id=card_id))


@APP.route('/cards/<string:card_id>/', methods=['GET'])
def card(card_id):
    '''
    Renders a single flash-card on screen
    '''
    APP.logger.debug('Type: %s', type(card_id))
    cursor = get_db().cursor()
    attributes = db.get_card_attributes(cursor, card_id)
    kanji = None
    hiragana = None
    meaning = None
    others = []

    for attribute in attributes:
        if attribute[1] == 'kanji':
            kanji = attribute[2]
        elif attribute[1] == 'hiragana':
            hiragana = attribute[2]
        elif attribute[1] == 'meaning':
            meaning = attribute[2]
        else:
            others.append((attribute[1], attribute[2]))
    return render_template(
        'card.html',
        kanji=kanji,
        hiragana=hiragana,
        meaning=meaning,
        others=others,
    )


@APP.route('/cards/<int:card_id>/vote', methods=['POST'])
def vote(card_id):
    '''
    Gives a vote to the given card and redirects to the next card
    '''
    # TODO: Set vote for card
    return redirect(url_for('cards'))
