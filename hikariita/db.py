'''
Imports flashcards into a sqlite database from CSV
'''

from __future__ import unicode_literals, print_function

import sqlite3
import random


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
    id INTEGER PRIMARY KEY,
    card_id INTEGER,
    FOREIGN KEY(card_id) REFERENCES cards(id)
);

CREATE TABLE IF NOT EXISTS preferences (
    attribute_name TEXT PRIMARY KEY,
    attribute_value TEXT,
    FOREIGN KEY(attribute_name) REFERENCES attributes(name) ON UPDATE CASCADE
    FOREIGN KEY(attribute_value) REFERENCES attributes(value) ON UPDATE CASCADE
);
'''


def read_data(file_path):
    '''
    Imports data from file system
    '''
    with open(file_path, 'r') as handle:
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
    print("Creating vote")
    # Insert vote record
    command = 'INSERT INTO votes (vote, card_id) VALUES (?, ?)'
    cursor.execute(command, (vote_value, card_id))

    # Calculate new state
    bucket = 'easy' if vote_value == 1 else calculate_state_of_card(
        cursor,
        card_id,
    )

    # Update state
    update_command = '''UPDATE cards SET bucket=? WHERE id==? AND bucket!=?'''
    cursor.execute(update_command, (bucket, card_id, bucket))

    print("Did something update? " + str(cursor.rowcount))
    print("What was the vote? " + str(vote_value))

    if vote_value == 1:
        # Evict from working set and resample if state is "easy"
        delete_card_from_working_set(cursor, card_id)
    else:
        # If we aren't confident in this card,
        # move it to the back of the working set queue
        delete_card_from_working_set(cursor, card_id)
        add_card_to_working_set(cursor, card_id)

    init_working_set(cursor)


def get_working_set_size(cursor):
    '''
    Returns the current size of the working set.  The working set is the list
    cards that we actively cycle through until we feel confident about them.
    That list must be maintained as cards "graduate" from them, so that we keep
    a certain minimum active size.
    '''
    working_set_size_query = 'SELECT COUNT(*) FROM working_set'
    cursor.execute(working_set_size_query)
    working_set_size_row = cursor.fetchone()
    working_set_size = working_set_size_row[0]
    print("Working Set Size: " + str(working_set_size))
    return working_set_size


def clear_working_set(cursor):
    '''
    Deletes all cards from the working set so any
    future queries will reinitialize the working set.

    This should be used for major preference or state changes.
    '''
    print("Clearing working set")
    delete_command = '''DELETE FROM working_set'''
    cursor.execute(delete_command)


def delete_card_from_working_set(cursor, card_id):
    '''
    Removes hte given card from the working set
    '''
    print("Evicting " + str(card_id))
    delete_command = '''DELETE FROM working_set WHERE card_id == ?'''
    cursor.execute(delete_command, (card_id,))


def add_card_to_working_set(cursor, card_id):
    '''
    Adds the given card to the working set
    '''
    print("Inserting " + str(card_id))
    update_command = 'INSERT INTO working_set (id, card_id) VALUES (NULL, ?)'
    cursor.execute(update_command, (card_id,))


def draw_from_least_recently_seen(cursor):
    '''
    Pulls a card from a bucket into a working set

    Returns the card_id pulled, or None if there isn't
    any in the bucket not in the working set
    '''
    print("Searching for least-recently-seen card")
    query_command = '''
        SELECT votes.card_id, MAX(votes.id) FROM votes
        LEFT JOIN working_set
        ON votes.card_id == working_set.card_id
        INNER JOIN attributes_cards_relation
        ON attributes_cards_relation.card_id == votes.card_id
        INNER JOIN attributes
        ON attributes.id == attributes_cards_relation.attribute_id
        INNER JOIN preferences
        ON preferences.attribute_name == attributes.name AND preferences.attribute_value = attributes.value
        WHERE working_set.card_id IS NULL
        GROUP BY votes.card_id
        ORDER BY MAX(votes.id) ASC
        LIMIT 1
    '''
    cursor.execute(query_command)
    row = cursor.fetchone()
    if not row:
        print("Found none")
        return None
    card_id = row[0]
    add_card_to_working_set(cursor, card_id)
    return card_id


def get_working_set_size_by_buckets(cursor):
    '''
    Returns a dictionary mapping "bucket" or
    state to a list of cards in that state.

    The list of cards are equal to the working set of cards.
    '''
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

    return buckets


def draw_from_bucket(cursor, bucket):
    '''
    Pulls a card from a bucket into a working set

    Returns the card_id pulled, or None if there isn't
    any in the bucket not in the working set
    '''
    print("Drawing from " + bucket)
    query_command = '''
        SELECT cards.id FROM cards
        LEFT JOIN working_set
        ON cards.id == working_set.card_id
        INNER JOIN attributes_cards_relation
        ON attributes_cards_relation.card_id == cards.id
        INNER JOIN attributes
        ON attributes.id == attributes_cards_relation.attribute_id
        INNER JOIN preferences
        ON preferences.attribute_name == attributes.name AND preferences.attribute_value = attributes.value
        WHERE working_set.card_id IS NULL AND bucket == ?
        ORDER BY RANDOM()
        LIMIT 1
    '''
    cursor.execute(query_command, (bucket,))
    row = cursor.fetchone()
    if not row:
        print("Found none")
        return None
    card_id = row[0]
    add_card_to_working_set(cursor, card_id)
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
        LIMIT 3
    '''
    cursor.execute(command, (card_id,))
    row = cursor.fetchone()

    # We don't have enough votes to determine state yet
    if row[1] < 3:
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


