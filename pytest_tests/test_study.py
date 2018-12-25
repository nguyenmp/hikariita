'''
Tests that we can load the study page in various conditions
'''

from __future__ import print_function

from bs4 import BeautifulSoup


def test_redirect(empty_client):
    """
    Make sure we redirect from no-trailing-slash to with-trailing-slash
    """

    response = empty_client.get('/cards')
    assert response.status_code == 301
    assert response.headers['Location'].endswith('/cards/')


def test_empty_database(empty_client):
    """
    Make sure the page can load, albeit with no content, when database is empty
    """

    response = empty_client.get('/cards/')
    assert response.status == '302 FOUND'
    assert response.headers['Location'].endswith('/cards/-1/')
    response = empty_client.get(response.headers['Location'])
    soup = BeautifulSoup(response.data, 'html.parser')
    labels = []
    for card in soup.find_all(attrs={'class': 'card'}):
        labels.extend(card.find_all('label'))
    assert not labels


def test_one_book(one_book_twenty_cards_client):
    """
    Make sure the page can load, albeit with no content, when database is empty
    """

    # Because this is a new site, no cards have been prefered
    response = one_book_twenty_cards_client.get('/cards/')
    assert response.status == '302 FOUND'
    assert response.headers['Location'].endswith('/cards/-1/')

    # Select a book to study from
    response = one_book_twenty_cards_client.post(
        '/preferences/edit',
        data={'Book': 'Mandarin'},
        headers={'Referer': response.headers['Location']}
    )

    # Redirect from /preferences/edit -> /cards/
    assert response.status == '302 FOUND'
    assert response.headers['Location'].endswith('/cards/')
    response = one_book_twenty_cards_client.get(response.headers['Location'])

    # Second redirect from /cards/ -> /cards/###/
    assert response.status == '302 FOUND'
    assert '/cards/' in response.headers['Location']
    response = one_book_twenty_cards_client.get(response.headers['Location'])

    # Check to see if there are actually three labels
    soup = BeautifulSoup(response.data, 'html.parser')
    labels = []
    for card in soup.find_all(attrs={'class': 'card'}):
        labels.extend(card.find_all('label'))
    assert len(labels) == 3


def test_two_books(two_books_ten_cards_each_client):
    """
    Make sure the page can load, albeit with no content, when database is empty
    """

    # Because this is a new site, no cards have been prefered
    response = two_books_ten_cards_each_client.get('/cards/')
    assert response.status == '302 FOUND'
    assert response.headers['Location'].endswith('/cards/-1/')

    # Select a book to study from
    response = two_books_ten_cards_each_client.post(
        '/preferences/edit',
        data={'Book': 'Genki 1'},
        headers={'Referer': response.headers['Location']}
    )

    # Redirect from /preferences/edit -> /cards/
    assert response.status == '302 FOUND'
    assert response.headers['Location'].endswith('/cards/')
    response = two_books_ten_cards_each_client.get(response.headers['Location'])

    # Second redirect from /cards/ -> /cards/###/
    assert response.status == '302 FOUND'
    assert '/cards/' in response.headers['Location']
    response = two_books_ten_cards_each_client.get(response.headers['Location'])

    # Check to see if there are actually three labels
    soup = BeautifulSoup(response.data, 'html.parser')
    labels = []
    for card in soup.find_all(attrs={'class': 'card'}):
        labels.extend(card.find_all('label'))
    assert len(labels) == 3
