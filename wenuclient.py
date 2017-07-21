#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from functools import wraps
import json
import requests
import logging
import getpass
from requests.models import Response

logging.basicConfig(level=logging.DEBUG)
logging.Logger(__name__, logging.DEBUG)


def validate_and_jsonify(func):
    '''
    Decorador, hace que un método que normalmente retorna una instancia
    de `requests.Response` con un cuerpo codificado en JSON pase a retornar
    el resultado de decodificar el mensaje JSON. Si la respuesta es un error
    el método lanzará una excepción.
    '''
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
        # FIXME: Cambiar para que lance una excepción con un
        # error específico si lo hubo
        assert http_request.status_code == 200 or http_request.status_code == 201 or http_request.status_code == 204
        return json.loads(http_request.text)

    return closure



def get_session(url,username,password):


    r = requests.get(url, auth=(username, password))
    item = r.json()
    assert r.status_code == 200 or r.status_code == 201
    token = item['token']

    s = requests.Session()
    s.auth = (token, None)
    return s

def register_user(url,username,password):
    payload = {'username': username, 'password': password}
    r = requests.post(url, data=payload)
    assert r.status_code == 201
    return True


class Entity(object):
    def __init__(self, **kwargs):
        '''
        Recibe como keyword arguments los campos y valores de la tabla
        '''
        self.fields = kwargs
        self.initialized = True

    def __getattr__(self, attr):
        '''
        Cada campo de la base de datos se puede acceder como un atributo
        de la instancia usando la notación habitual `entity.nombre_campo`,
        alternativamente se puede acceder al diccionario `fields` con
        `entity.fields`.
        '''
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
        '''
        `spawn_sublcass` es el método que debe ser utilizado para crear
        nuevas clases que representen tablas en la base de datos.
        '''
        entity = type(str(title), (cls,), {
            'server': server,
            'link': link,
        })
        return entity

    @classmethod
    def list(cls, args=None):
        '''
        Retorna una lista con todas las filas de la tabla actual en la
        base de datos. Cada fila será una instancia de una subclase
        de `Entity`.
        '''
        link = cls.link if args is None else '{}?{}'.format(cls.link, args)
        return [cls(**entry) for entry in cls.server.get(link)['_items']]

    @classmethod
    def get_by_id(cls, _id, args=None):
        assert cls.link != 'measurement'
        if args is None:
            link = '{}/{}'.format(cls.link, _id)
        else:
            link = '{}/{}?{}'.format(cls.link, _id, args)
        return cls(**cls.server.get(link))


    @classmethod
    def where(cls,arg='', **kwargs):
        results = cls.server.get('{}?where={}&{}'.format(cls.link, json.dumps(kwargs),arg))
        return (cls(**result) for result in results['_items'])

    @classmethod
    def embedded(cls,arg='',**kwargs):
        results = cls.server.get('{}?embedded={}&{}'.format(cls.link, json.dumps(kwargs),arg))
        return (cls(**result) for result in results['_items'])

    @classmethod
    def first_where(cls,**kwargs):
        try:
            return next(cls.where(**kwargs))
        except StopIteration:
            return None

    def __str__(self):
        return str(self.fields)

    def regular_fields(self):
        '''
        Diccionario con las entradas de `self.fields` cuyo nombre no empieza
        con `_`.
        '''
        return {k: v for k, v in self.fields.items() if not k.startswith('_')}

    def remove(self):
        response = self.server.delete(
        '{}/{}'.format(self.link, self.fields['_id']))
        return response

    def create(self):
        '''
        Crea una nueva fila en la base de datos con los datos de la instancia
        actual.
        '''
        response = self.server.post(self.link, json=self.fields)
        self.fields.update(response)
        return response

    def save(self):
        '''
        Actualiza una fila de la base de datos usando los datos cargados en
        la instancia actual.
        '''
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
        # `measurement` no es una tabla reconocida por Eve, por lo que
        # el servidor no la reporará. Forzamos la creación de una clase
        # que la represente del lado del cliente.
        extra_entities = [
            {u'title': u'Measurement', u'href': u'measurement'},
        ]
        self.entities = self._spawn_entities(insert=extra_entities)


    def refresh_token(self):

        r = self.session.get('/'.join((self.url, 'refreshtoken')))
        item = r.json()
        assert r.status_code == 200 or r.status_code == 201    or r.status_code == 204
        token = item['token']

        s = requests.Session()
        s.auth = (token, None)
        self.session = s



    def __getattr__(self, attr):
        '''
        Las clases que representan a cada tabla pueden ser accedidas como
        atributos de las instancias de `Server`.
        '''
        try:
            return self.entities[attr]
        except KeyError:
            raise AttributeError(
                '{} has no attribute {}'.format(type(self), attr)
            )

    def _validate(self, response):
        response.raise_for_status()

    def _spawn_entities(self, insert=None):
        '''
        Hace una petición `GET` a la URL base del servidor Eve, el mismo
        retornará las tablas disponibles, a excepción de `Measurement` que
        es manejada de forma especial en el servidor ya que se encuentra
        en una base de datos InfluxDB.
        '''
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

    @validate_and_jsonify
    def delete(self, route):
        response = self.session.get('/'.join((self.url, route)))
        r = self.session.delete('/'.join((self.url, route)))
        delete_response = Response()
        delete_response.status_code = r.status_code
        delete_response._content = response._content
        delete_response._text = response.text
        return delete_response

