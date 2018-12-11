# -*- coding: utf-8 -*-

'''
This module is an application for flashcarding Japanese.
'''

from __future__ import unicode_literals

from flask import (
    Flask,
    render_template,
)


APP = Flask(__name__)


@APP.route('/')
def card():
    '''
    Renders a single flash-card on screen
    '''
    return render_template(
        'card.html',
        kanji="紹介",
        hiragana="しょうかい",
        meaning='introduction',
    )
