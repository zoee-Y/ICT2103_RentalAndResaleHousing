import pandas.core.groupby.groupby
from flask import Flask, render_template, url_for, redirect, request, session, jsonify, flash
from flask_navigation import Navigation
import mariadb
import sys
import pandas as pd
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
    nav.Item('Login', 'Login'),
    nav.Item('Register', 'Register'),
    nav.Item('Log out', 'Logout')
])

try:
    with open("dbconnection.txt", "r") as f:
        conn = mariadb.connect(
                 host=f.readline().strip(),
                 port=int(f.readline().strip()),
                 user=f.readline().strip(),
                 password=f.readline().strip(),
                 database=f.readline().strip())
except mariadb.Error as e:
    print(f"An error occurred while connecting to MariaDB: ", {e})
    sys.exit(1)

cur = conn.cursor()

def setUpTablesAndData():
    try:
        #create user table
        cur.execute('''CREATE TABLE IF NOT EXISTS
            user(
            user_id int NOT NULL PRIMARY KEY AUTO_INCREMENT,
            username varchar(50) NOT NULL,
            password varchar(50) NOT NULL,
            name varchar(100) NOT NULL
            );
        ''')

        #create housetype table
        cur.execute('''CREATE TABLE IF NOT EXISTS
            housetype(
            house_type_id int NOT NULL PRIMARY KEY AUTO_INCREMENT,
            house_type varchar(50) NOT NULL,
            number_of_rooms int NOT NULL
        );
        ''')

        #create preference table
        #foreign keys to user and housetype IDs
        cur.execute('''CREATE TABLE IF NOT EXISTS
            preference(
            preference_id int NOT NULL PRIMARY KEY AUTO_INCREMENT,
            user_id int NOT NULL,
            house_type_id int NOT NULL,
            district_code int NOT NULL,
            town varchar(50) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user(user_id),
            FOREIGN KEY (house_type_id) REFERENCES housetype(house_type_id)
            );
        ''')

        #create rent table
        #foreign key to housetypeID
        cur.execute('''CREATE TABLE IF NOT EXISTS
            rent(
            rent_id int NOT NULL PRIMARY KEY AUTO_INCREMENT,
            house_type_id int NOT NULL,
            rental_fees int NOT NULL,
            postal_district int NOT NULL,
            floor_area varchar(50) NOT NULL,
            year_of_lease int NOT NULL,
            month_of_lease varchar(50) NOT NULL,
            FOREIGN KEY (house_type_id) REFERENCES housetype(house_type_id)
            );
        ''')

        #create resale table
        #foreign key to housetypeID
        cur.execute('''CREATE TABLE IF NOT EXISTS
            resale(
            sell_id int NOT NULL PRIMARY KEY AUTO_INCREMENT,
            house_type_id int NOT NULL,
            resale_price int NOT NULL,
            town varchar(50) NOT NULL,
            remaining_lease varchar(50) NOT NULL,
            floor_area int NOT NULL,
            FOREIGN KEY (house_type_id) REFERENCES HouseType(house_type_id)
        );
        ''')

        #insert data into housetype:
        #rent rooms: 1,2,3,4,5,6,8
        #resale rooms: 1,2,3,4,5

        #check if table is empty
        cur.execute("SELECT 1 FROM housetype;")
        if cur.rowcount == 0:
            cur.execute('''INSERT INTO housetype(house_type_id, house_type, number_of_rooms)
                VALUES(1, 'Rent', 1), (2, 'Rent', 2),(3, 'Rent',3), (4, 'Rent', 4), (5, 'Rent', 5), (6, 'Rent', 6), (7, 'Rent', 8),
                (8, 'Resale', 1), (9, 'Resale', 2), (10, 'Resale', 3), (11, 'Resale', 4), (12, 'Resale', 5);
            ''')
            conn.commit()
            print("Added data into housetype table")
        else:
            print("housetype table has already been populated")

        #create default user001 godbless mes
        cur.execute("SELECT 1 FROM user;")
        if cur.rowcount == 0:
            cur.execute('''INSERT INTO user(user_id, username, password, name)
                        VALUES(001, 'user001', 'pass123', 'default user');
            ''')
            conn.commit()
            print("Added user001 into user table")
        else:
            print("user table has already been populated")

    except mariadb.Error as e:
        print("Error during setup: ", {e})
        print("SQL statement: ", cur.statement)


