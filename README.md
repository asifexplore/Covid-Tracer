# 2103-covid-tracer

This is a SIT ICT2103 project developed using python.

### The team consists of 
@GeraldHeng
@Luxreus
@TanYuHui
@NJinng
Myself

### Installation Guide
- Have Python version 3.8 or newer installed
- Ensure that is in your PATH for windows systems: https://projects.raspberrypi.org/en/projects/using-pip-on-windows/4
- For MacOS or other Linux systems, ensure that pip is installed: https://phoenixnap.com/kb/install-pip-mac
- With choice of IDE, open source code file of 2103-covid-tracer as a project (Visual Studio Code (VSC) for Windows will be used as example).
- In 2103-covid-tracer main project dir, create a virtual environment by running the following command:
```
python -m venv venv
```
- for VSC users, the following pop-up should appear at the bottom right of the screen: Click Yes
![image](https://user-images.githubusercontent.com/58392111/144270864-f30e1d59-5421-481d-b151-19e83a5a2649.png)
- Otherwise, change dir to the following to access venv: Type 'Activate' or 'Activate.ps1' and press enter after successful cd
```
cd /your/path/to/dir/venv/Scripts
C:/your/path/to/dir/venv/Scripts/Activate
```
- The dir in cmd terminal should now look something like this: 
- ![image](https://user-images.githubusercontent.com/58392111/144272311-04364b2e-00ce-4111-baa2-8b882308a638.png)
- run pip install requirements.txt
```
pip install -r requirements.txt
```
- To run COVID Tracer in the RDBMS version, run the following:
```
python -u "c:\your\path\to\dir\2103-covid-tracer\rdbms_part\main.py"
```
- To run COVID Tracer in the NoSQL version, run the following:
```
python -u "c:\your\path\to\dir\2103-covid-tracer\no_sql_part\main.py"
```
### Note
- helper dir contains the csv data files used for the project. 
- rdbms_part contains the mysql part of the project.
- no_sql_part contains the mongodb + neo4j part of the project.
- please run python main.py to run the project.
- http://localhost:3000/ or http://127.0.0.1:3000/ will be the url for the flask application
- db_statements dir contains all the developed db complex/mix statements.
- templates dir contains all html files developed for Covid Tracer.
- constants.py contains static variables that can be reused often, eg. table_name.

### Current UI

![Imgur Image](https://imgur.com/kOAcRKv.jpg)
![Imgur Image](https://imgur.com/0G08RBn.jpg)
![Imgur Image](https://imgur.com/ODLtOsn.jpg)
![Imgur Image](https://imgur.com/Zpiwab8.jpg)

### Resources

###### SQL Cloud Login Details

https://auth-db595.hostinger.com/index.php?db=u696578939_2103_covid
Username: u696578939_2103_admin
Password: jDHKIXZb+U0

###### NOSQL MONGO Cloud Login Details

URI: mongodb+srv://admin:tJbJLK8YiYkDKYg@cluster0.96usv.mongodb.net/?retryWrites=true&w=majority
Username: admin
Password: tJbJLK8YiYkDKYg

###### Neo4J Cloud Login Details

URI: neo4j+s://c6e9b0ba.databases.neo4j.io
Username: neo4j
Password: ookMFGysaMn9Iwy80SFMPKQazP1BSehgn1ocB4AWiig

###### ERD

- https://lucid.app/lucidchart/538ee0a6-b669-4925-9dfc-a98d42d9ddb9/edit?invitationId=inv_c0b85598-0396-4a3c-9a37-211deb36c3c5&page=0_0#

###### Setup virtual environment

- https://realpython.com/python-virtual-environments-a-primer/
- https://github.com/IartemidaI/CRUD-operation-at-mySQL/blob/master/start.py
- https://www.datacamp.com/community/tutorials/mysql-python

###### lat lng in mysql

- https://stackoverflow.com/questions/12504208/what-mysql-data-type-should-be-used-for-latitude-longitude-with-8-decimal-places
- https://stackoverflow.com/questions/159255/what-is-the-ideal-data-type-to-use-when-storing-latitude-longitude-in-a-mysql

###### Area and landmark data

- https://en.wikipedia.org/wiki/Regions_of_Singapore

###### Login Auth

https://github.com/tecladocode/simple-flask-template-app/blob/feature/login_next/app.py

###### MongoDB

https://github.com/robbyparlan/Flask-Mongodb/blob/master/mongo.py

- Check update success
  https://stackoverflow.com/questions/43971543/pymongo-how-to-check-if-the-update-was-successful

- Update array in object
  https://stackoverflow.com/questions/17288439/mongodb-how-to-insert-additional-object-into-object-collection

- Update
  https://www.w3schools.com/python/python_mongodb_update.asp
