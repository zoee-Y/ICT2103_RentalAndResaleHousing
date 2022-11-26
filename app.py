import pandas.core.groupby.groupby
from flask import Flask, render_template, url_for, redirect, request, session, jsonify
from flask_navigation import Navigation
import pandas as pd
import pymongo
from pymongo import MongoClient
import json
import plotly
import plotly.express as px
import os

app = Flask(__name__)
nav = Navigation(app)
app.secret_key = os.urandom(32)

nav.Bar('top', [
    nav.Item('Home', 'Home'),
    nav.Item('Rental', 'GRental'),
    nav.Item('Resale', 'Resaleindex'),
    #add more if needed
    # added login but cant make login href link to register
    nav.Item('Login', 'Login'),
    nav.Item('Register', 'Register'),
])

client = MongoClient('localhost', 27017)

db = client.rnrhousing

# def setUpTablesAndData():
#     try:
#         #create user table
#         cur.execute('''CREATE TABLE IF NOT EXISTS
#             user(
#             user_id int NOT NULL PRIMARY KEY AUTO_INCREMENT,
#             username varchar(50) NOT NULL,
#             password varchar(50) NOT NULL,
#             name varchar(100) NOT NULL
#             );
#         ''')
#
#         #create housetype table
#         cur.execute('''CREATE TABLE IF NOT EXISTS
#             housetype(
#             house_type_id int NOT NULL PRIMARY KEY AUTO_INCREMENT,
#             house_type varchar(50) NOT NULL,
#             number_of_rooms int NOT NULL
#         );
#         ''')
#
#         #create preference table
#         #foreign keys to user and housetype IDs
#         cur.execute('''CREATE TABLE IF NOT EXISTS
#             preference(
#             preference_id int NOT NULL PRIMARY KEY AUTO_INCREMENT,
#             user_id int NOT NULL,
#             house_type_id int NOT NULL,
#             district_code int NOT NULL,
#             town varchar(50) NOT NULL,
#             FOREIGN KEY (user_id) REFERENCES user(user_id),
#             FOREIGN KEY (house_type_id) REFERENCES housetype(house_type_id)
#             );
#         ''')
#
#         #create rent table
#         #foreign key to housetypeID
#         cur.execute('''CREATE TABLE IF NOT EXISTS
#             rent(
#             rent_id int NOT NULL PRIMARY KEY AUTO_INCREMENT,
#             house_type_id int NOT NULL,
#             rental_fees int NOT NULL,
#             postal_district int NOT NULL,
#             floor_area varchar(50) NOT NULL,
#             year_of_lease int NOT NULL,
#             month_of_lease varchar(50) NOT NULL,
#             FOREIGN KEY (house_type_id) REFERENCES housetype(house_type_id)
#             );
#         ''')
#
#         #create resale table
#         #foreign key to housetypeID
#         cur.execute('''CREATE TABLE IF NOT EXISTS
#             resale(
#             sell_id int NOT NULL PRIMARY KEY AUTO_INCREMENT,
#             house_type_id int NOT NULL,
#             resale_price int NOT NULL,
#             town varchar(50) NOT NULL,
#             remaining_lease varchar(50) NOT NULL,
#             floor_area int NOT NULL,
#             FOREIGN KEY (house_type_id) REFERENCES HouseType(house_type_id)
#         );
#         ''')
#
#         #insert data into housetype:
#         #rent rooms: 1,2,3,4,5,6,8
#         #resale rooms: 1,2,3,4,5
#
#         #check if table is empty
#         cur.execute("SELECT 1 FROM housetype;")
#         if cur.rowcount == 0:
#             cur.execute('''INSERT INTO housetype(house_type_id, house_type, number_of_rooms)
#                 VALUES(1, 'Rent', 1), (2, 'Rent', 2),(3, 'Rent',3), (4, 'Rent', 4), (5, 'Rent', 5), (6, 'Rent', 6), (7, 'Rent', 8),
#                 (8, 'Resale', 1), (9, 'Resale', 2), (10, 'Resale', 3), (11, 'Resale', 4), (12, 'Resale', 5);
#             ''')
#             conn.commit()
#             print("Added data into housetype table")
#         else:
#             print("housetype table has already been populated")
#
#         #create default user001 godbless mes
#         cur.execute("SELECT 1 FROM user;")
#         if cur.rowcount == 0:
#             cur.execute('''INSERT INTO user(user_id, username, password, name)
#                         VALUES(001, 'user001', 'pass123', 'default user');
#             ''')
#             conn.commit()
#             print("Added user001 into user table")
#         else:
#             print("user table has already been populated")
#
#     except mariadb.Error as e:
#         print("Error during setup: ", {e})
#         print("SQL statement: ", cur.statement)
#