def insertRentDataFromCSV():
    try:
        data = pd.read_csv("./rental data.csv")
        df = pd.DataFrame(data)
        print("Adding rent data")

        datalist = []

        cur.execute("SELECT 1 FROM rent;")
        if cur.rowcount == 0:
            try:
                for row in df.itertuples():

                    cur.execute('''SELECT house_type_id, ''' + str(row.monthly_gross_rent) + ", " + str(
                        row.postal_district) + ", '" + row.floor_area + "', " + str(
                        row.lease_commencement_year) + ", '" + row.lease_commencement_month + "' "
                                + ''' FROM housetype
                                WHERE house_type = 'Rent' AND number_of_rooms = ''' + str(row.no_of_bedroom))
                    result = cur.fetchall()
                    for r in result:
                        datalist.append(r)

                cur.executemany('''
                    INSERT INTO rent(
                    house_type_id,
                    rental_fees,
                    postal_district,
                    floor_area,
                    year_of_lease,
                    month_of_lease)

                    VALUES(?, ?, ?, ?, ?, ?)''', datalist)
            except mariadb.Error as e:
                #print(cur.statement)
                print("Error inserting Rent data: ", {e})
        else:
            print("Data already exists in Rent table")
    except pandas.core.groupby.groupby.DataError as pe:
        print("Error in Pandas: ", {pe})
    else: #if no exception then commit
        conn.commit()
        print("InsertRentData ran successfully")


def insertResaleDataFromCSV():
    try:
        data = pd.read_csv("./resale data.csv")
        df = pd.DataFrame(data)
        print("Adding resale data")

        datalist = []

        cur.execute("SELECT 1 FROM resale;")
        if cur.rowcount == 0:
            try:
                for row in df.itertuples():
                    cur.execute('''SELECT house_type_id, ''' + str(
                            row.resale_price) + ", '" + row.town + "' , '" + row.remaining_lease + "', " + str(
                            row.floor_area) + ''' FROM housetype
                            WHERE house_type = 'Resale' AND number_of_rooms = ''' + row.flat_type[0])
                    result = cur.fetchall()
                    for r in result:
                        datalist.append(r)

                cur.executemany('''
                    INSERT INTO resale(
                    house_type_id,
                    resale_price,
                    town,
                    remaining_lease,
                    floor_area)

                    VALUES(?,?,?,?,?)''', datalist)
            except mariadb.Error as e:
                #print(cur.statement)
                print("Error inserting Resale data: ", {e})
        else:
            print("Data already exists in Resale table")
    except pandas.core.groupby.groupby.DataError as pe:
        print("Error in Pandas: ", {pe})
    else: # if no exception then commit
        conn.commit()
        print("InsertResaleData ran successfully")

#set up database
setUpTablesAndData()
insertRentDataFromCSV()
insertResaleDataFromCSV()

