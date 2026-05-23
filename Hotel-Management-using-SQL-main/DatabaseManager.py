import mysql.connector as connector
import pandas as pd
import os
import time 

def get_db_con():

    path_secret= os.getenv('DB_PASSWORD')

    try:

        with open(path_secret, 'r') as f:
            db_pwd = f.read().strip()
    
    except FileNotFoundError:

         print("Erreur : Secret de l'application introuvable !")
         return None

    while True:

        try:

            connection = connector.connect(
            host=os.getenv('DB_HOST', 'mysql'),
            user=os.getenv('DB_USER', 'jean'), 
            password=db_pwd, 
            database=os.getenv('DB_NAME', 'hoteldatabase')
            )
            print("connect as 'jean' ! ")

            return connection
        
        except connector.Error as err:
            print(f"⏳ Attente de MySQL ({err})...")
            time.sleep(5)

con = get_db_con()
cur = con.cursor()


def createTables():
    queries = [
        "create table if not exists customerdetails(cid int primary key,aadhar char(20), cname char(50), cage int, phone char(20), caddress char(100), finalprice float, checkin date,checkout date)",
        "create table if not exists room(roomnum int primary key,roomtypeid int, size int)",
        "create table if not exists roomtype(roomtypeid int primary key,bednum int, ac char(10), rate float, description char(200))",
        "create table if not exists roomservice(orderid int primary key,itemid int, quantity int, rscid int)",
        "create table if not exists items(itemid int primary key,itemname char(20), rate float)",
        "create table if not exists bookingdetails(bid int primary key,cid int, checkin date, checkout date, finalprice float)",
        "create table if not exists employees(empid int primary key, aadhar char(20), ename char(50), age int, gender char(10), roleid int, sal float)",
        "create table if not exists roles(roleid int primary key, rolename char(50),sal float)"]
    for query in queries:
        cur.execute(query)
        print("OK ", query)



def addDefaultValues():
    queries = [
        "insert into customerdetails values(115,'669524138972','Rohit M S',20,'9358432100','#41, 1st Main, Marathahalli, Bangalore',1500,'2022-11-12','2022-11-13')",
        "insert into roles values(11,'Manager',95000)",
        "insert into employees values(31,'668574239817','Samuel Johnson',32,'Male',11,95000)",
        "insert into items values(1,'Chocolate Ice Cream',150)",
        "insert into roomtype values(1,2,'AC',2500,'Comfortable double room with AC, two single beds, a wardrobe and an outward facing window')",
        "insert into room values(188,1,268)",
        "insert into roomservice values(1768,1,3,115)",
        "insert into bookingdetails values(1327,115,'2022-11-12','2022-11-13',1950)"]
    for query in queries:
        cur.execute(query)
        con.commit()
        print("OK ", query)


def addForeignKeys():
    queries = [
        "alter table room add foreign key(roomtypeid) references roomtype(roomtypeid) on update cascade on delete cascade",
        "alter table roomservice add foreign key(itemid) references items(itemid) on update cascade on delete cascade",
        "alter table bookingdetails add foreign key(cid) references customerdetails(cid) on update cascade on delete cascade",
        "alter table employees add foreign key(roleid) references roles(roleid) on update cascade on delete cascade",
        "alter table roomservice add foreign key(rscid) references customerdetails(cid)"]
    for query in queries:
        cur.execute(query)
        con.commit()
        print("OK ", query)


def addCustDetails(aadhar, cname, cage, phone, caddress, finalprice, checkin, checkout):
    # Partie ID (on simplifie avec fetchone)
    cur.execute('select cid from customerdetails order by cid desc limit 1')
    row = cur.fetchone()
    cid = (int(row[0]) + 10) if row else 10

    # INSERTION SÉCURISÉE
    # 1. On utilise des %s comme placeholders
    sql = "INSERT INTO customerdetails VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
    # 2. On regroupe les variables dans un tuple
    values = (cid, aadhar, cname, cage, phone, caddress, finalprice, checkin, checkout)

    # 3. Le connecteur fait le travail de sécurité
    cur.execute(sql, values)
    con.commit()
    
    return cid



