from fabric.api import local, cd
import os

def kapacitor(module):
    #with cd("/home/vagrant/go/src/github.com/influxdata/kapacitor"):
    local('cd /home/vagrant/go/src/github.com/influxdata/kapacitor; go run ./cmd/kapacitord/main.go -config udf/agent/examples/{}/{}.conf'.format(module, module))

def spiritenergy():
    easy_define("spiritenergy")
    enable("spiritenergy")

def threshold():
    easy_define("threshold")
    enable("threshold")

def spirit():
    easy_define("spirit")
    enable("spirit")

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
    local('cd /home/vagrant/go/src/github.com/influxdata/kapacitor; go run cmd/kapacitor/main.go define {} -type {} -dbrp {} -tick {}'.format(module, type, db, script))


def log(module, n="10"):
    local('tail -n {} /home/vagrant/var/{}/kapacitor.log'.format(n, module))


def init(module):
    if os.path.exists('/vagrant/udf/agent/examples/{}'.format(module)):
        local('echo Module {} already exists. Perhaps delete the module or choose a new name.'.format(module))
    else:
        local('mkdir /vagrant/udf/agent/examples/{}'.format(module))
        local('sed -e "s/\${{Module}}/{}/g" /vagrant/udf/templates/template.py > /vagrant/udf/agent/examples/{}/{}.py'.format(module.capitalize(), module, module))
        local('sed -e "s/\${{module}}/{}/g" /vagrant/udf/templates/template.conf > /vagrant/udf/agent/examples/{}/{}.conf'.format(module, module, module))
        local('sed -e "s/\${{module}}/{}/g" /vagrant/udf/templates/template.tick > /vagrant/udf/agent/examples/{}/{}.tick'.format(module, module, module))

def delete(module):
    clean(module)
    local('rm -rf /vagrant/udf/agent/examples/{}'.format(module))


def clean(module):
    '''deletes kapacitor data for the module'''
    local('rm -rf /home/vagrant/var/{}'.format(module))

def list():
    local('cd /home/vagrant/go/src/github.com/influxdata/kapacitor; go run cmd/kapacitor/main.go list tasks')

def enable(module):
    local('cd /home/vagrant/go/src/github.com/influxdata/kapacitor; go run cmd/kapacitor/main.go enable {}'.format(module))

def reload(module):
    local('cd /home/vagrant/go/src/github.com/influxdata/kapacitor; go run cmd/kapacitor/main.go reload {}'.format(module))

def build(args):
    local('cd /home/vagrant/go/src/github.com/influxdata/kapacitor; ./build.py {}'.format(args))

def build_environment():
    if os.path.isdir("/home/vagrant/anaconda2/envs/ims_web"):
        local('sudo /home/vagrant/anaconda2/bin/conda env remove -n ims_web -y')
    #local('sudo PATH=$PATH:/usr/pgsql-9.5/bin /home/vagrant/anaconda2/bin/conda env create -f ./environments/ims_web.yml -p /home/vagrant/anaconda2/envs/ims_web')
    local('/home/vagrant/anaconda2/bin/conda env create -f ./environments/ims_web.yml -p /home/vagrant/anaconda2/envs/ims_web')