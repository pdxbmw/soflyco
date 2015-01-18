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

# rebuild without git push
git clone https://github.com/scottatron/dokku-rebuild rebuild

# do install
dokku plugins-install

# goto domain and finish dokku install

# optional: if setting up new droplet
# verify sofly repo setup
git remote rm dokku 
git remote add dokku dokku@sofly.co:www
git push dokku master

# set flask config
dokku config:set www FLASK_CONFIG=production

# create memcached
dokku memcached:create www

# create mongodb database
dokku mongodb:start
dokku mongodb:create www sofly
dokku mongodb:link www sofly

# manual start with docker
# docker run -t -i -e PORT=5000 dokku/www /bin/bash -c "/start web"
# docker restart `cat /home/dokku/sofly.co/CONTAINER`

# install npm and less
sudo apt-add-repository ppa:chris-lea/node.js
sudo apt-get update
sudo apt-get install nodejs
sudo npm install -g less

# add ssl support
mkdir /home/dokku/www/tls

# create server.key
-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----

# create server.crt
-----BEGIN CERTIFICATE-----
MIIHLjCCBhagAwIBAgIDERsTMA0GCSqGSIb3DQEBCwUAMIGMMQswCQYDVQQGEwJJ
TDEWMBQGA1UEChMNU3RhcnRDb20gTHRkLjErMCkGA1UECxMiU2VjdXJlIERpZ2l0
YWwgQ2VydGlmaWNhdGUgU2lnbmluZzE4MDYGA1UEAxMvU3RhcnRDb20gQ2xhc3Mg
MSBQcmltYXJ5IEludGVybWVkaWF0ZSBTZXJ2ZXIgQ0EwHhcNMTQwNjE2MTQ0NDMy
WhcNMTUwNjE3MDY1ODMxWjBHMQswCQYDVQQGEwJVUzEVMBMGA1UEAxMMd3d3LnNv
Zmx5LmNvMSEwHwYJKoZIhvcNAQkBFhJ3ZWJtYXN0ZXJAc29mbHkuY28wggIiMA0G
CSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQC216jxYWWaODGRFxbwk/SAjsA2uhFv
5/UOVlYvtWPafafHbEhT77bXc0zguNVlvd//iYsoOC/LFn3s3zlFZpieN12nftYc
418FdhglCEMa3M/dVt2Ov5kScTq2Gv9RHf5RZ6MZAT/O6EO0ar8c8BTeaFB7H6rV
fyL1ydZVJ7VvM8xa+J31cioH909BZ3sloDj98Npknc9HPZa/5Hq29DONHPB5ZxBX
LD/vZMoKNnz6K2R/IjB4v7F581u7wXiAo7On565kkYjNHYuP7Yt2e+SgRPdlrICP
x3Axd5fq3EZjVrPYmLaBTI9zzhgZlbe485rDpb1R3mN98Ck0zMQrDkIrqcmPPDLm
SoUY+X6weLnmPyPC9jyj53gzuYQBeDSceyo+ER2gscg+gh1zF9d8Wq38EEvpn566
RdiRK7HOwIZLEvPOenrqo9+jFm1m15diVwzjmZRNSb9NjkDgVXvp/fNjHQUGiUuH
xaiVLviKkRrbak0t1+8YST3B97DfhHnk0tIIYyILlnWV1LNBsClRBzmTgVJ0tuhH
HYTUlP3ncLJ7ryxy9QDCCzx7uYpfqdflqrEgaNGNc0z8Io5Nkr7hl4xKs2371/7F
DxTGsS4KQzkNwp0aTKy8SWqgRlksI3nA6BTlRbaRm5nD1qdLu0VtaxVGn2SOgFI8
q6dhQEICo1LFBQIDAQABo4IC2zCCAtcwCQYDVR0TBAIwADALBgNVHQ8EBAMCA6gw
EwYDVR0lBAwwCgYIKwYBBQUHAwEwHQYDVR0OBBYEFMtDlC1DMOZX+hN33NluEkKC
AMLgMB8GA1UdIwQYMBaAFOtCNNCYsKuf9BtrCPfMZC7vDixFMCEGA1UdEQQaMBiC
DHd3dy5zb2ZseS5jb4IIc29mbHkuY28wggFWBgNVHSAEggFNMIIBSTAIBgZngQwB
AgEwggE7BgsrBgEEAYG1NwECAzCCASowLgYIKwYBBQUHAgEWImh0dHA6Ly93d3cu
c3RhcnRzc2wuY29tL3BvbGljeS5wZGYwgfcGCCsGAQUFBwICMIHqMCcWIFN0YXJ0
Q29tIENlcnRpZmljYXRpb24gQXV0aG9yaXR5MAMCAQEagb5UaGlzIGNlcnRpZmlj
YXRlIHdhcyBpc3N1ZWQgYWNjb3JkaW5nIHRvIHRoZSBDbGFzcyAxIFZhbGlkYXRp
b24gcmVxdWlyZW1lbnRzIG9mIHRoZSBTdGFydENvbSBDQSBwb2xpY3ksIHJlbGlh
bmNlIG9ubHkgZm9yIHRoZSBpbnRlbmRlZCBwdXJwb3NlIGluIGNvbXBsaWFuY2Ug
b2YgdGhlIHJlbHlpbmcgcGFydHkgb2JsaWdhdGlvbnMuMDUGA1UdHwQuMCwwKqAo
oCaGJGh0dHA6Ly9jcmwuc3RhcnRzc2wuY29tL2NydDEtY3JsLmNybDCBjgYIKwYB
BQUHAQEEgYEwfzA5BggrBgEFBQcwAYYtaHR0cDovL29jc3Auc3RhcnRzc2wuY29t
L3N1Yi9jbGFzczEvc2VydmVyL2NhMEIGCCsGAQUFBzAChjZodHRwOi8vYWlhLnN0
YXJ0c3NsLmNvbS9jZXJ0cy9zdWIuY2xhc3MxLnNlcnZlci5jYS5jcnQwIwYDVR0S
BBwwGoYYaHR0cDovL3d3dy5zdGFydHNzbC5jb20vMA0GCSqGSIb3DQEBCwUAA4IB
AQCa9m5mvIZixvukrowpCO4tVzKoCwfis/xAPL6/sbFBQMVeLWsOqoEhF+RL/e6l
YcsNME32xv30GWywR94UD9Wd9+1W+gh2TrCkO9YhaWeUUhOTQQaZfeJVTQMhMSkI
W2jMF9eOrJOBs2cZb0zohQOS/7aIg794zf8dB5wFgmyO7jk6caSrs+cMVlekTSBe
eLdVVNoT+6rTm0j3/mfB9Z04aAdCX3xPy/TVbr4wFk3AWWuSUB4UnM/nGWCCP4RN
RDOwOyM0c32w9HWDCW7sgjYCG0uinM4O6jfE/rtljMjBzRr3OpaVfAJ4pke+bBAx
YD7daUCU8CyrqApHfmxIWd6U
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIGNDCCBBygAwIBAgIBGDANBgkqhkiG9w0BAQUFADB9MQswCQYDVQQGEwJJTDEW
MBQGA1UEChMNU3RhcnRDb20gTHRkLjErMCkGA1UECxMiU2VjdXJlIERpZ2l0YWwg
Q2VydGlmaWNhdGUgU2lnbmluZzEpMCcGA1UEAxMgU3RhcnRDb20gQ2VydGlmaWNh
dGlvbiBBdXRob3JpdHkwHhcNMDcxMDI0MjA1NDE3WhcNMTcxMDI0MjA1NDE3WjCB
jDELMAkGA1UEBhMCSUwxFjAUBgNVBAoTDVN0YXJ0Q29tIEx0ZC4xKzApBgNVBAsT
IlNlY3VyZSBEaWdpdGFsIENlcnRpZmljYXRlIFNpZ25pbmcxODA2BgNVBAMTL1N0
YXJ0Q29tIENsYXNzIDEgUHJpbWFyeSBJbnRlcm1lZGlhdGUgU2VydmVyIENBMIIB
IjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtonGrO8JUngHrJJj0PREGBiE
gFYfka7hh/oyULTTRwbw5gdfcA4Q9x3AzhA2NIVaD5Ksg8asWFI/ujjo/OenJOJA
pgh2wJJuniptTT9uYSAK21ne0n1jsz5G/vohURjXzTCm7QduO3CHtPn66+6CPAVv
kvek3AowHpNz/gfK11+AnSJYUq4G2ouHI2mw5CrY6oPSvfNx23BaKA+vWjhwRRI/
ME3NO68X5Q/LoKldSKqxYVDLNM08XMML6BDAjJvwAwNi/rJsPnIO7hxDKslIDlc5
xDEhyBDBLIf+VJVSH1I8MRKbf+fAoKVZ1eKPPvDVqOHXcDGpxLPPr21TLwb0pwID
AQABo4IBrTCCAakwDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMCAQYwHQYD
VR0OBBYEFOtCNNCYsKuf9BtrCPfMZC7vDixFMB8GA1UdIwQYMBaAFE4L7xqkQFul
F2mHMMo0aEPQQa7yMGYGCCsGAQUFBwEBBFowWDAnBggrBgEFBQcwAYYbaHR0cDov
L29jc3Auc3RhcnRzc2wuY29tL2NhMC0GCCsGAQUFBzAChiFodHRwOi8vd3d3LnN0
YXJ0c3NsLmNvbS9zZnNjYS5jcnQwWwYDVR0fBFQwUjAnoCWgI4YhaHR0cDovL3d3
dy5zdGFydHNzbC5jb20vc2ZzY2EuY3JsMCegJaAjhiFodHRwOi8vY3JsLnN0YXJ0
c3NsLmNvbS9zZnNjYS5jcmwwgYAGA1UdIAR5MHcwdQYLKwYBBAGBtTcBAgEwZjAu
BggrBgEFBQcCARYiaHR0cDovL3d3dy5zdGFydHNzbC5jb20vcG9saWN5LnBkZjA0
BggrBgEFBQcCARYoaHR0cDovL3d3dy5zdGFydHNzbC5jb20vaW50ZXJtZWRpYXRl
LnBkZjANBgkqhkiG9w0BAQUFAAOCAgEAIQlJPqWIbuALi0jaMU2P91ZXouHTYlfp
tVbzhUV1O+VQHwSL5qBaPucAroXQ+/8gA2TLrQLhxpFy+KNN1t7ozD+hiqLjfDen
xk+PNdb01m4Ge90h2c9W/8swIkn+iQTzheWq8ecf6HWQTd35RvdCNPdFWAwRDYSw
xtpdPvkBnufh2lWVvnQce/xNFE+sflVHfXv0pQ1JHpXo9xLBzP92piVH0PN1Nb6X
t1gW66pceG/sUzCv6gRNzKkC4/C2BBL2MLERPZBOVmTX3DxDX3M570uvh+v2/miI
RHLq0gfGabDBoYvvF0nXYbFFSF87ICHpW7LM9NfpMfULFWE7epTj69m8f5SuauNi
YpaoZHy4h/OZMn6SolK+u/hlz8nyMPyLwcKmltdfieFcNID1j0cHL7SRv7Gifl9L
WtBbnySGBVFaaQNlQ0lxxeBvlDRr9hvYqbBMflPrj0jfyjO1SPo2ShpTpjMM0InN
SRXNiTE8kMBy12VLUjWKRhFEuT2OKGWmPnmeXAhEKa2wNREuIU640ucQPl2Eg7PD
wuTSxv0JS3QJ3fGz0xk+gA2iCxnwOOfFwq/iI9th4p1cbiCJSS4jarJiwUW0n6+L
p/EiO/h94pDQehn7Skzj0n1fSoMD7SfWI55rjbRZotnvbIIp3XUZPD9MEI3vu3Un
0q6Dp6jOW6c=
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIHyTCCBbGgAwIBAgIBATANBgkqhkiG9w0BAQUFADB9MQswCQYDVQQGEwJJTDEW
MBQGA1UEChMNU3RhcnRDb20gTHRkLjErMCkGA1UECxMiU2VjdXJlIERpZ2l0YWwg
Q2VydGlmaWNhdGUgU2lnbmluZzEpMCcGA1UEAxMgU3RhcnRDb20gQ2VydGlmaWNh
dGlvbiBBdXRob3JpdHkwHhcNMDYwOTE3MTk0NjM2WhcNMzYwOTE3MTk0NjM2WjB9
MQswCQYDVQQGEwJJTDEWMBQGA1UEChMNU3RhcnRDb20gTHRkLjErMCkGA1UECxMi
U2VjdXJlIERpZ2l0YWwgQ2VydGlmaWNhdGUgU2lnbmluZzEpMCcGA1UEAxMgU3Rh
cnRDb20gQ2VydGlmaWNhdGlvbiBBdXRob3JpdHkwggIiMA0GCSqGSIb3DQEBAQUA
A4ICDwAwggIKAoICAQDBiNsJvGxGfHiflXu1M5DycmLWwTYgIiRezul38kMKogZk
pMyONvg45iPwbm2xPN1yo4UcodM9tDMr0y+v/uqwQVlntsQGfQqedIXWeUyAN3rf
OQVSWff0G0ZDpNKFhdLDcfN1YjS6LIp/Ho/u7TTQEceWzVI9ujPW3U3eCztKS5/C
Ji/6tRYccjV3yjxd5srhJosaNnZcAdt0FCX+7bWgiA/deMotHweXMAEtcnn6RtYT
Kqi5pquDSR3l8u/d5AGOGAqPY1MWhWKpDhk6zLVmpsJrdAfkK+F2PrRt2PZE4XNi
HzvEvqBTViVsUQn3qqvKv3b9bZvzndu/PWa8DFaqr5hIlTpL36dYUNk4dalb6kMM
Av+Z6+hsTXBbKWWc3apdzK8BMewM69KN6Oqce+Zu9ydmDBpI125C4z/eIT574Q1w
+2OqqGwaVLRcJXrJosmLFqa7LH4XXgVNWG4SHQHuEhANxjJ/GP/89PrNbpHoNkm+
Gkhpi8KWTRoSsmkXwQqQ1vp5Iki/untp+HDH+no32NgN0nZPV/+Qt+OR0t3vwmC3
Zzrd/qqc8NSLf3Iizsafl7b4r4qgEKjZ+xjGtrVcUjyJthkqcwEKDwOzEmDyei+B
26Nu/yYwl/WL3YlXtq09s68rxbd2AvCl1iuahhQqcvbjM4xdCUsT37uMdBNSSwID
AQABo4ICUjCCAk4wDAYDVR0TBAUwAwEB/zALBgNVHQ8EBAMCAa4wHQYDVR0OBBYE
FE4L7xqkQFulF2mHMMo0aEPQQa7yMGQGA1UdHwRdMFswLKAqoCiGJmh0dHA6Ly9j
ZXJ0LnN0YXJ0Y29tLm9yZy9zZnNjYS1jcmwuY3JsMCugKaAnhiVodHRwOi8vY3Js
LnN0YXJ0Y29tLm9yZy9zZnNjYS1jcmwuY3JsMIIBXQYDVR0gBIIBVDCCAVAwggFM
BgsrBgEEAYG1NwEBATCCATswLwYIKwYBBQUHAgEWI2h0dHA6Ly9jZXJ0LnN0YXJ0
Y29tLm9yZy9wb2xpY3kucGRmMDUGCCsGAQUFBwIBFilodHRwOi8vY2VydC5zdGFy
dGNvbS5vcmcvaW50ZXJtZWRpYXRlLnBkZjCB0AYIKwYBBQUHAgIwgcMwJxYgU3Rh
cnQgQ29tbWVyY2lhbCAoU3RhcnRDb20pIEx0ZC4wAwIBARqBl0xpbWl0ZWQgTGlh
YmlsaXR5LCByZWFkIHRoZSBzZWN0aW9uICpMZWdhbCBMaW1pdGF0aW9ucyogb2Yg
dGhlIFN0YXJ0Q29tIENlcnRpZmljYXRpb24gQXV0aG9yaXR5IFBvbGljeSBhdmFp
bGFibGUgYXQgaHR0cDovL2NlcnQuc3RhcnRjb20ub3JnL3BvbGljeS5wZGYwEQYJ
YIZIAYb4QgEBBAQDAgAHMDgGCWCGSAGG+EIBDQQrFilTdGFydENvbSBGcmVlIFNT
TCBDZXJ0aWZpY2F0aW9uIEF1dGhvcml0eTANBgkqhkiG9w0BAQUFAAOCAgEAFmyZ
9GYMNPXQhV59CuzaEE44HF7fpiUFS5Eyweg78T3dRAlbB0mKKctmArexmvclmAk8
jhvh3TaHK0u7aNM5Zj2gJsfyOZEdUauCe37Vzlrk4gNXcGmXCPleWKYK34wGmkUW
FjgKXlf2Ysd6AgXmvB618p70qSmD+LIU424oh0TDkBreOKk8rENNZEXO3SipXPJz
ewT4F+irsfMuXGRuczE6Eri8sxHkfY+BUZo7jYn0TZNmezwD7dOaHZrzZVD1oNB1
ny+v8OqCQ5j4aZyJecRDjkZy42Q2Eq/3JR44iZB3fsNrarnDy0RLrHiQi+fHLB5L
EUTINFInzQpdn4XBidUaePKVEFMy3YCEZnXZtWgo+2EuvoSoOMCZEoalHmdkrQYu
L6lwhceWD3yJZfWOQ1QOq92lgDmUYMA0yZZwLKMS9R9Ie70cfmu3nZD0Ijuu+Pwq
yvqCUqDvr0tVk+vBtfAii6w0TiYiBKGHLHVKt+V9E9e4DGTANtLJL4YSjCMJwRuC
O3NJo2pXh5Tl1njFmUNj403gdy3hZZlyaQQaRwnmDwFWJPsfvw55qVguucQJAX6V
um0ABj6y6koQOdjQK/W/7HW/lwLFCRsI3FU34oH7N4RDYiDK51ZLZer+bMEkkySh
NOsF/5oirpt9P/FlUQqmMGqz9IgcgA38corog14=
-----END CERTIFICATE-----

