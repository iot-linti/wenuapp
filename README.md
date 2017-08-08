wenuclient.py
-------------

`wenuclient.py` provee una API de alto nivel que permite modificar la base de
datos de Wenu de forma remota. Internamente `wenuclient.py` se comunica con el
servidor REST "wenuapi".

## Login

-CON USUARIO Y CONTRASEÑA:

    from wenuclient import *
    username = 'admin'
    password = 1234
    s = get_session('http://localhost:5000/login',username,password)
    server = Client('http://localhost:5000',s)

- OBTENER TOKEN DESDE LA SESSION:

    token = s.auth[0]

-CON TOKEN:

    s = requests.Session()
    s.auth = (token, None)
    server = Client('http://localhost:5000',s)

## Queries

REGISTRAR USUARIO:

    register_user('http://localhost:5000/user',username,password)

ACTUALIZAR TOKEN:

    server.refresh_token()

AGREGAR ELEMENTOS:

    server.Action(mote_id=3, command='turn_off', arguments='').create()
    server.Action(mote_id=4, command='turn_off', arguments='').create()

Listar elementos:

    for elemento in server.Action.list():
        print(elemento.command)

VER UN ELEMENTO:

    action = server.Action().get_by_id(1)

MODIFICAR ELEMENTO:

    action.viewed = True
    action.save()



VER LOS PERFIL DE USUARIOS, LISTANTO SUS ROLES E IMPRIMIENDOLOS (en el caso de no ser admin solo listara el detalle de su perfil. Si el admin
desea ver su perfil no enviar 'list'):

    def getUser():
        users = server.User.embedded('list', roles=1)
        for user in users:
            roles =  user.roles
            #print user.fields['username']
            print 'Username: ' + user.username
            print 'Roles:'
            for rol in roles:
                print rol['rolname']
            print '----'


AGREGAR UN ROL A UN USUARIO:

    server.Roletable(user_id=46,role_id=1).create()

ELIMINAR USUARIO:

    user = server.User.get_by_id(id)
    user.remove()

ELIMINAR ACTION:

    server.Action(_id=27).remove()

LISTAR MEASUREMENTS USANDO WHERE:

    measurements = server.Measurement.where(mota_id="linti_cocina")
    for measure in measurements:
        print 'Mote id: {}'.format(measure.mote_id)
        print 'Temperature: {}'.format(measure.temperature)
        print 'Date: {}'.format(measure._created)
        print "--------"
