https://www.digitalocean.com/community/articles/how-to-deploy-a-flask-application-on-an-ubuntu-vps
sudo apt-get install python-dev
sudo apt-get install libevent-dev
sudo apt-get install libxml2-dev
sudo apt-get install libxslt1-dev 
sudo apt-get install -y zlib1g-dev


# Setting up Dokku
# - https://www.digitalocean.com/community/articles/how-to-use-the-dokku-one-click-digitalocean-image-to-deploy-a-python-flask-app

# ssh keys
# - https://www.digitalocean.com/community/articles/how-to-use-ssh-keys-with-digitalocean-droplets
ssh-keygen

# Enter file in which to save the key (/home/sehrope/.ssh/id_rsa): id_rsa_digital_ocean
mv id_rsa_digital_ocean* ~/.ssh/.
cat ~/.ssh/id_rsa_digital_ocean.pub | ssh root@sofly.co "cat >> ~/.ssh/authorized_keys" 

# tell ssh to use identify file for ssh
sudo vi ~/.ssh/config
# paste this in
Host sofly.co
  User root
  IdentityFile ~/.ssh/id_rsa_digital_ocean

# remove root login on remote host
ssh root@sofly.co
vi /etc/ssh/sshd_config
# paste this in
PermitRootLogin without-password

# login and install dokku plugins

# install MongoDB and Memcached plugins
# - https://github.com/progrium/dokku/wiki/Plugins#community-plugins

# install plugins 
cd /var/lib/dokku/plugins

# mongodb
# - https://github.com/jeffutter/dokku-mongodb-plugin 
git clone https://github.com/jeffutter/dokku-mongodb-plugin.git /var/lib/dokku/plugins/mongodb

# memcached
cd /var/lib/dokku/plugins
git clone https://github.com/jezdez/dokku-memcached-plugin memcached

# link plugin
# - https://github.com/rlaneve/dokku-link
git clone https://github.com/rlaneve/dokku-link.git link

# do install
dokku plugins-install

# optional: if setting up new droplet
# verify sofly repo setup
git remote rm dokku 
git remote add dokku dokku@sofly.co:sofly.co
git push dokku master

# set flask config
dokku config:set sofly.co FLASK_CONFIG=production

# create memcached
dokku memcached:create sofly.co

# create mongodb database
dokku mongodb:start
dokku mongodb:create sofly.co sofly

# manual start with docker
# docker run -t -i -e PORT=5000 app/sofly /bin/bash -c "/start web"

# install npm and less
sudo apt-add-repository ppa:chris-lea/node.js
sudo apt-get update
sudo apt-get install nodejs
sudo npm install -g less