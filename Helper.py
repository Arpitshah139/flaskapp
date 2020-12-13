import jwt
import datetime
class Mongo:
    Dbname = 'imdb'
    collectionname = 'imdbdata'
    jwtsecret = 'test123'

class IMDB:
    popularity = '99popularity'
    director = 'director'
    genre = 'genre'
    imdb_score = 'imdb_score'
    name = 'name'

class QueryType:
    many = "many"
    one = "one"

class CommanFunction:
    @staticmethod
    def encode_auth_token(userdata):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=10),
                'iat': datetime.datetime.utcnow(),
                'uid': userdata['uid'],
                'role' : userdata['role']
            }
            return jwt.encode(
                payload,
                Mongo.jwtsecret,
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, Mongo.jwtsecret)
            return payload['role']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