# def insertRentDataFromCSV():
#     try:
#         data = pd.read_csv("./rental data.csv")
#         df = pd.DataFrame(data)
#         print("Adding rent data")
#
#         cur.execute("SELECT 1 FROM rent;")
#         if cur.rowcount == 0:
#             for row in df.itertuples():
#                 try:
#                     cur.execute('''
#                         INSERT INTO rent(
#                         house_type_id,
#                         rental_fees,
#                         postal_district,
#                         floor_area,
#                         year_of_lease,
#                         month_of_lease)
#
#                         SELECT house_type_id, ''' + str(row.monthly_gross_rent) + ", " + str(
#                         row.postal_district) + ", '" + row.floor_area + "', " + str(
#                         row.lease_commencement_year) + ", '" + row.lease_commencement_month + "' "
#                         + ''' FROM housetype
#                         WHERE house_type = 'Rent' AND number_of_rooms = ''' + str(row.no_of_bedroom))
#                 except mariadb.Error as e:
#                     #print(cur.statement)
#                     print("Error inserting Rent data: ", {e})
#         else:
#             print("Data already exists in Rent table")
#     except pandas.core.groupby.groupby.DataError as pe:
#         print("Error in Pandas: ", {pe})
#     else: #if no exception then commit
#         conn.commit()
#         print("InsertRentData ran successfully")
#
#
# def insertResaleDataFromCSV():
#     try:
#         data = pd.read_csv("./resale data.csv")
#         df = pd.DataFrame(data)
#         print("Adding resale data")
#
#         cur.execute("SELECT 1 FROM resale;")
#         if cur.rowcount == 0:
#             for row in df.itertuples():
#                 try:
#                     cur.execute('''
#                         INSERT INTO resale(
#                         house_type_id,
#                         resale_price,
#                         town,
#                         remaining_lease,
#                         floor_area)
#
#                         SELECT house_type_id, ''' + str(
#                         row.resale_price) + ", '" + row.town + "' , '" + row.remaining_lease + "', " + str(
#                         row.floor_area) + ''' FROM housetype
#                         WHERE house_type = 'Resale' AND number_of_rooms = ''' + row.flat_type[0])
#                 except mariadb.Error as e:
#                     #print(cur.statement)
#                     print("Error inserting Resale data: ", {e})
#         else:
#             print("Data already exists in Resale table")
#     except pandas.core.groupby.groupby.DataError as pe:
#         print("Error in Pandas: ", {pe})
#     else: # if no exception then commit
#         conn.commit()
#         print("InsertResaleData ran successfully")
#
#
# def displayResaleData():
#     try:
#         cur.execute("SELECT COUNT(*) FROM resale")
#
#         s = "<table style='border:1px solid red; border-collapse: collapse;'>"
#         s = s + '''<tr style='border-bottom: 1px solid black'>
#         <td style='padding: 10px; border-right: 1px solid blue'>sellID</td>
#         <td style='padding: 10px; border-right: 1px solid blue'>houseTypeID</td>
#         <td style='padding: 10px; border-right: 1px solid blue'>resale price</td>
#         <td style='padding: 10px; border-right: 1px solid blue'>town</td>
#         <td style='padding: 10px; border-right: 1px solid blue'>remaining lease</td>
#         <td style='padding: 10px; border-right: 1px solid blue'>floor area (sqm)</td>
#         '''
#         for row in cur:
#             s = s + "<tr style='border-bottom: 1px solid black'>"
#             for x in row:
#                 s = s + "<td style='padding: 10px; border-right: 1px solid blue'>" + str(x) + "</td>"
#             s = s + "</tr>"
#         s = s + "</table>"
#
#         return s
#
#     except mariadb.Error as e:
#         print("Error displaying Resale data: ", {e})
#         return "<html><body>Error displaying data!</body></html>"
#
#
# def displayRentData():
#     try:
#         cur.execute("SELECT COUNT(*) FROM rent")
#
#         s = "<table style='border:1px solid red; border-collapse: collapse;'>"
#         s = s + '''<tr style='border-bottom: 1px solid black'>
#             <td style='padding: 10px; border-right: 1px solid blue'>rentID</td>
#             <td style='padding: 10px; border-right: 1px solid blue'>houseTypeID</td>
#             <td style='padding: 10px; border-right: 1px solid blue'>rental fees (monthly)</td>
#             <td style='padding: 10px; border-right: 1px solid blue'>postal district</td>
#             <td style='padding: 10px; border-right: 1px solid blue'>floor area (sqm)</td>
#             '''
#         for row in cur:
#             s = s + "<tr style='border-bottom: 1px solid black'>"
#             for x in row:
#                 s = s + "<td style='padding: 10px; border-right: 1px solid blue'>" + str(x) + "</td>"
#             s = s + "</tr>"
#         s = s + "</table>"
#
#         return s
#
#     except mariadb.Error as e:
#         print("Error displaying Rent data: ", {e})
#         return "<html><body>Error displaying data!</body></html>"
#
#
#
# def testDisplayData():
#     try:
#         cur.execute("SELECT r.rental_fees, r.postal_district, h.number_of_rooms, r.floor_area FROM rent as r, housetype as h WHERE r.house_type_id = h.house_type_id")
#         s = "<table style='border:1px solid red; border-collapse: collapse;'>"
#         s = s + '''<tr style='border-bottom: 1px solid black'>
#             <td style='padding: 10px; border-right: 1px solid blue'>Resale price/Resale</td>
#             <td style='padding: 10px; border-right: 1px solid blue'>sellID</td>
#             <td style='padding: 10px; border-right: 1px solid blue'>Town</td>
#             <td style='padding: 10px; border-right: 1px solid blue'>No. of rooms</td>
#             <td style='padding: 10px; border-right: 1px solid blue'>Floor area (sqm)</td>
#             <td style='padding: 10px; border-right: 1px solid blue'>Remaining lease</td>
#             '''
#
#         for row in cur:
#             s = s + "<tr style='border-bottom: 1px solid black'>"
#             for x in row:
#                 s = s + "<td style='padding: 10px; border-right: 1px solid blue'>" + str(x) + "</td>"
#             s = s + "</tr>"
#         s = s + "</table>"
#         rv = cur.fetchall()
#         print(rv)
#
#         return s
#     except mariadb.Error as e:
#         print("Error displaying test data: ", {e})
#         return "<html><body>Error displaying test data!</body></html>"