def displayResaleData():
    try:
        cur.execute("SELECT COUNT(*) FROM resale")

        s = "<table style='border:1px solid red; border-collapse: collapse;'>"
        s = s + '''<tr style='border-bottom: 1px solid black'>
        <td style='padding: 10px; border-right: 1px solid blue'>sellID</td>
        <td style='padding: 10px; border-right: 1px solid blue'>houseTypeID</td>
        <td style='padding: 10px; border-right: 1px solid blue'>resale price</td>
        <td style='padding: 10px; border-right: 1px solid blue'>town</td>
        <td style='padding: 10px; border-right: 1px solid blue'>remaining lease</td>
        <td style='padding: 10px; border-right: 1px solid blue'>floor area (sqm)</td>
        '''
        for row in cur:
            s = s + "<tr style='border-bottom: 1px solid black'>"
            for x in row:
                s = s + "<td style='padding: 10px; border-right: 1px solid blue'>" + str(x) + "</td>"
            s = s + "</tr>"
        s = s + "</table>"

        return s

    except mariadb.Error as e:
        print("Error displaying Resale data: ", {e})
        return "<html><body>Error displaying data!</body></html>"


def displayRentData():
    try:
        cur.execute("SELECT COUNT(*) FROM rent")

        s = "<table style='border:1px solid red; border-collapse: collapse;'>"
        s = s + '''<tr style='border-bottom: 1px solid black'>
            <td style='padding: 10px; border-right: 1px solid blue'>rentID</td>
            <td style='padding: 10px; border-right: 1px solid blue'>houseTypeID</td>
            <td style='padding: 10px; border-right: 1px solid blue'>rental fees (monthly)</td>
            <td style='padding: 10px; border-right: 1px solid blue'>postal district</td>
            <td style='padding: 10px; border-right: 1px solid blue'>floor area (sqm)</td>
            '''
        for row in cur:
            s = s + "<tr style='border-bottom: 1px solid black'>"
            for x in row:
                s = s + "<td style='padding: 10px; border-right: 1px solid blue'>" + str(x) + "</td>"
            s = s + "</tr>"
        s = s + "</table>"

        return s

    except mariadb.Error as e:
        print("Error displaying Rent data: ", {e})
        return "<html><body>Error displaying data!</body></html>"



def testDisplayData():
    try:
        cur.execute("SELECT r.rental_fees, r.postal_district, h.number_of_rooms, r.floor_area FROM rent as r, housetype as h WHERE r.house_type_id = h.house_type_id")
        s = "<table style='border:1px solid red; border-collapse: collapse;'>"
        s = s + '''<tr style='border-bottom: 1px solid black'>
            <td style='padding: 10px; border-right: 1px solid blue'>Resale price/Resale</td>
            <td style='padding: 10px; border-right: 1px solid blue'>sellID</td>
            <td style='padding: 10px; border-right: 1px solid blue'>Town</td>
            <td style='padding: 10px; border-right: 1px solid blue'>No. of rooms</td>
            <td style='padding: 10px; border-right: 1px solid blue'>Floor area (sqm)</td>
            <td style='padding: 10px; border-right: 1px solid blue'>Remaining lease</td>
            '''

        for row in cur:
            s = s + "<tr style='border-bottom: 1px solid black'>"
            for x in row:
                s = s + "<td style='padding: 10px; border-right: 1px solid blue'>" + str(x) + "</td>"
            s = s + "</tr>"
        s = s + "</table>"
        rv = cur.fetchall()
        print(rv)

        return s
    except mariadb.Error as e:
        print("Error displaying test data: ", {e})
        return "<html><body>Error displaying test data!</body></html>"

# uncomment if u wanna add to database and see if records are added
#@app.route("/")
def index():
    setUpTablesAndData()

    insertRentDataFromCSV() #uncomment these two lines if you want to insert data
    insertResaleDataFromCSV()

    #testDisplayData()

    return "<html><body>" + displayRentData() + displayResaleData() + "</html></body>"

@app.route('/AveragePriceResale')
def GResale():
    cur.execute("select town, avg(resale_price) from resale GROUP BY town;")
    grouped = cur.fetchall()
    town = []
    resalePrice = []
    for x in grouped:
        town.append(x[0])
        resalePrice.append(x[1])
    df = pd.DataFrame(list(zip(town, resalePrice)), columns=['town', 'resale_price'])

    fig = px.bar(df, x="town", y="resale_price", color='town', barmode="group")

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header = "Resale Graph "
    description = """
    A graph showing the average price comparison between the different areas.
    """
    return render_template('AveragePriceResale.html', graphJSON=graphJSON, header=header, description=description)


