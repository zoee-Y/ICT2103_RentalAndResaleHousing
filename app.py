import pandas.core.groupby.groupby
from flask import Flask, render_template
from flask_navigation import Navigation
import mariadb
import sys
import pandas as pd

app = Flask(__name__)
nav = Navigation(app)

nav.Bar('top', [
    nav.Item('Home', 'Home'),
    nav.Item('Rental', 'GRental'),
    nav.Item('Resale', 'GResale'),
    #add more if needed
])

try:
    conn = mariadb.connect(
             host='127.0.0.1',
             port=3306,
             user='root',
             password='root',
             database='RnRHousing')
except mariadb.Error as e:
    print(f"An error occurred while connecting to MariaDB: ", {e})
    sys.exit(1)

cur = conn.cursor()

def setUpTablesAndData():
    try:
        #create user table
        cur.execute('''CREATE TABLE IF NOT EXISTS
            User(
            userID int NOT NULL PRIMARY KEY AUTO_INCREMENT,
            username varchar(50) NOT NULL,
            password varchar(50) NOT NULL,
            name varchar(100) NOT NULL,
            preferences varchar(255) NULL
        );
        ''')

        #create housetype table
        cur.execute('''CREATE TABLE IF NOT EXISTS
            HouseType(
            houseTypeID int NOT NULL PRIMARY KEY AUTO_INCREMENT,
            houseType varchar(50) NOT NULL,
            numberOfRooms int NOT NULL
        );
        ''')

        #create preference table
        #foreign keys to user and housetype IDs
        cur.execute('''CREATE TABLE IF NOT EXISTS
            Preference(
            preferenceID int NOT NULL PRIMARY KEY AUTO_INCREMENT,
            userID int NOT NULL,
            houseTypeID int NOT NULL,
            districtCode int NOT NULL,
            town varchar(50) NOT NULL,
            FOREIGN KEY (userID) REFERENCES User(userID),
            FOREIGN KEY (houseTypeID) REFERENCES HouseType(houseTypeID)
            );
        ''')

        #create rent table
        #foreign key to housetypeID
        cur.execute('''CREATE TABLE IF NOT EXISTS
            Rent(
            rentID int NOT NULL PRIMARY KEY AUTO_INCREMENT,
            houseTypeID int NOT NULL,
            rentalFees int NOT NULL,
            postalDistrict int NOT NULL,
            floorArea varchar(50) NOT NULL,
            YearOfLease varchar(50) NOT NULL,
            MonthOfLease varchar(50) NOT NULL,
            FOREIGN KEY (houseTypeID) REFERENCES HouseType(houseTypeID)
            );
        ''')

        #create resale table
        #foreign key to housetypeID
        cur.execute('''CREATE TABLE IF NOT EXISTS
            Resale(
            sellID int NOT NULL PRIMARY KEY AUTO_INCREMENT,
            houseTypeID int NOT NULL,
            resalePrice int NOT NULL,
            town varchar(50) NOT NULL,
            remainingLease varchar(50) NOT NULL,
            floorArea int NOT NULL,
            FOREIGN KEY (houseTypeID) REFERENCES HouseType(houseTypeID)
        );
        ''')

        #insert data into housetype:
        #rent rooms: 1,2,3,4,5,6,8
        #resale rooms: 1,2,3,4,5

        #using replace instead of insert in case it has already been added before
        cur.execute('''REPLACE INTO HouseType(houseTypeID, houseType, numberOfRooms)
            VALUES(1, 'Rent', 1), (2, 'Rent', 2),(3, 'Rent',3), (4, 'Rent', 4), (5, 'Rent', 5), (6, 'Rent', 6), (7, 'Rent', 8),
            (8, 'Resale', 1), (9, 'Resale', 2), (10, 'Resale', 3), (11, 'Resale', 4), (12, 'Resale', 5);
        ''')

        conn.commit()

    except mariadb.Error as e:
        print("Error during setup: ", {e})
        print("SQL statement: ", cur.statement)


def insertRentDataFromCSV():
    try:
        data = pd.read_csv("./rental data.csv")
        df = pd.DataFrame(data)
        for row in df.itertuples():
            try:
                cur.execute('''
                   INSERT INTO Rent(
                   houseTypeID,
                   rentalFees,
                   postalDistrict,
                   floorArea,
                   YearOfLease,
                   MonthOfLease)

                   SELECT houseTypeID, ''' + str(row.monthly_gross_rent) + ", " + str(
                    row.postal_district) + ", '" + row.floor_area +"', " + str(row.Lease_Commencement_Year) +", '" + row.Lease_Commencement_Month  +"' "+ ''' FROM HouseType
                       WHERE houseType = 'Rent' AND numberOfRooms = ''' + str(row.no_of_bedroom))

                conn.commit()
            except:
                print(cur.warnings)
                raise
    except mariadb.Error as e:
        print("Error inserting Rent data: ", {e})
    except pandas.core.groupby.groupby.DataError as pe:
        print("Error in Pandas: ", {pe})


def insertResaleDataFromCSV():
    try:
        data = pd.read_csv("./resale data.csv")
        df = pd.DataFrame(data)

        for row in df.itertuples():
            try:
                cur.execute('''
                    INSERT INTO Resale(
                    houseTypeID,
                    resalePrice,
                    town,
                    remainingLease,
                    floorArea)

                    SELECT houseTypeID, ''' + str(
                    row.resale_price) + ", '" + row.town + "' , '" + row.remaining_lease + "', " + str(
                    row.floor_area_sqm) + ''' FROM HouseType
                        WHERE houseType = 'Resale' AND numberOfRooms = ''' + row.flat_type[0])

                conn.commit()
            except:
                print(cur.warnings)
                raise
    except mariadb.Error as e:
        print("Error inserting Resale data: ", {e})
    except pandas.core.groupby.groupby.DataError as pe:
        print("Error in Pandas: ", {pe})


def displayResaleData():
    try:
        cur.execute("SELECT COUNT(*) FROM Resale")

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
        print("Error displaying Rent data: ", {e})
        return "<html><body>Error displaying data!</body></html>"


def displayRentData():
    try:
        cur.execute("SELECT COUNT(*) FROM Rent")

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
        cur.execute("SELECT r.rentalFees, r.postalDistrict, h.numberOfRooms, r.floorArea FROM Rent as r, HouseType as h WHERE r.houseTypeID = h.houseTypeID")
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
@app.route("/")

def index():
    #testDisplayData()
    #setUpTablesAndData()
    #insertRentDataFromCSV() #uncomment this if you want to insert data
    #insertResaleDataFromCSV()
    return "<html><body>" + displayRentData() + displayResaleData() + "</html></body>"

#@app.route('/')
#def Home():
 #   test()
  #  return render_template('Home.html')
@app.route('/RentalGraphs')
def GRental():
    return render_template('Rental_Graph1.html')

@app.route('/ResaleGraphs')
def GResale():
    return render_template('Resale_Graph.html')






if __name__ == "__main__":
    app.run()