def insertRentDataFromCSV():
    try:
        data = pd.read_csv("./rental data.csv")
        df = pd.DataFrame(data)
        records = df.to_dict(orient="records")
        print("Adding rent data")

        if db.rent.count_documents({}) == 0:
            db.rent.insert_many(records)
        else:
            print("Data already exists in Rent collection")

    except pandas.core.groupby.groupby.DataError as pe:
        print("Error in Pandas: ", {pe})
    else:
        print("InsertRentData ran successfully")


def insertResaleDataFromCSV():
    try:
        data = pd.read_csv("./resale data.csv")
        df = pd.DataFrame(data)
        records = df.to_dict(orient="records")
        print("Adding resale data")

        if db.resale.count_documents({}) == 0:
            db.resale.insert_many(records)
        else:
            print("Data already exists in Resale collection")

    except pandas.core.groupby.groupby.DataError as pe:
        print("Error in Pandas: ", {pe})
    else:
        print("InsertResaleData ran successfully")

def displayRentData():
    s = "<table style='border:1px solid red; border-collapse: collapse;'>"
    s = s + '''<tr style='border-bottom: 1px solid black'>
                        <td style='padding: 10px; border-right: 1px solid blue'>floor area (sqm)</td>
                        <td style='padding: 10px; border-right: 1px solid blue'>no of bedroom</td>
                        <td style='padding: 10px; border-right: 1px solid blue'>rental fees (monthly)</td>
                        <td style='padding: 10px; border-right: 1px solid blue'>postal district</td>
                        <td style='padding: 10px; border-right: 1px solid blue'>lease commencement year</td>
                        <td style='padding: 10px; border-right: 1px solid blue'>lease commencement month</td></tr>
                        '''

    #test display those with lease commencement year 2021 AND june
    for doc in db.rent.find({"lease_commencement_year": 2021, "lease_commencement_month": "Jun"}):
        s = s + "<tr style='border-bottom: 1px solid black'>"
        for row in doc:
            if str(row) != "_id": #dont print object id
                s = s + "<td style='padding: 10px; border-right: 1px solid blue'>" + str(doc[str(row)]) + "</td>"
        s = s + "</tr>"

    s = s + "</table>"

    return s

def displayResaleData():
    s = "<table style='border:1px solid red; border-collapse: collapse;'>"
    s = s + '''<tr style='border-bottom: 1px solid black'>
                            <td style='padding: 10px; border-right: 1px solid blue'>resale price</td>
                            <td style='padding: 10px; border-right: 1px solid blue'>town</td>
                            <td style='padding: 10px; border-right: 1px solid blue'>remaining lease</td>
                            <td style='padding: 10px; border-right: 1px solid blue'>room type</td>
                            <td style='padding: 10px; border-right: 1px solid blue'>floor area (sqm)</td></tr>
                            '''

    # test display those with resale price less than 168000 and flat type 1 room or 3 room
    for doc in db.resale.find({"resale_price": {"$lt": 168000}, "flat_type": {"$in": ["1 ROOM", "3 ROOM"]}}):
        s = s + "<tr style='border-bottom: 1px solid black'>"
        for row in doc:
            if str(row) != "_id":  # dont print object id
                s = s + "<td style='padding: 10px; border-right: 1px solid blue'>" + str(doc[str(row)]) + "</td>"
        s = s + "</tr>"

    s = s + "</table>"

    return s

# uncomment if u wanna add to database and see if records are added
@app.route("/")
def index():

    insertRentDataFromCSV()     # uncomment these two lines if you want to insert data
    insertResaleDataFromCSV()

    #resale: test display those with resale price less than 168000 and flat type 1 room or 3 room
    #rent:test display those with lease commencement year 2021 AND june
    return "<html><body>" + displayResaleData() + displayRentData() + "</html></body>"



# TestLogin
# @app.route('/')
# def index():
#     return render_template("Login.html")
# @app.route('/Register')
# def new_user():
#     return render_template("Register.html")
# @app.route('/Home')
# def home():
#     return render_template("Home.html")



if __name__ == "__main__":
    app.run(debug=True)