@app.route('/TotalResale')
def GResale2():
    cur.execute("  select distinct town,  COUNT(*) AS counts FROM resale group by town HAVING (COUNT(*)>1);")
    grouped = cur.fetchall()
    town = []
    counts = []
    for x in grouped:
        town.append(x[0])
        counts.append(x[1])
    df = pd.DataFrame(list(zip(town, counts)), columns=['town', 'counts'])
    fig = px.bar(df, x="town", y="counts", color='town', barmode="group")

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header = "Resale Graph 2"
    description = """
    A graph showing the highest resale comparison between the different areas.
    """
    return render_template('TotalResale.html', graphJSON=graphJSON, header=header, description=description)

@app.route('/Rental')
def GRental():
    cur.execute("select avg(rental_fees),year_of_lease from rent GROUP BY year_of_lease;")
    avgRentalFees1 = []
    year = []
    AvgRentalOverTime = cur.fetchall()
    for x in AvgRentalOverTime:
        avgRentalFees1.append(x[0])
        year.append(x[1])
    AvgRentalOverTimeDF = pd.DataFrame(list(zip(avgRentalFees1, year)), columns=['Average_Rental_Fees', 'year'])
    fig1 = px.line(AvgRentalOverTimeDF, x="year", y="Average_Rental_Fees", title='Average Rental Price Over Years')
    graphJSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    description1 = """
    A graph showing the increase of rental prices over the years.
    """

    cur.execute("select postal_district, avg(rental_fees) as average_rental_fees from rent Group By(postal_district) order by average_rental_fees  ;")
    AvgRentalByPostalDistrict = cur.fetchall()
    avgRentalFees2 = []
    postalDistrict = []
    for x in AvgRentalByPostalDistrict:
        avgRentalFees2.append(x[1])
        postalDistrict.append(str(x[0]))
    AvgRentalByPostalDistrictDF = pd.DataFrame(list(zip(avgRentalFees2, postalDistrict)), columns=['Average_Rental_Fees', 'postal_district'])
    fig2 = px.bar(AvgRentalByPostalDistrictDF, x="postal_district", y="Average_Rental_Fees", title=' Average Rental Price by Postal District')
    graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    description2 = """
    A graph showing the average price comparison between the different areas.
    """

    cur.execute("select avg(r.rental_fees), h.number_of_rooms from rent as r inner join  housetype as h on h.house_type_id = r.house_type_id group by h.number_of_rooms;")
    ResalePriceNoRooms = cur.fetchall()
    print(ResalePriceNoRooms)
    avgRentalFees3 = []
    noOfRooms = []
    for x in ResalePriceNoRooms:
        avgRentalFees3.append(x[0])
        noOfRooms.append(str(x[1]))
    AvgRentalByRoomDF = pd.DataFrame(list(zip(avgRentalFees3, noOfRooms)), columns=['Average_Rental_Fees', 'noOfRooms'])
    print(AvgRentalByRoomDF)
    fig3 = px.bar(AvgRentalByRoomDF, x="noOfRooms", y="Average_Rental_Fees", title='Average Rental Fees by No of Rooms ')
    graphJSON3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
    description3 = """
    A graph showing the average price comparison between the different areas.
    """

    return render_template('Rental_Graph.html', graphJSON=graphJSON,graphJSON2=graphJSON2,graphJSON3=graphJSON3, description1=description1,description2 = description2,description3 = description3 )

