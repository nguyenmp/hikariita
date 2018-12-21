'''
Tests that we can load the index page
'''

from __future__ import print_function


def test_index_empty(empty_client):
    """Start with a blank database."""

    response = empty_client.get('/')
    assert response.status_code == 200
    assert 'Welcome!' in response.data


def test_index_with_content(one_book_twenty_cards_client):
    """Start with a blank database."""

    response = one_book_twenty_cards_client.get('/')
    assert response.status_code == 200
    assert 'Welcome!' in response.data