def addEmployeeDetails(empid, aadhar, ename, age, gender, roleid):
    # 1. Récupération sécurisée du salaire
    query_sal = 'SELECT sal FROM roles WHERE roleid = %s'
    cur.execute(query_sal, (roleid,)) # On passe roleid dans un tuple
    row = cur.fetchone()
    
    if row:
        sal = float(row[0])
    else:
        print("Erreur : Role ID inexistant")
        return

    # 2. Insertion sécurisée de l'employé
    query_insert = "INSERT INTO employees VALUES (%s, %s, %s, %s, %s, %s, %s)"
    data = (empid, aadhar, ename, age, gender, roleid, sal)
    
    cur.execute(query_insert, data) # Le connecteur nettoie toutes les variables ici
    con.commit()



def addItem(itemid, itemname, itemrate):
    # 1. On définit la structure avec des %s
    sql = "INSERT INTO items VALUES (%s, %s, %s)"
    
    # 2. On regroupe les données dans un tuple
    val = (itemid, itemname, itemrate)
    
    # 3. On laisse le connecteur gérer la sécurité
    cur.execute(sql, val)
    con.commit()


def addRole(roleid, rolename, rolesal):
    # La structure de la requête avec des placeholders %s
    sql = "INSERT INTO roles VALUES (%s, %s, %s)"
    
    # Les données isolées dans un tuple
    val = (roleid, rolename, rolesal)
    
    # Exécution sécurisée : le driver s'occupe de l'échappement
    cur.execute(sql, val)
    con.commit()



def addRoomType(roomtypeid, bednum, ac, roomrate, desc):
    # Placeholders %s pour chaque valeur
    sql = "INSERT INTO roomtype VALUES (%s, %s, %s, %s, %s)"
    
    # Regroupement des données dans un tuple
    val = (roomtypeid, bednum, ac, roomrate, desc)
    
    # Exécution sécurisée
    cur.execute(sql, val)
    con.commit()



def addRoomService(itemid, quantity, rscid):
    # 1. Récupération du dernier orderid (plus propre avec fetchone)
    cur.execute('SELECT orderid FROM roomservice ORDER BY orderid DESC LIMIT 1')
    row = cur.fetchone()
    orderid = (int(row[0]) + 10) if row else 10

    # 2. Insertion sécurisée
    sql = "INSERT INTO roomservice VALUES (%s, %s, %s, %s)"
    val = (orderid, itemid, quantity, rscid)
    
    cur.execute(sql, val)
    con.commit()



def addRoom(roomnum, roomid, size):
    # Utilisation des placeholders %s
    sql = "INSERT INTO room VALUES (%s, %s, %s)"
    
    # Les données sont transmises séparément dans un tuple
    val = (roomnum, roomid, size)
    
    cur.execute(sql, val)
    con.commit()



def addBookingDetails(cid, totalamt):
    # 1. Récupérer le dernier ID de réservation (Sûr - statique)
    cur.execute('SELECT bid FROM bookingdetails ORDER BY bid DESC LIMIT 1')
    row = cur.fetchone()
    bid = (int(row[0]) + 10) if row else 10

    # 2. Récupérer les dates en UNE SEULE fois de manière SÉCURISÉE
    # On utilise %s pour le CID
    query_dates = 'SELECT checkin, checkout FROM customerdetails WHERE cid = %s'
    cur.execute(query_dates, (cid,))
    result = cur.fetchone()

    if result:
        checkin, checkout = result
    else:
        print("Erreur : Client introuvable")
        return

    # 3. Insertion finale SÉCURISÉE
    sql_insert = "INSERT INTO bookingdetails VALUES (%s, %s, %s, %s, %s)"
    data = (bid, cid, checkin, checkout, totalamt)
    
    cur.execute(sql_insert, data)
    con.commit()