@app.route('/ResaleTable')
def resaleTable():
    if "filter" not in session:
        cur.execute("select r.resale_price,r.town,r.remaining_lease,r.floor_area, h.number_of_rooms from resale as r join housetype as h on h.house_type_id = r.house_type_id ;")
        resale_data = cur.fetchall()
        resale_dict = {}
        for x in resale_data:
            resale_dict[x[0]] = {"resale_price":x[0],
                                 "town": x[1],
                                 "remaining_lease":x[2],
                                 "floor_sqm": x[3],
                                 "no_of_rooms": x[4]
                                 }

        return render_template('Resale_Table.html', resale_dict = resale_dict)

    else:
        filter_dict = session["filter"]
        filter_statement = "select r.resale_price,r.town,r.remaining_lease,r.floor_area, h.number_of_rooms from resale as r inner join  housetype as h on h.house_type_id = r.house_type_id where r.resale_price <= " + filter_dict["resalePrice"] + " and r.town ='" + filter_dict["town"] + "' and r.floor_area <= " + filter_dict["floorArea"] + " and h.number_of_rooms =  " + filter_dict["roomNo"] +";"
        cur.execute(filter_statement)
        resale_data = cur.fetchall()
        resale_dict = {}

        for x in resale_data:
            resale_dict[x[0]] = {"resale_price":x[0],
                                 "town": x[1],
                                 "remaining_lease":x[2],
                                 "floor_sqm": x[3],
                                 "no_of_rooms": x[4]
                                 }

        return render_template('Resale_Table.html', resale_dict = resale_dict)


@app.route("/updateResaleTable", methods=["POST"])
def updateResaleTable():
    if "filter" in session:
        session.pop("filter")
    resalePrice = request.form["resalePrice"]
    town = request.form["town"]
    floorArea = request.form["floorArea"]
    roomNo = request.form["roomNo"]
    session['filter'] = {"resalePrice":resalePrice,"town":town,"floorArea":floorArea, "roomNo":roomNo}
    return redirect(url_for("resaleTable"))


#add user function
@app.route("/registerNewUser", methods=["POST"])
def registerNewUser():
    if request.method == "POST":
        username = request.form["username"]
        name = request.form["name"]
        password = request.form["password"]
        try:
            cur.execute("INSERT INTO user(username, password, name)" +
            "VALUES('" + str(username) + "', '" + str(password) + "', '" + str(name) + "');")
        except mariadb.Error as e:
            #print(cur.statement)
            print("Error adding user: ", {e})
        else:
            conn.commit()
            return redirect(url_for("Login"))

@app.route("/loginUser", methods=["POST"])
def loginUser():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            cur.execute("SELECT user_id FROM user WHERE" +
            " username = '" + str(username) + "' AND password = '" + str(password) + "';")
            if cur.rowcount == 0:
                session["loggedIn"] = False
                flash("Invalid username or password!", "LoginError")
                return redirect(url_for("Login"))
            elif cur.rowcount == 1:
                session["loggedIn"] = True
                session["loggedInUser"] = username
                session["loggedInUserID"] = cur.fetchone()[0]
                if session.get("loginMsg") == True:
                    del session["loginMsg"]
            else:
                session["loggedIn"] = False
                flash("Error occured!", "LoginError")
                return redirect(url_for("Login"))
        except mariadb.Error as e:
            print(cur.statement)
            print("Error logging in: ", {e})
        else:
            return redirect(url_for("Home"))

@app.route("/Logout")
def Logout():
    if session.get("loggedIn") == True:
        session["loggedIn"] = False
        del session["loggedInUser"]
        del session["loggedInUserID"]
    return redirect(url_for("Login"))

# TestLogin
@app.route('/')
def Login():
    return render_template("Login.html")

@app.route('/Register')
def Register():
    return render_template("Register.html")

@app.route('/Home')
def Home():
    if session.get("loggedIn") == True:
        return render_template("Home.html")
    else:
        redirect(url_for("Login"))

@app.route('/ResaleGraph')
def Resaleindex():
    return render_template('Resale_Graph.html')

if __name__ == "__main__":
    app.run(debug=True)
