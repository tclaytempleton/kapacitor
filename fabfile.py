from fabric.api import local, cd

def kapacitor(module):
    #with cd("/home/vagrant/go/src/github.com/influxdata/kapacitor"):
    local('cd /home/vagrant/go/src/github.com/influxdata/kapacitor; go run ./cmd/kapacitord/main.go -config udf/agent/examples/{}/{}.conf'.format(module, module))


def easy_define(module, type="stream"):
    '''
    in the case that
    a) the database, module, and script all have name <module> and
    b) are located in folder /vagrant/udf/agent/examples/<module>
    '''
    script = 'udf/agent/examples/{}/{}.tick'.format(module, module)
    db =  '{}.autogen'.format(module)
    define(module, db, script, type)


def define(module, db, script, type="stream"):
    local('cd /home/vagrant/go/src/github.com/influxdata/kapacitor; go run cmd/kapacitor define {} -type {} -dbrp {} -tick {}'.format(module, type, db, script))


def log(module, n="10"):
    local('tail -n {} /home/vagrant/var/{}/kapacitor.log'.format(n, module))