# change permissions
chown dokku:dokku server.*
chmod 600 server.*

# nginx.conf
upstream sofly.co { server 127.0.0.1:49154; }
server {
  listen              [::]:443 ssl spdy;
  listen              443 ssl spdy;
  server_name         www.sofly.co;
  ssl_certificate     /home/dokku/www/tls/server.crt;
  ssl_certificate_key /home/dokku/www/tls/server.key;

  keepalive_timeout   70;
  add_header          Alternate-Protocol  443:npn-spdy/2;

  location    / {
    proxy_pass  http://sofly.co;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $http_host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_set_header X-Forwarded-Port $server_port;
    proxy_set_header X-Request-Start $msec;
  }

}
server {
  listen      [::]:80;
  listen      80;
  server_name www.sofly.co;
  return 301 https://$host$request_uri;
}
server {
  listen               *:80;
  listen               *:443 ssl spdy;
  listen               [::]:80;
  listen               [::]:443 ssl spdy;
  server_name          sofly.co;
  ssl_certificate      /home/dokku/www/tls/server.crt;
  ssl_certificate_key  /home/dokku/www/tls/server.key;

  return 301 https://www.$host$request_uri;
}

# add nightly crawler
0 15 * * * bash -c ': | PATH="$PATH:/usr/local/bin" dokku run sofly.co python crawl.py' > /tmp/crawl.output