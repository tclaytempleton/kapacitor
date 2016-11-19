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
rm /home/vagrant/go1.7.linux-amd64.tar.gz
SCRIPT

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  # Using Ubuntu 14.04
  config.vm.box = "bento/ubuntu-16.04"
  # Forwarding port 8080 to local 8080.
  config.vm.network "forwarded_port", guest: 8080, host: 8080
  config.vm.network "forwarded_port", guest: 9092, host: 9092
  #Calling bootstrap setup
  config.vm.provision "shell", privileged: false, inline: $bootstrapScript
end