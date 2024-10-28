import requests

class Spotify():
    SHOW_ID:str
    CLIENT_ID:str
    CLIENT_SECRET:str
    BEARER_TOKEN:str
    ENDPOINT_ACCOUNT='https://accounts.spotify.com/api'
    ENDPOINT_API='https://api.spotify.com/v1'
    
    def __init__(self, client_id, client_secret):
        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret
        self.BEARER_TOKEN = self._getBearerToken()
    
    def _getBearerToken(self) -> str:
        data = self._post(
            f"{self.ENDPOINT_ACCOUNT}/token",
            f"grant_type=client_credentials&client_id={self.CLIENT_ID}&client_secret={self.CLIENT_SECRET}"
        )
        if 'access_token' in data.keys():
            return data['access_token']
        return ''
    
    def _post(self, endpoint:str, data:str="") -> dict:
        """Sends a POST request to the given Spotify API endpoint"""
        return requests.post(
            endpoint,
            headers= {'Content-type': 'application/x-www-form-urlencoded'},
            data=data).json()
    
    def _get(self, endpoint:str) -> dict:
        """Sends a GET request to the given Spotify API endpoint, uses BEARER token Auth"""
        return requests.get(
            endpoint,
            headers={'Authorization': f"Bearer {self.BEARER_TOKEN}"}
        ).json()
    
    def episodes(self, show_id:str, limit:int=5, offset:int=0) -> dict:
        """Gets the recent episodes for the given Show"""
        return self._get(f"{self.ENDPOINT_API}/shows/{show_id}/episodes?limit={str(limit)}&offset={str(offset)}")
    
    def allEpisodes(self, show_id:str) -> list:
        """Gets all episodes for the given Show"""
        response = self.episodes(show_id, limit=50)
        episodes = response['items']
        
        while response['next'] is not None:
            newResponse = self._get(response['next'])
            if 'items' in newResponse:
                for item in newResponse['items']:
                    episodes.append(item)
            response = newResponse
        
        return episodes