import logging
import os
from datetime import datetime

import psycopg2
from serpapi import GoogleSearch

from logger import logger

google_params = {
    "api_key": os.getenv("SERPAPI_KEY"),
    "engine": "google_trends_trending_now",
    "frequency": "daily",
    "geo": os.getenv("LOCATION"),
    "hl": "en",
}

# Replace with your PostgreSQL connection parameters
DB_CONNECTION_PARAMS = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}


def fetch_trending_google_search(
    api_key=None,
    engine="google_trends_trending_now",
    frequency="daily",
    geo=None,
    hl="en",
):
    """
    Fetches trending Google searches using the SERP API.

    Args:
        - api_key (str): API key for the SERP API.
        - engine (str): Search engine to use (default is "google_trends_trending_now").
        - frequency (str): Frequency of trending searches (default is "daily").
        - geo (str): Geographical location for searches.
        - hl (str): Language setting (default is "en").

    Returns:
        - dict: Results of the Google search.
    """
    params = {
        "api_key": api_key or os.getenv("SERPAPI_KEY"),
        "engine": engine,
        "frequency": frequency,
        "geo": geo or os.getenv("LOCATION"),
        "hl": hl,
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        logger.info("Google search successful.")
        return results
    except Exception as e:
        logger.error(f"Error in Google search: {str(e)}")
        raise e


def create_connection(DB_CONNECTION_PARAMS):
    """
    Creates a connection to the PostgreSQL database.

    Args:
        - DB_CONNECTION_PARAMS (dict): Database Credentials.

    Returns:
        psycopg2.extensions.connection: A connection to the database if successful, None otherwise.
    """
    try:
        connection = psycopg2.connect(**DB_CONNECTION_PARAMS)
        logger.info("Database connection established.")
        return connection
    except Exception as e:
        logger.error(f"Error: Unable to connect to the database - {e}")
        return None


def insert_daily_search(cursor, date):
    """
    Inserts a record for daily searches into the database.

    Args:
        - cursor (psycopg2.extensions.cursor): The database cursor.
        - date (datetime.date): The date for the daily search record.

    Returns:
        - int: The ID of the inserted record if successful, None otherwise.
    """
    try:
        query = "INSERT INTO daily_searches (date) VALUES (%s) RETURNING id"
        cursor.execute(query, (date,))
        inserted_id = cursor.fetchone()[0]
        logger.info(f"Daily search record inserted with ID: {inserted_id}")
        return inserted_id
    except Exception as e:
        logger.error(f"Error: Unable to insert daily_search record - {e}")
        return None


def insert_search(cursor, daily_search_id, search):
    """
    Inserts a record for a search into the database.

    Args:
        - cursor (psycopg2.extensions.cursor): The database cursor.
        - daily_search_id (int): The ID of the associated daily search record.
        - search (dict): A dictionary containing search information with keys:
            - 'query' (str): The search query.
            - 'google_trends_link' (str): The Google Trends link for the search.
            - 'traffic' (int): The traffic associated with the search.

    Returns:
        - int: The ID of the inserted record if successful, None otherwise.
    """
    try:
        query = "INSERT INTO searches (daily_search_id, query, google_trends_link, traffic) VALUES (%s, %s, %s, %s) RETURNING id"
        cursor.execute(
            query,
            (
                daily_search_id,
                search.get("query", "NA"),
                search.get("google_trends_link", "NA"),
                search.get("traffic", 0),
            ),
        )
        inserted_id = cursor.fetchone()[0]
        logger.info(f"Search record inserted with ID: {inserted_id}")
        return inserted_id
    except Exception as e:
        logger.error(f"Error: Unable to insert search record - {e}")
        return None


def insert_related_query(cursor, search_id, related_query):
    """
    Inserts a record for a related query into the database.

    Args:
        - cursor (psycopg2.extensions.cursor): The database cursor.
        - search_id (int): The ID of the associated search record.
        - related_query (dict): A dictionary containing related query information with keys:
            - 'query' (str): The related query.
            - 'google_trends_link' (str): The Google Trends link for the related query.

    Returns:
        None
    """
    try:
        query = "INSERT INTO related_queries (search_id, query, google_trends_link) VALUES (%s, %s, %s)"
        cursor.execute(
            query,
            (
                search_id,
                related_query.get("query", "NA"),
                related_query.get("google_trends_link", "NA"),
            ),
        )
        logger.info("Related query record inserted successfully.")
    except Exception as e:
        logger.error(f"Error: Unable to insert related_query record - {e}")


def insert_article(cursor, search_id, article):
    """
    Inserts a record for an article into the database.

    Args:
        - cursor (psycopg2.extensions.cursor): The database cursor.
        - search_id (int): The ID of the associated search record.
        - article (dict): A dictionary containing article information with keys:
            - 'title' (str): The title of the article.
            - 'link' (str): The link to the article.
            - 'snippet' (str): A snippet or summary of the article.
            - 'source' (str): The source or publication of the article.
            - 'date' (str): The publication date of the article.
            - 'thumbnail' (str): The link to the article's thumbnail or image.

    Returns:
        None
    """
    try:
        query = "INSERT INTO articles (search_id, title, link, snippet, source, time_ago, thumbnail) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(
            query,
            (
                search_id,
                article.get("title", "NA"),
                article.get("link", "NA"),
                article.get("snippet", "NA"),
                article.get("source", "NA"),
                article.get("date", "NA"),
                article.get("thumbnail", "NA"),
            ),
        )
        logger.info("Article record inserted successfully.")
    except Exception as e:
        logger.error(f"Error: Unable to insert article record - {e}")