def edit_attribute(cursor, attribute_id, attribute_value):
    '''
    Updates the given card's attribute to be the given value
    '''
    command = 'UPDATE attributes SET value=? WHERE id==?'
    cursor.execute(command, (attribute_value, attribute_id,))
    print("Affected " + str(cursor.rowcount) + " rows")


def get_attributes(cursor):
    '''
    Returns a dictionary of all the attribute names
    mapped to all their respective values

    Originally written so that I could create a "filtering" UI
    '''
    query = '''
        SELECT name, value FROM attributes
        ORDER BY attributes.name
    '''
    cursor.execute(query)
    rows = cursor.fetchall()
    result = {}
    for (name, value) in rows:
        values = result.get(name, [])
        values.append(value)
        result[name] = values
    return result


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
    print("Getting next card")
    command = '''
        SELECT working_set.card_id
        FROM working_set
        LEFT JOIN votes
        ON working_set.card_id == votes.card_id
        GROUP BY working_set.card_id
        ORDER BY MAX(working_set.id) ASC
        LIMIT 1
    '''
    cursor.execute(command)
    row = cursor.fetchone()
    if not row:
        print("No cards in working set")
        return None
    card_id = row[0]
    print("Got " + str(card_id))
    return card_id


def get_books(cursor):
    '''
    Returns the list of books available and the active book we're filtering on
    '''
    print("Getting all books")
    command = '''
        SELECT attributes.value FROM attributes
        WHERE attributes.name == "Book"
    '''
    cursor.execute(command)
    rows = cursor.fetchall()
    book_names = [row[0] for row in rows]
    print("Got " + str(len(book_names)) + " books")
    return book_names


def clear_preferences(cursor):
    '''
    Erases all the preference stuff
    '''
    print("Clearing user's preferences")
    command = '''
        DELETE FROM preferences
    '''
    cursor.execute(command)


def set_preference(cursor, preference):
    '''
    Adds/sets the given preference for the user
    '''
    print("Updating user's preference for " + str(preference))
    (attribute_name, attribute_value) = preference
    command = '''
        INSERT OR REPLACE INTO preferences (attribute_name, attribute_value)
        VALUES(?, ?)
    '''
    cursor.execute(command, (attribute_name, attribute_value,))
    print("Setted " + attribute_name + ' to ' + attribute_value)


