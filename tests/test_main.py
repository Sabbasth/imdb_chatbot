import json

from imdb_chatbot import main

IMDB_API_VERSION = "3"
IMDB_API_ROOT = 'https://api.themoviedb.org'
IMDB_API_ENDPOINT_TV_DETAILS = 'tv/{}'
IMDB_API_ENDPOINT_SEARCH_TV = 'search/tv'

TEXT = {
    "en": {
        "next_show": "Next {tv_show} episode will be on air on {date}",
        "no_next_show": "There's no show coming for {tv_show}",
        "no_show": "I found no TV show with this name",
    },
    "fr": {
        "next_show": "Le prochain épisode de {tv_show} sera diffusé le {date}",
        "no_next_show": "Il n'y a pas d'épisode à venir pour {tv_show}",
        "no_show": "Je n'ai trouvé aucune série de ce nom",
    },
}


def test_search_tv_1(requests_mock):
    '''Tests happy path
    '''
    url = 'https://api.themoviedb.org/3/search/tv'
    response_payload = '{"results":[{"name": "FAKE_SHOW"}],"total_results": 1}'
    requests_mock.get(url, text=response_payload)

    assert main.search_tv(api_key="", query="FAKE_SHOW") == (True, {"name": "FAKE_SHOW"})


def test_search_tv_2(requests_mock):
    '''Tests no show match
    '''
    url = 'https://api.themoviedb.org/3/search/tv'
    response_payload = '{"results": [],"total_results": 0}'
    requests_mock.get(url, text=response_payload)

    assert main.search_tv(api_key="", query="FAKE_SHOW") == (False, None)


def test_show_details_1(requests_mock):
    '''Test happy path
    '''
    url = 'https://api.themoviedb.org/3/tv/0'
    response_payload = '{"payload":"payload"}'
    requests_mock.get(url, text=response_payload)

    assert main.show_details(api_key="", show_id=0) == json.loads(response_payload)


def test_show_next_1(requests_mock):
    '''Test happy path
    '''
    lang = 'en'

    url_search = 'https://api.themoviedb.org/3/search/tv'
    search_response_payload = '{"results":[{"name": "FAKE_SHOW", "id": "0"}],"total_results": 1}'
    requests_mock.get(url_search, text=search_response_payload)

    url_details = 'https://api.themoviedb.org/3/tv/0'
    details_response_payload = '{"next_episode_to_air":{"air_date":"2019-05-16"}}'
    # details_response_payload = '{"next_episode_to_air":null}'
    requests_mock.get(url_details, text=details_response_payload)

    text = TEXT[lang]["next_show"].format(date='2019-05-16', tv_show='FAKE_SHOW')
    assert main.show_next(
        lang=lang,
        show_text="FAKE_SHOW"
    ) == '{"fulfillmentText": "' + text + '"}'

def test_show_next_2(requests_mock):
    '''Test if no next show
    '''
    lang = 'en'

    url_search = 'https://api.themoviedb.org/3/search/tv'
    search_response_payload = '{"results":[{"name": "FAKE_SHOW", "id": "0"}],"total_results": 1}'
    requests_mock.get(url_search, text=search_response_payload)

    url_details = 'https://api.themoviedb.org/3/tv/0'
    details_response_payload = '{"next_episode_to_air":null}'
    requests_mock.get(url_details, text=details_response_payload)

    text = TEXT[lang]["no_next_show"].format(tv_show='FAKE_SHOW')
    assert main.show_next(
        lang=lang,
        show_text="FAKE_SHOW"
    ) == '{"fulfillmentText": "' + text + '"}'