def parse_and_insert(json_data):
    """
    Parses and inserts data from a JSON format into the PostgreSQL database.

    Args:
        - json_data (dict): A dictionary containing the parsed JSON data with the following structure:
            {
                'daily_searches': [
                    {
                        'date': 'YYYYMMDD',
                        'searches': [
                            {
                                'query': 'search_query',
                                'google_trends_link': 'trends_link',
                                'related_queries': [
                                    {
                                        'query': 'related_query',
                                        'google_trends_link': 'related_trends_link',
                                    },
                                    ...
                                ],
                                'articles': [
                                    {
                                        'title': 'article_title',
                                        'link': 'article_link',
                                        'snippet': 'article_snippet',
                                        'source': 'article_source',
                                        'date': 'article_date',
                                        'thumbnail': 'article_thumbnail',
                                    },
                                    ...
                                ],
                            },
                            ...
                        ],
                    },
                    ...
                ]
            }

    Returns:
        None
    """
    connection = create_connection(DB_CONNECTION_PARAMS)

    if connection:
        try:
            with connection:
                with connection.cursor() as cursor:
                    for daily_search in json_data.get("daily_searches", []):
                        date = datetime.strptime(
                            daily_search.get("date", "NA"), "%Y%m%d"
                        ).date()
                        daily_search_id = insert_daily_search(cursor, date)

                        if daily_search_id is not None:
                            for search in daily_search.get("searches", []):
                                if "serpapi" not in search.get(
                                    "google_trends_link", ""
                                ):
                                    search_id = insert_search(
                                        cursor, daily_search_id, search
                                    )

                                    if search_id is not None:
                                        for related_query in search.get(
                                            "related_queries", []
                                        ):
                                            if "serpapi" not in related_query.get(
                                                "google_trends_link", ""
                                            ):
                                                insert_related_query(
                                                    cursor, search_id, related_query
                                                )

                                        for article in search.get("articles", []):
                                            insert_article(cursor, search_id, article)

            logger.info("Data inserted successfully into the database.")
        except Exception as e:
            logger.error(f"Error: Unable to insert data into the database - {e}")
        finally:
            connection.close()


if __name__ == "__main__":
    logger.debug("Starting the application.")
    # Get the Treanding searches
    trending_search_results = fetch_trending_google_search(
        google_params.get("api_key"),
        google_params.get("engine"),
        google_params.get("frequency"),
        google_params.get("geo"),
        google_params.get("hl"),
    )
    # Call the function to parse and insert data into the PostgreSQL database
    parse_and_insert(trending_search_results)
    logger.debug("Application finished.")
