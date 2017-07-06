INICIANDO EL CLIENTE:
-CON USUARIO Y CONTRASEÑA
    username = 'admin'
    password = 1234
    s = get_session('http://localhost:5000/login',username,password)
    server = Client('http://localhost:5000',s)

- OBTENER TOKEN DESDE LA SESSION
    token = s.auth[0]

-CON TOKEN
    s = requests.Session()
    s.auth = (token, None)
    server = Client('http://localhost:5000',s)

REGISTRAR USUARIO:
    register_user('http://localhost:5000/user',username,password)

ACTUALIZAR TOKEN:
    server.refresh_token()

AGREGAR ELEMENTOS:
    server.Action(mote_id=3, command='turn_off', arguments='').create()
    server.Action(mote_id=4, command='turn_off', arguments='').create()

VER UN ELEMENTO
    action = server.Action().get_by_id(1)

MODIFICAR ELEMENTO
    action.__setattr__('viewed', True)
    action.save()



VER LOS PERFIL DE USUARIOS, LISTANTO SUS ROLES E IMPRIMIENDOLOS (en el caso de no ser admin solo listara el detalle de su perfil. Si el admin
desea ver su perfil no enviar 'list'):

    def getUser():
        arg2 = {
            "roles" : 1,
        }
        users = server.User.embedded('list',**arg2)
        for user in users:
            roles =  user.__getattr__('roles')
            #print user.__dict__['fields']['username']
            print 'Username: ' + user.__getattr__('username')
            print 'Roles:'
            for rol in roles:
                print rol['rolname']
            print '----'


AGREGAR UN ROL A UN USUARIO:
    server.Roletable(user_id=46,role_id=1).create()

ELIMINAR USUARIO :
    user = server.User.get_by_id(id)
    user.remove()

ELIMINAR ACTION:
    server.Action(_id=27).remove()

LISTAR MEASUREMENTS USANDO WHERE:
        arg = {
        "mota_id" : "'linti_cocina'"
    }

    measurements = server.Measurement.where(**arg)
    for measure in measurements:
        print 'Mote id: {}'.format(measure.__getattr__('mote_id'))
        print 'Temperature: {}'.format(measure.__getattr__('temperature'))
        print 'Date: {}'.format(measure.__getattr__('_created'))
        print "--------"
