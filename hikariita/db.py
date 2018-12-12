'''
Imports flashcards into a sqlite database from CSV
'''

from __future__ import unicode_literals

import sqlite3


INIT_DB_COMMANDS = '''
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY,
    bucket TEXT DEFAULT "genesis"
);

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

CREATE TABLE IF NOT EXISTS working_set (
    card_id INTEGER,
    FOREIGN KEY(card_id) REFERENCES cards(id)
);
'''


def read_data():
    '''
    Imports data from file system
    '''
    with open("/Users/livingon/Downloads/An Integrated Approach to Intermediate Japanese - Lesson 1.tsv", 'r') as handle:
        content = handle.read().decode('utf8')

    result = []

    for line in content.splitlines():
        parts = line.split('\t')
        result.append(parts)

    return result


def init(cursor):
    '''
    Initializes the database with the base tables
    '''
    cursor.executescript(INIT_DB_COMMANDS)
    init_working_set(cursor)


def create_book(cursor, title):
    '''
    Adds a new book to the DB, and returns it's ID
    '''
    return create_attribute(cursor, "Book", title)


def create_vote(cursor, card_id, vote_value):
    '''
    Registers a vote on a card
    '''
    # Insert vote record
    command = 'INSERT INTO votes (vote, card_id) VALUES (?, ?)'
    cursor.execute(command, (vote_value, card_id))

    # Calculate new state
    bucket = calculate_state_of_card(cursor, card_id)

    # Update state
    update_command = '''UPDATE cards SET bucket=? WHERE id==? AND bucket!=?'''
    cursor.execute(update_command, (bucket, card_id, bucket))

    # Evict from working set and resample if state has changed
    if cursor.rowcount != 0:
        delete_command = '''DELETE FROM working_set WHERE card_id == ?'''
        cursor.execute(delete_command, (card_id,))

        working_set_distribution_query = '''
            SELECT COUNT(*), bucket
            FROM working_set
            INNER JOIN cards
            ON working_set.card_id == cards.id
            GROUP BY bucket
        '''
        cursor.execute(working_set_distribution_query)
        distribution_rows = cursor.fetchall()
        buckets = {}
        for row in distribution_rows:
            buckets[row[1]] = row[0]

        for _ in range(buckets.get('hard', 0) + buckets.get('genesis', 0), 3):
            if not draw_from_bucket(cursor, 'hard'):
                draw_from_bucket(cursor, 'genesis')

        for _ in range(buckets.get('okay', 0), 2):
            draw_from_bucket(cursor, 'okay')

        for _ in range(buckets.get('easy', 0), 2):
            draw_from_bucket(cursor, 'easy')


def draw_from_bucket(cursor, bucket):
    '''
    Pulls a card from a bucket into a working set

    Returns the card_id pulled, or None if there isn't
    any in the bucket not in the working set
    '''
    query_command = '''
        SELECT id FROM cards
        LEFT JOIN working_set
        ON cards.id == working_set.card_id
        WHERE working_set.card_id IS NULL AND bucket == ?
        ORDER BY RANDOM()
        LIMIT 1
    '''
    cursor.execute(query_command, (bucket,))
    row = cursor.fetchone()
    if not row:
        return None
    card_id = row[0]

    print "Inserting " + str(card_id)
    update_command = 'INSERT INTO working_set (card_id) VALUES (?)'
    cursor.execute(update_command, (card_id,))
    return card_id


def calculate_state_of_card(cursor, card_id):
    '''
    Queries for the last 5 votes and calculates the state of that card:

    * easy
    * medium
    * hard
    '''
    command = '''
        SELECT AVG(vote), COUNT(vote)
        FROM votes
        WHERE card_id=?
        ORDER BY ROWID DESC
        LIMIT 5
    '''
    cursor.execute(command, (card_id,))
    row = cursor.fetchone()

    # We don't have enough votes to determine state yet
    if row[1] < 5:
        return None

    assert row[0] >= -1
    assert row[0] <= 1

    if row[0] < 0:
        return 'hard'
    elif row[0] < 1:
        return 'okay'
    elif row[0] == 1:
        return 'easy'

    assert False


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
    command = '''
        INSERT INTO attributes_cards_relation (card_id, attribute_id)
        VALUES (?, ?)
    '''
    cursor.execute(command, (card_id, attribute_id))


def create_card(cursor):
    '''
    Creates a blank card to fill in with attributes later
    '''
    command = 'INSERT INTO cards (id, bucket) VALUES (NULL, "genesis")'
    cursor.execute(command)
    return cursor.lastrowid


def get_card_attributes(cursor, card_id):
    '''
    Gets all the attributes associated with a card_id
    '''
    command = '''
    SELECT * FROM attributes
    INNER JOIN attributes_cards_relation
    ON attributes.id == attributes_cards_relation.attribute_id
    WHERE attributes_cards_relation.card_id == ?
    '''
    cursor.execute(command, (card_id,))
    rows = cursor.fetchall()
    return rows


def get_next_card(cursor):
    '''
    Out of the working set, pick the card that we have not seen for the longest
    '''
    print "getting next card"
    command = '''
        SELECT working_set.card_id
        FROM working_set
        LEFT JOIN votes
        ON working_set.card_id == votes.card_id
        GROUP BY working_set.card_id
        ORDER BY MAX(votes.ROWID) ASC
        LIMIT 1
    '''
    cursor.execute(command)
    row = cursor.fetchone()
    return row[0]


def init_working_set(cursor):
    '''
    Creates a working set for the user from 3 random cards from genesis
    '''
    # Assert working set is not initialized
    print "Initing working set"
    working_set_count_query = '''SELECT count(ROWID) FROM working_set'''
    cursor.execute(working_set_count_query)
    working_set_count = cursor.fetchone()[0]
    if working_set_count != 0:
        print "We don't need to init working set, it already has content"
        return

    # Pick 5 random from genesis (cards without votes)
    # aka cards that haven't been seen yet
    for _ in range(0, 3):
        draw_from_bucket(cursor, 'genesis')


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
