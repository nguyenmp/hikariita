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
    request,
    abort,
)

from . import db


APP = Flask(__name__)


def get_db():
    '''
    Returns the cached database connection
    '''
    if 'db' not in g:
        g.db = sqlite3.connect('example.db')
        cursor = g.db.cursor()
        db.init(cursor)
        g.db.commit()
        cursor.close()
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
    print "Getting cursor"
    cursor = get_db().cursor()
    card_id = db.get_next_card(cursor)

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
    cursor.close()

    primaries = ['hanzi', 'kanji']
    hidden = ['Book', 'Lesson']
    print "Attributes: " + str(attributes)

    return render_template(
        'card.html',
        primaries=primaries,
        hidden=hidden,
        attributes=attributes,
    )


@APP.route('/cards/<int:card_id>/vote', methods=['POST'])
def vote(card_id):
    '''
    Gives a vote to the given card and redirects to the next card
    '''
    if 'confidence' in request.form:
        confidence = request.form['confidence']
        if confidence == 'good':
            confidence = 1
        elif confidence == 'okay':
            confidence = 0
        elif confidence == 'bad':
            confidence = -1
        else:
            abort(400)

        APP.logger.debug(
            "Received vote request for %s to %s",
            card_id,
            request.form['confidence']
        )

        cursor = get_db().cursor()
        db.create_vote(cursor, card_id, confidence)
        get_db().commit()
    else:
        APP.logger.warning("No confidence in this vote for %s", card_id)

    return redirect(url_for('cards'))
