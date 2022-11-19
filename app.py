from flask import Flask
import mariadb
import pandas as pd

app = Flask(__name__)

conn = mariadb.connect(
         host='127.0.0.1',
         port=3306,
         user='root',
         password='root',
         database='RnRHousing')

cur = conn.cursor()


def displayResaleData():
    cur.execute("SELECT * FROM Resale")

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


def insertResaleDataFromCSV():
    # test insert 7 rows of resale data
    data = pd.read_csv("./resale data.csv")
    df = pd.DataFrame(data)

    for row in df.itertuples():
        cur.execute('''
            INSERT INTO Resale(
            houseTypeID,
            resalePrice,
            town,
            remainingLease,
            floorArea)

            SELECT houseTypeID, ''' + str(row.resale_price) + ", '" + row.town + "' , '" + row.remaining_lease + "', " + str(row.floor_area_sqm) + ''' FROM HouseType
                WHERE houseType = 'Resale' AND numberOfRooms = ''' + row.flat_type[0])

    conn.commit()

def displayRentData():
    cur.execute("SELECT * FROM Rent")

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

def insertRentDataFromCSV():
    # test insert 7 rows of rental data
    data = pd.read_csv("./rental data.csv")
    df = pd.DataFrame(data)

    for row in df.itertuples():
        cur.execute('''
               INSERT INTO Rent(
               houseTypeID,
               rentalFees,
               postalDistrict,
               floorArea)

               SELECT houseTypeID, ''' + str(row.monthly_gross_rent) + ", " + str(row.postal_district) + ", '" + row.floor_area  + "'" + ''' FROM HouseType
                   WHERE houseType = 'Rent' AND numberOfRooms = ''' + str(row.no_of_bedroom))

    conn.commit()

def testDisplayData():
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

    return s

@app.route("/")
def index():
    insertRentDataFromCSV() #uncomment this if you want to insert data
    #insertResaleDataFromCSV()

    return "<html><body>" + displayRentData() + displayResaleData() + "</html></body>"


if __name__ == "__main__":
    app.run()