def set_preferences(cursor, preferences):
    '''
    Sets the user's preferences to the provided
    '''
    print("Updating user's preferences")
    clear_preferences(cursor)
    for preference in preferences:
        set_preference(cursor, preference)


def set_prefered_book(cursor, book_name):
    '''
    Sets the user's prefered book
    '''
    print("Setting prefered book to " + str(book_name))
    set_preference(cursor, ('Book', book_name,))


def get_card_stats(cursor):
    '''
    Returns statistics about card stats
    '''
    print("Getting statistics")
    command = '''
        SELECT COUNT(*), attributes.value, cards.bucket FROM cards
        LEFT JOIN attributes_cards_relation
        ON cards.id == attributes_cards_relation.card_id
        INNER JOIN attributes
        ON attributes_cards_relation.attribute_id == attributes.id
        WHERE attributes.name == "Book"
        GROUP BY attributes.value, cards.bucket
    '''
    cursor.execute(command)
    rows = cursor.fetchall()
    by_book = {}
    for (count, book, bucket) in rows:
        buckets = by_book.get(book, {})
        buckets[bucket] = count
        by_book[book] = buckets
    return by_book


def get_preferences(cursor):
    '''
    Returns the list of attributes and values the user wants to filter by
    '''
    print("Getting preferences")
    command = '''
        SELECT id as id, name as name, value as value FROM preferences
        INNER JOIN attributes
        ON attributes.name == preferences.attribute_name
        AND preferences.attribute_value == attributes.value
        '''
    cursor.execute(command)
    rows = cursor.fetchall()
    return rows


def get_book(cursor):
    '''
    Gets the user's prefered book, or None if not selected
    '''
    preferences = get_preferences(cursor)
    for preference in preferences:
        print(preference)
        print(type(preference))
        if preference[str('name')] == 'Book':
            return preference[str('value')]
    return None


def init_working_set(cursor):
    '''
    Creates a working set for the user with at least 7 cards

    These cards are drawin from the "genesis" deck,
    or else it's the oldest card we haven't seen.
    '''
    # Assert working set is not initialized
    print("Initing working set")

    for _ in range(get_working_set_size(cursor), 7):
        if draw_from_bucket(cursor, "genesis") is not None:
            print("Found a card from genesis to add to working set")
            continue

        if random.random() < 0.3:
            print("Randomly draw from the easy pool to mix things up")
            if draw_from_bucket(cursor, "easy") is not None:
                print("Found a card from genesis to add to working set")
                continue

        # However, usually, we should draw from the tail to prevent stale cards
        if draw_from_least_recently_seen(cursor) is not None:
            print("Found a card we haven't seen in a while for working set")
            continue

        print("Could not find another card to add to the working set. \
        This could there's not enough cards in the deck to form a full \
        working set, or a bug.")


def create_content(cursor, book_title, lesson_name, headers, cards):
    '''
    Populates/inserts the given content into the database

    We will not reuse any content (merging).
    '''
    book_id = create_book(cursor, book_title)
    lesson_id = create_lesson(cursor, lesson_name)
    for row in cards:
        assert len(headers) == len(row)

        card_id = create_card(cursor)
        print("Created card: " + str(card_id))
        for i in range(0, len(headers)):
            name = headers[i].lower()
            value = row[i]
            attribute_id = create_attribute(cursor, name, value)
            print("Created attribute: " + str(attribute_id) + " for " + name + " = " + value)
            associate_card_and_attribute(cursor, card_id, attribute_id)
        associate_card_and_attribute(cursor, card_id, book_id)
        associate_card_and_attribute(cursor, card_id, lesson_id)


def main():
    ''' Imports data from a file '''
    connection = sqlite3.connect('example.db')
    cursor = connection.cursor()
    init(cursor)
    title = 'Genki 1'
    lesson = 1
    file_path = "/Users/livingon/Downloads/Genki I & II - Lesson 1.tsv"
    data = read_data(file_path)
    headers = data[0]
    cards = data[1:]
    create_content(cursor, title, lesson, headers, cards)
    connection.commit()

if __name__ == '__main__':
    main()
