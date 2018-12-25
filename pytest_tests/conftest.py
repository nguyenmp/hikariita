# -*- coding: utf-8 -*-

'''
The test code is located in the tests directory. This directory is next to the
hikariita package, not inside it. The `tests/conftest.py` file contains setup
functions called fixtures that each test will use. Tests are in Python modules
that start with `test_`, and each test function in those modules also starts
with `test_`.


http://flask.pocoo.org/docs/1.0/tutorial/tests/
'''

from __future__ import unicode_literals, print_function

import tempfile

import pytest

from hikariita import APP, get_db
from hikariita.db import create_content

JAPANESE_BOOKS = {
    'headers': ('kanji', 'hiragana', 'meaning'),
    'Genki 1': {
        'Lesson 1': [
            ('', 'あの。 。 。', 'umm...'),
            ('今', 'いま', 'now'),
            ('英語', 'えい', 'English (language)'),
            ('', 'はい', 'yes'),
            ('学生', 'がくせい', 'student'),
            ('〜語', '〜 ご', '... language'),
            ('高校', 'こうこう', 'high school'),
            ('午後', 'ごご', 'PM'),
            ('午前', 'ごぜ', 'AM'),
            ('〜歳', '〜 さい', '~ years old'),
        ],
        'Lesson 2': [
            ('これ', 'これ', 'this one'),
            ('それ', 'それ', 'That one'),
            ('あれ', 'あれ', 'that one over there'),
            ('どれ', 'どれ', 'which one'),
            ('この', 'この', 'this... (thing)'),
            ('その', 'その', 'That.... (thing)'),
            ('あの', 'あの', 'that (thing) over there'),
            ('どの', 'どの', 'Which (thing)'),
            ('ここ', 'ここ', 'here'),
            ('そこ', 'そこ', 'There'),
        ],
    },
    'Genki 2': {
        'Lesson 13': [
            ('ウェイター', 'ウェイター', 'Waiter'),
            ('お宅', 'おたく', "(someone's) house/home"),
            ('大人', 'おとな', 'adult'),
            ('外国語', 'がいこく', 'ご  Foreign language'),
            ('楽器', 'がっき', 'musical instrument'),
            ('空手', 'からて', 'karate'),
            ('カレー', 'カレー', 'curry'),
            ('着物', 'きもの', 'kimono; Japanese traditional dress'),
            ('広告', 'こうこく', 'advertisment'),
            ('紅茶', 'こうちゃ', 'tea (black tea)'),
        ],
        'Lesson 14': [
            ('兄', 'あに', '(my) older brother'),
            ('大家さん', 'おおやさん', 'Landlord; landlady'),
            ('お返し', 'おかえし', 'return (as a token of gratitude)'),
            ('奥さん', 'おくさん', '(your/his) wife'),
            ('おじさん', 'おじさん', 'uncle; middle-aged man'),
            ('おばさん', 'おばさん', 'aunt; middle-aged woman'),
            ('グラス', 'グラス', 'tumbler; glass'),
            ('クリスマス', 'クリスマス', 'Christmas'),
            ('ご主人', 'ごしゅじん', '(your/her) husband'),
            ('皿', 'さら', 'plate; dish'),
        ],
    },
}

MANDARIN_BOOKS = {
    'headers': ('hanzi', 'pinyin', 'english'),
    'Mandarin': {
        'Lesson  - Class 1': [
            ('户外', 'hù wài', 'outdoor'),
            ('运动', 'yùn dòng', 'exercise'),
            ('冲浪', 'chōng làng', 'to surf'),
            ('滑雪', 'huá xuě', 'to ski'),
            ('露营', 'lù yíng', 'to camp'),
            ('远足', 'yuǎn zú', 'to hike'),
            ('室内', 'shì nèi', 'indoor'),
            ('打猎', 'dǎ liè', 'to hunt'),
            ('爬山', 'pá shān', 'to climb a mountain'),
            ('钓鱼', 'diào yú', 'to fish'),
        ],
        'Lesson  - Class 2': [
            ('海报', 'hǎi bào', 'poster'),
            ('麦片', 'mài piàn', 'oatmeal'),
            ('自己', 'zì jǐ', 'by oneself'),
            ('邻居', 'lín jū', 'neighbor'),
            (
                '他昨天在开车呢。',
                'tā zuó tiān zài kāi chē ní 。',
                'He was driving yesterday.'),
            (
                '他昨天晚上八点左右在和朋友吃饭。',
                'tā zuó tiān wǎn shàng bā din zuǒ yòu zài hé péng yǒu chī fàn',
                'He was eating with friends at around 8pm last night.',
            ),
            ('上周五', 'shàng zhōu wǔ', 'last Friday'),
            ('前天晚上', 'qián tiān wǎn shàng', 'The night before last'),
            ('两小时前', 'liǎng xiǎo shí qián', 'Two hours ago'),
            (
                '他明天会在学习',
                'tā míng tiān huì zài xué xí',
                'He will be studying tomorrow',
            ),
        ],
    },
}


def _init(books):
    '''
    Takes in a dictionary of book names to a dictionary of lessons to cards.
    The cards are defined by a tuple of attributes.  These attributes are
    named by the tuple of strings at the top level of the book dictionary
    keyed as 'headers'

    Must be called from a flask application context
    '''
    database = get_db()
    cursor = database.cursor()
    headers = books['headers']
    for (book_name, lessons) in books.items():
        if book_name == 'headers':
            continue

        for (lesson_name, cards) in lessons.items():
            create_content(cursor, book_name, lesson_name, headers, cards)

    database.commit()
    cursor.close()
    print("Committed")


def _client(init_func):
    '''
    Returns a testing client to make requests to the hikariita flask app
    '''

    # Create a temporary database
    print("initing client")
    db_file = tempfile.NamedTemporaryFile(delete=False)
    db_path = db_file.name

    APP.config['DATABASE'] = db_path

    # Configure for testing
    APP.config['TESTING'] = True

    # Init DB with base data
    with APP.app_context():
        if init_func is not None:
            init_func()

    return APP.test_client()


@pytest.fixture
def empty_client():
    '''
    Returns a testing client configured with no data
    '''

    return _client(None)


@pytest.fixture
def one_book_twenty_cards_client():
    '''
    Creates an app client where the database contains
    one book and one lesson with twenty cards
    '''

    return _client(lambda: _init(MANDARIN_BOOKS))


@pytest.fixture
def two_books_ten_cards_each_client():
    '''
    Creates an app client where the database
    contains two books, each with 10 cards
    '''
    return _client(lambda: _init(JAPANESE_BOOKS))