def getFinalAmount(cid):
    # 1. Récupération sécurisée du prix de base
    query1 = "SELECT finalprice FROM customerdetails WHERE cid = %s"
    cur.execute(query1, (cid,))
    row1 = cur.fetchone()
    p1 = float(row1[0]) if row1 else 0.0

    # 2. Calcul sécurisé du total roomservice
    query2 = """SELECT SUM(items.rate * roomservice.quantity) 
                FROM roomservice 
                JOIN items ON roomservice.itemid = items.itemid 
                WHERE roomservice.rscid = %s"""
    cur.execute(query2, (cid,))
    row2 = cur.fetchone()
    
    # Gestion du cas où il n'y a pas de service de chambre (SUM renvoie None)
    p2 = float(row2[0]) if row2 and row2[0] is not None else 0.0
    
    return p1 + p2



def getRoomType(roomtypeid):
    # Utilisation du placeholder %s
    query = 'SELECT * FROM roomtype WHERE roomtypeid = %s'
    
    # Passage de la variable dans un tuple
    cur.execute(query, (roomtypeid,))
    
    # fetchone() est idéal ici car l'ID est unique (Primary Key)
    return cur.fetchone()



def selectRoom(roomtypeid, checkin, checkout):
    # 1. Requête paramétrée avec %s
    query = 'SELECT rate FROM roomtype WHERE roomtypeid = %s'
    cur.execute(query, (roomtypeid,))
    row = cur.fetchone()
    
    # 2. Vérification si la chambre existe
    if row:
        rate = int(row[0])
    else:
        print("Erreur : Type de chambre introuvable")
        return 0
    
    # 3. Calcul de la durée
    delta = checkout - checkin
    totalprice = rate * delta.days
    
    return totalprice



def getCustDetails(cid):
    # Requête paramétrée
    query = 'SELECT * FROM customerdetails WHERE cid = %s'
    
    # On passe le CID dans un tuple
    cur.execute(query, (cid,))
    
    # fetchone() est parfait ici car le CID est unique
    return cur.fetchone()



def getAllItems():
    query = pd.read_sql_query('select * from items', con)
    df = pd.DataFrame(query, columns=['itemid', 'itemname', 'rate'])
    return df


def getAllRoles():
    query = pd.read_sql_query('select * from roles', con)
    df = pd.DataFrame(query, columns=['roleid', 'rolename', 'sal'])
    return df


def getAllEmployees():
    query = pd.read_sql_query('select * from employees', con)
    df = pd.DataFrame(query, columns=['empid', 'ename', 'aadhar', 'age', 'gender', 'roleid', 'sal'])
    return df


def getAllRooms():
    query = pd.read_sql_query('select * from room', con)
    df = pd.DataFrame(query, columns=['roomnum', 'roomtypeid', 'size'])
    return df


def getAllRoomTypes():
    query = pd.read_sql_query('select * from roomtype', con)
    df = pd.DataFrame(query, columns=['roomtypeid', 'bednum', 'ac', 'rate', 'description'])
    return df


def getAllBookingDetails():
    query = pd.read_sql_query('select * from bookingdetails', con)
    df = pd.DataFrame(query, columns=['bid', 'cid', 'checkin', 'checkout', 'finalprice'])
    return df


def getAllCustomerDetails():
    query = pd.read_sql_query('select * from customerdetails', con)
    df = pd.DataFrame(query, columns=['cid', 'aadhar', 'cname', 'cage', 'phone', 'caddress', 'finalprice', 'checkin',
                                      'checkout'])
    return df


def getAllOrders():
    query = pd.read_sql_query('select * from roomservice', con)
    df = pd.DataFrame(query, columns=['orderid', 'itemid', 'quantity', 'rscid'])
    return df



### Réglage pour les injonctions sql --- fetch info
### code test pour déployer l'application avec docker