Torrent9 CouchPotato provider
============================

##Installation

cloner le repository dans le répertoire customs_plugins de CouchPotato

Installer le fichier **namer_check.py** depuis le repos https://github.com/TimmyOtool/namer_check

certaines librairies doivent être ajoutées à couchpotato dans CouchPotatoServer/libs:

cfscrape

et ses dépendances:

js2py

pyjsparser

pytz

tzlocal

dans le répertoire de couchpotato (/var/packages/couchpotatoserver-custom/target/var/CouchPotatoServer sur syno):

pip install --target=libs/ cfscrape


Si pip n'est pas disponible:

wget https://bootstrap.pypa.io/get-pip.py

python get-pip.py

##Utilisation

Activer le founisseur dans les paramétres de CouchPotato
