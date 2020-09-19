import logging
import os
from time import time

from dotenv import find_dotenv, load_dotenv

from src.infrastructure.database import Database
from src.infrastructure.services import VagalumeAPI

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
db_file = os.path.join(BASE_DIR, 'data', 'vagalume.db')
DB_URL = 'sqlite:///' + db_file


def main():
    logger = logging.getLogger(__name__)

    vagalume_apitoken = os.getenv('API_TOKEN_VAGALUME')

    vagalume = VagalumeAPI(vagalume_apitoken)

    db = Database(DB_URL)
    db.create_tables()

    artist = vagalume.get_artist('emicida')

    try:
        db.execute_query(
            f'INSERT INTO artist (id, name, url) VALUES (\'{artist["id"]}\', \'{artist["desc"]}\', \'{artist["url"]}\')'
        )
    except Exception as e:
        logger.error(e)

    LANGUAGES = {
        1: 'pt-BR',
        2: 'en-US',
        3: 'sp-ES',
        4: 'fr-FR',
        5: 'de-DE',
        6: 'it-IT',
        7: 'nl-NL',
        8: 'ja-JP',
        9: 'pt-PT',
        999999: 'other',
    }

    artist_id = artist["id"]
    artist_name = artist["desc"]

    query = 'INSERT INTO music (id, name, url, language, text, artist_id) VALUES (?, ?, ?, ?, ?, ?)'
    values = []

    try_list = [lyric['id'] for lyric in artist['lyrics']['item'][:5]]
    start = time()
    while not len(try_list) == 0:
        for lyric in artist['lyrics']['item'][:5]:
            try:
                if not lyric_was_processed(lyric, try_list):
                    logger.info(f'getting music {lyric["desc"]}')

                    music = vagalume.get_music(artist=artist_name, music=lyric['desc'])
                    mus = music['mus'][0]
                    variables = (mus["id"], mus["name"], mus["url"], LANGUAGES[mus["lang"]], mus["text"], artist_id)
                    values.append(variables)
                    try_list.remove(lyric['id'])
            except Exception as e:
                # when an error occur, continue to process another musics
                logger.error(f'erro ao processar a música id: {lyric["id"]} nome: {lyric["desc"]} artista: {artist_name}', e)
                continue

    print(f'Time taken: {time() - start}')

    try:
        db.execute_query(query, values)
    except Exception as e:
        logger.error(e)


def lyric_was_processed(lyric, try_list):
    return not lyric['id'] in try_list


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
