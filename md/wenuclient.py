from functools import wraps
import json
import requests
import logging

logging.basicConfig(level=logging.DEBUG)
logging.Logger(__name__, logging.DEBUG)


def validate_and_jsonify(func):
    @wraps(func)
    def closure(self, route, *args, **kwargs):
        logger = logging.getLogger(__name__)
        http_request = func(self, route, *args, **kwargs)
        logger.debug(
            'Request to route %s returned status %d',
            route,
            http_request.status_code,
        )
        logger.debug(http_request.text)
        assert http_request.status_code == 200 or http_request.status_code == 201
        return json.loads(http_request.text)

    return closure


class Entity(object):
    def __init__(self, **kwargs):
        self.fields = kwargs
        self.initialized = True

    def __getattr__(self, attr):
        try:
            return self.fields[attr]
        except KeyError:
            raise AttributeError(
                '{} has no attribute {}'.format(type(self), attr)
            )

    def __setattr__(self, attr, val):
        if 'initialized' in self.__dict__ and attr in self.fields:
            self.fields[attr] = val
        else:
            object.__setattr__(self, attr, val)

    @classmethod
    def spawn_subclass(cls, title, link, server):
        entity = type(str(title), (cls,), {
            'server': server,
            'link': link,
        })
        return entity

    @classmethod
    def list(cls):
        return [cls(**entry) for entry in cls.server.get(cls.link)['_items']]

    @classmethod
    def get_by_id(cls, _id):
        return cls(**cls.server.get('{}/{}'.format(cls.link, _id)))

    @classmethod
    def where(cls, **kwargs):
        results = cls.server.get('{}?where={}'.format(cls.link, json.dumps(kwargs)))
        return (cls(**result) for result in results['_items'])

    @classmethod
    def first_where(cls, **kwargs):
        try:
            return next(cls.where(**kwargs))
        except StopIteration:
            return None

    def __str__(self):
        return str(self.fields)

    def regular_fields(self):
        return {k: v for k, v in self.fields.items() if not k.startswith('_')}

    def create(self):
        response = self.server.post(self.link, json=self.fields)
        self.fields.update(response)
        return response

    def save(self):
        response = self.server.put(
            '{}/{}'.format(self.link, self.fields['_id']),
            json=self.regular_fields(),
            etag=self.fields['_etag'],
        )
        return response


class Client(object):
    def __init__(self, url, session=None):
        if session is None:
            self.session = requests.Session()
        else:
            self.session = session

        self.url = url
        extra_entities = [
            {u'title': u'Measurement', u'href': u'measurement'},
        ]
        self.entities = self._spawn_entities(insert=extra_entities)


    def __getattr__(self, attr):
        try:
            return self.entities[attr]
        except KeyError:
            raise AttributeError(
                '{} has no attribute {}'.format(type(self), attr)
            )

    def _validate(self, response):
        response.raise_for_status()

    def _spawn_entities(self, insert=None):
        http_response = self.session.get(self.url)
        self._validate(http_response)
        logger = logging.getLogger()
        logger.debug(http_response.text)
        response = json.loads(http_response.text)
        entities = {}

        if insert is not None:
            for entry in insert:
                response['_links']['child'].append({
                    'title': entry['title'],
                    'href': entry['href'],
                })

        for child in response['_links']['child']:
            title = child['title'].title().replace('_', '')
            entities[title] = Entity.spawn_subclass(
                title=title,
                link=child['href'],
                server=self,
            )

        return entities

    @validate_and_jsonify
    def get(self, route):
        return self.session.get('/'.join((self.url, route)))

    @validate_and_jsonify
    def put(self, route, json, etag):
        return self.session.put(
            '/'.join((self.url, route)),
            json=json,
            headers={'If-Match': etag}
        )

    @validate_and_jsonify
    def post(self, route, json):
        return self.session.post('/'.join((self.url, route)), json=json)


if __name__ == '__main__':
    s = Client('http://localhost:5000')
    print(s.entities)
    print(s.Mote)
    print(s.Mote.list())
