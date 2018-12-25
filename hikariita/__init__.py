# -*- coding: utf-8 -*-

'''
This module is an application for flashcarding Japanese.
'''

from __future__ import unicode_literals, print_function

import os
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
        print(str(os.environ))
        db_path = os.environ.get('DATABASE', APP.config.get('DATABASE', 'example.db'))
        print("DB STAT: " + str(os.stat(db_path)))
        print("Dtabase: " + str(db_path))
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
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
    return render_template(
        'index.html',
    )


@APP.route('/cards/', methods=['GET'])
def cards():
    '''
    The index of cards, redirects to an instance of a random card
    '''
    print("Getting cursor")
    cursor = get_db().cursor()
    card_id = db.get_next_card(cursor)

    APP.logger.debug('Type 1: %s', type(card_id))
    return redirect(url_for('card', card_id=card_id or -1))


@APP.route('/cards/<string:card_id>/', methods=['GET'])
def card(card_id):
    '''
    Renders a single flash-card on screen
    '''
    APP.logger.debug('Type: %s', type(card_id))

    cursor = get_db().cursor()
    attributes = db.get_card_attributes(cursor, card_id)
    books = db.get_books(cursor)
    active_book = db.get_book(cursor)
    cursor.close()

    primaries = ['hanzi', 'kanji']
    hidden = ['Book', 'Lesson']
    print("Attributes: " + str(attributes))

    return render_template(
        'card.html',
        active_book=active_book,
        books=books,
        primaries=primaries,
        hidden=hidden,
        attributes=attributes,
    )


@APP.route('/cards/<string:card_id>/edit/', methods=['POST'])
def edit_card(card_id):
    '''
    Renders a single flash-card on screen
    '''
    cursor = get_db().cursor()
    for (attribute_id, attribute_value) in request.form.items():
        APP.logger.info(
            "Editing %s setting %s to %s",
            card_id,
            attribute_id,
            attribute_value,
        )
        db.edit_attribute(cursor, attribute_id, attribute_value)
    cursor.close()
    get_db().commit()
    return redirect(url_for('card', card_id=card_id))


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


@APP.route('/preferences/edit', methods=['POST'])
def preferences_edit():
    '''
    Saves some given user preferences
    '''
    cursor = get_db().cursor()
    db.set_preferences(cursor, request.form.items())
    db.clear_working_set(cursor)
    get_db().commit()
    if 'preferences' in request.referrer:
        return redirect(url_for('preferences'))
    return redirect(url_for('cards'))


@APP.route('/preferences/', methods=['GET'])
def preferences():
    '''
    Saves some given user preferences
    '''
    cursor = get_db().cursor()
    prefs = db.get_preferences(cursor)
    attributes = db.get_attributes(cursor)
    return render_template(
        'preferences.html',
        preferences=prefs,
        attributes=attributes,
    )


@APP.route('/stats/', methods=['GET'])
def stats():
    '''
    Shows some summary information about my cards
    '''
    cursor = get_db().cursor()
    books = db.get_card_stats(cursor)
    return render_template(
        'stats.html',
        books=books,
    )
