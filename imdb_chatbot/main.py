import json
import os

import requests


IMDB_API_KEY = os.environ["IMDB_API_KEY"]
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


def search_tv(api_key, query, lang='fr'):
    '''Returns the first show of the list

    Args:
        api_key (str): API Key for authn
        query (str): the query to search on
        lang (str): ISO639-1 language format defines the response language

    Returns:
        tuple: First member is success, second is response

    '''
    request_uri = os.path.join(
        IMDB_API_ROOT,
        IMDB_API_VERSION,
        IMDB_API_ENDPOINT_SEARCH_TV
    )
    request_params = {
        "api_key": api_key,
        "language": lang,
        "query": query
    }
    r = requests.get(request_uri, params=request_params)

    # By contract IMDB API must always return a results entry
    if r.json().get("total_results") == 0:
        return False, None

    return True, r.json()["results"][0]


def show_details(api_key, show_id, lang='fr'):
    '''Returns the details of a given TV Show

    Warning: We assume that the show_id is correct because it's sent by IMDB
             in the previous call

    Args:
        api_key (str): IMDB API KEY
        show_id (str): ID of the show as given by IMDB
        lang (str): ISO639-1 language format defines the response language

    Returns:
        dict: structured informations of the show
    '''
    request_uri = os.path.join(
        IMDB_API_ROOT,
        IMDB_API_VERSION,
        IMDB_API_ENDPOINT_TV_DETAILS
    ).format(show_id)
    request_params = {"api_key": api_key, "language": lang}

    r = requests.get(request_uri, params=request_params)
    return r.json()


def show_next(lang, show_text):
    '''Find the date of the next episode and returns a text response

    Args:
        lang (str): ISO639-1 language format
        show_text (str): text to query

    Returns:
        str: returns text from the bot
    '''
    success, show = search_tv(api_key=IMDB_API_KEY, lang=lang, query=show_text)

    if not success:
        fullfillment_text = TEXT[lang]["no_show"]

    details = show_details(api_key=IMDB_API_KEY, show_id=show["id"], lang=lang)
    if details["next_episode_to_air"] is None:
        fullfillment_text = TEXT[lang]["no_next_show"].format(tv_show=show_text)

    else:
        fullfillment_text = TEXT[lang]["next_show"].format(
            date=details["next_episode_to_air"]["air_date"],
            tv_show=show_text
        )

    return json.dumps({"fulfillmentText": fullfillment_text})


def chatbot(request):
    '''This is the routing function. It takes a Flask request as parameter and sends back the response

    Args:
        request (flask.request): the request object

    Returns:
        str or tuple: the message sent back to the requester optionnally
                      with a return code
    '''
    if request.path == '/imdb':
        # We test if the data payload is correct for this endpoint
        if (
            not request.json.get("queryResult") and (
                not request.json["queryResult"].get("languageCode") or
                not request.json["queryResult"].get("tv_show")
            )
        ):
            return 'Incomplete data', 400

        lang = request.json["queryResult"]["languageCode"]
        tv_show = request.json["queryResult"]["parameters"]["tv_show"]
        return show_next(lang=lang, show_text=tv_show)

    # Default behavior
    return 'URL not found'
