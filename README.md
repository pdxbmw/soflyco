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
cat ~/.ssh/id_rsa.pub | ssh root@dev.sofly.co "cat >> ~/.ssh/authorized_keys" 

# remove root login
ssh root@dev.sofly.co
vi /etc/ssh/sshd_config
PermitRootLogin without-password

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