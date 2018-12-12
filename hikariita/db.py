'''
Imports flashcards into a sqlite database from CSV
'''

from __future__ import unicode_literals


INIT_DB_COMMANDS = '''
CREATE TABLE IF NOT EXISTS cards (id INTEGER PRIMARY KEY);

CREATE TABLE IF NOT EXISTS votes (
    id INTEGER PRIMARY KEY,
    vote INTEGER NOT NULL,
    card_id INTEGER NOT NULL,
    FOREIGN KEY(card_id) REFERENCES cards(id)
);

CREATE TABLE IF NOT EXISTS attributes (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS attributes_cards_relation (
    card_id INTEGER,
    attribute_id INTEGER,
    FOREIGN KEY(card_id) REFERENCES cards(id),
    FOREIGN KEY(attribute_id) REFERENCES attributes(id)
);
'''


def init(cursor):
    '''
    Initializes the database with the base tables
    '''
    cursor.executescript(INIT_DB_COMMANDS)


def create_book(cursor, title):
    '''
    Adds a new book to the DB, and returns it's ID
    '''
    return create_attribute(cursor, "Book", title)


def create_vote(cursor, card_id, vote_value):
    '''
    Registers a vote on a card
    '''
    command = 'INSERT INTO votes (vote, card_id) VALUES (?, ?)'
    cursor.execute(command, (vote_value, card_id))


def create_lesson(cursor, number):
    '''
    Creates a new lesson for the given number
    '''
    return create_attribute(cursor, "Lesson", number)


def create_attribute(cursor, name, value):
    '''
    Creates a generic attribute, not associated with anything yet
    '''
    command = 'INSERT INTO attributes (name, value) VALUES (?, ?)'
    cursor.execute(command, (name, value))
    return cursor.lastrowid


def associate_card_and_attribute(cursor, card_id, attribute_id):
    '''
    Attaches the given attribute to the given card
    '''
    command = 'INSERT INTO attributes_cards_relation (card_id, attribute_id) VALUES (?, ?)'
    cursor.execute(command, (card_id, attribute_id))


def create_card(cursor):
    '''
    Creates a blank card to fill in with attributes later
    '''
    command = 'INSERT INTO cards (id) VALUES (NULL)'
    cursor.execute(command)
    return cursor.lastrowid


def read_data():
    '''
    Imports data from file system
    '''
    with open("~/Downloads/An Integrated Approach to Intermediate Japanese - Lesson 1.tsv", 'r') as handle:
        content = handle.read().decode('utf8')

    result = []

    for line in content.splitlines():
        parts = line.split('\t')
        result.append(parts)

    return result


def get_random_card_id(cursor):
    '''
    Pick a random card and returns that card_id
    '''
    command = 'SELECT id FROM cards ORDER BY RANDOM() LIMIT 1'
    cursor.execute(command)
    row = cursor.fetchone()
    return row[0]


def get_card_attributes(cursor, card_id):
    '''
    Gets all the attributes associated with a card_id
    '''
    command = '''
    SELECT * FROM attributes
    INNER JOIN attributes_cards_relation ON attributes.id == attributes_cards_relation.attribute_id
    WHERE attributes_cards_relation.card_id == ?
    '''
    cursor.execute(command, (card_id,))
    rows = cursor.fetchall()
    return rows


def main():
    ''' main '''
    connection = sqlite3.connect('example.db')
    cursor = connection.cursor()
    init(cursor)
    title = 'An Integrated Approach to Intermediate Japanese'
    book_id = create_book(cursor, title)
    lesson_id = create_lesson(cursor, 1)
    for (kanji, hiragana, meaning) in read_data():
        card_id = create_card(cursor)
        kanji_id = create_attribute(cursor, "kanji", kanji)
        associate_card_and_attribute(cursor, card_id, kanji_id)
        hiragana_id = create_attribute(cursor, "hiragana", hiragana)
        associate_card_and_attribute(cursor, card_id, hiragana_id)
        meaning_id = create_attribute(cursor, "meaning", meaning)
        associate_card_and_attribute(cursor, card_id, meaning_id)
        associate_card_and_attribute(cursor, card_id, book_id)
        associate_card_and_attribute(cursor, card_id, lesson_id)
        connection.commit()


if __name__ == '__main__':
    main()
