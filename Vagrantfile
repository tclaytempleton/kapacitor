# -*- mode: ruby -*-
# vi: set ft=ruby :


#Bootstrap script for installing Go and setting correct environments
$bootstrapScript = <<SCRIPT
GO_VERSION=1.7
echo 'Updating and installing Ubuntu packages...'
sudo apt-get update
echo 'Downloading go$GO_VERSION.linux-amd64.tar.gz'
wget –quiet https://storage.googleapis.com/golang/go$GO_VERSION.linux-amd64.tar.gz
echo 'Unpacking go language'
sudo tar -C /usr/local -xzf go$GO_VERSION.linux-amd64.tar.gz
echo 'Setting up correct env. variables'
echo "export GOPATH=/home/vagrant/go" >> /home/vagrant/.bashrc
echo "export PATH=$PATH:$GOPATH/bin:/usr/local/go/bin" >> /home/vagrant/.bashrc
mkdir -p /home/vagrant/go/src/github.com/influxdata
ln -s /vagrant /home/vagrant/go/src/github.com/influxdata/kapacitor
export GOPATH=/home/vagrant/go
export PATH=$PATH:$GOPATH/bin:/usr/local/go/bin
cd /home/vagrant/go/src/github.com/influxdata/kapacitor
go build ./cmd/kapacitor
go build ./cmd/kapacitord

cd /home/vagrant
sudo apt-get install -y python-pip
sudo apt-get install -y fabric
wget https://repo.continuum.io/archive/Anaconda2-4.2.0-Linux-x86_64.sh -O anaconda2.sh
bash anaconda2.sh -b -p /home/vagrant/anaconda2
echo "export PATH=/home/vagrant/anaconda2/bin:$PATH" >> /home/vagrant/.bashrc

mkdir /home/vagrant/var

rm /home/vagrant/go1.7.linux-amd64.tar.gz
rm anaconda2.sh

pip install protobuf==3.0.0b2

cd /home/vagrant
wget https://dl.influxdata.com/influxdb/releases/influxdb_1.1.0_amd64.deb
sudo dpkg -i influxdb_1.1.0_amd64.deb
rm influxdb_1.1.0_amd64.deb

wget https://grafanarel.s3.amazonaws.com/builds/grafana_3.1.1-1470047149_amd64.deb
sudo apt-get install -y adduser libfontconfig
sudo dpkg -i grafana_3.1.1-1470047149_amd64.deb
rm grafana_3.1.1-1470047149_amd64.deb

sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9
sudo add-apt-repository 'deb [arch=amd64,i386] https://cran.rstudio.com/bin/linux/ubuntu xenial/'
sudo apt-get update
sudo apt-get install r-base
sudo mkdir -p /usr/local/lib64/R/library
sudo R -e 'install.packages("lmtest", "/usr/local/lib64/R/library", repos="http://cran.us.r-project.org")'
conda install -c r rpy2

SCRIPT

$startupScript = <<SCRIPT
sudo service influxdb start
sudo service grafana-server start

SCRIPT


# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  # Using Ubuntu 14.04
  config.vm.box = "bento/ubuntu-16.04"
  # Forwarding port 8080 to local 8080.
  config.vm.network "forwarded_port", guest: 8080, host: 8080
  config.vm.network "forwarded_port", guest: 9092, host: 9092
  config.vm.network "forwarded_port", guest: 3000, host: 3001
  config.vm.network "forwarded_port", guest: 8086, host: 8086
  # Setting virtualbox specs
  config.vm.provider "virtualbox" do |vb|
      vb.memory = "1024"
      vb.cpus = 2
  end
  #Calling bootstrap setup
  config.vm.provision "shell", privileged: false, inline: $bootstrapScript
  config.vm.provision "shell", run: "always", privileged: false, inline: $startupScript
end
