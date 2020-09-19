import json

import requests


class VagalumeAPI:
    api_key = ''
    base_url = 'https://api.vagalume.com.br'

    def __init__(self, api_key: str):
        if not api_key:
            raise Exception('api_key is required')

        self.api_key = api_key

    def get_artist(self, artist: str):
        url = f'{self.base_url}/{artist}/index.js'
        response = requests.get(url)
        data = json.loads(response.content)

        return data['artist']

    def get_music(self, artist: str, music: str):
        counter = 1
        # while True:
        try:
            params = {
                'art': artist,
                'mus': music,
                'apikey': self.api_key,
            }
            url = f'{self.base_url}/search.php'

            response = requests.get(url, params=params)

            data = json.loads(response.content)
            return data
        except Exception as e:
            print(f'erro ao baixar a música nome: {music} artista: {artist}')
            print(f'counter: {counter} result: {response.content} headers: {response.headers}', e)
            raise e

