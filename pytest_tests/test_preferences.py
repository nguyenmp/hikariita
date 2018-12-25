'''
Tests that we can load the index page
'''

from __future__ import print_function


def test_index_empty(empty_client):
    """Start with a blank database."""

    response = empty_client.get('/preferences/')
    assert response.status_code == 200


def test_index_with_content(one_book_twenty_cards_client):
    """Checks to see the page loads given some content."""

    response = one_book_twenty_cards_client.get('/preferences/')
    assert response.status_code == 200


def test_index_with_more_content(two_books_ten_cards_each_client):
    """Checks to see the page loads given some content."""

    response = two_books_ten_cards_each_client.get('/preferences/')
    assert response.status_code == 200


def test_redirects(empty_client):
    """Checks redirects."""

    response = empty_client.get('/preferences')
    assert response.status_code == 301
