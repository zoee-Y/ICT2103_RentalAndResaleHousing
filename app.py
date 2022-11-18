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


def displayData():
    cur.execute("SELECT * FROM Resale")

    s = "<table style='border:1px solid red; border-collapse: collapse;'>"
    s = s + '''<tr style='border-bottom: 1px solid black'>
    <td style='padding: 10px; border-right: 1px solid blue'>sellID</td>
    <td style='padding: 10px; border-right: 1px solid blue'>houseTypeID</td>
    <td style='padding: 10px; border-right: 1px solid blue'>resale price</td>
    <td style='padding: 10px; border-right: 1px solid blue'>town</td>
    <td style='padding: 10px; border-right: 1px solid blue'>remaining lease</td>
    <td style='padding: 10px; border-right: 1px solid blue'>floor area (sqft)</td>
    '''
    for row in cur:
        s = s + "<tr style='border-bottom: 1px solid black'>"
        for x in row:
            s = s + "<td style='padding: 10px; border-right: 1px solid blue'>" + str(x) + "</td>"
        s = s + "</tr>"

    return s


def insertDataFromCSV():
    # test insert 7 rows of data
    data = pd.read_csv("./test.csv")
    df = pd.DataFrame(data)

    for row in df.itertuples():
        cur.execute('''
            INSERT INTO Resale(
            houseTypeID,
            resalePrice,
            town,
            remainingLease,
            floorArea)

            SELECT h.houseTypeID, ''' + str(row.resale_price) + ", '" + row.town + "' , '" + row.remaining_lease + "', " + str(row.floor_area_sqm) + ''' FROM HouseType AS h
                WHERE houseType = 'Resale' AND numberOfRooms = ''' + row.flat_type[0])

    conn.commit()

@app.route("/")
def index():
    #insertDataFromCSV() #uncomment this if you want to insert data

    return "<html><body>" + displayData() + "</html></body>"


if __name__ == "__main__":
    app.run()
