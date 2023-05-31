import psycopg2
from PIL import Image
import io
# Kết nối đến cơ sở dữ liệu PostgreSQL
def connect():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="postgres",
            user="postgres",
            password="1234"
            # options="-c search_path=Safety_PPE"
        )
        print("Connected to PostgreSQL")
        cursor = conn.cursor()
        # Tạo schema 'Safety_PPE' nếu chưa tồn tại
        create_schema_query = "CREATE SCHEMA IF NOT EXISTS Safety_PPE;"
        cursor.execute(create_schema_query)

        # Sử dụng schema 'Safety_PPE'
        use_schema_query = "SET search_path TO Safety_PPE, public;"
        cursor.execute(use_schema_query)
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print("Failed to connect to PostgreSQL", error)

# Tạo bảng USERS và RESULTS
def create_tables(conn):
    try:
        cursor = conn.cursor()
        # Câu lệnh tạo bảng USERS
        create_table_users = """CREATE TABLE IF NOT EXISTS USERS(
                                    UserID SERIAL PRIMARY KEY,
                                    HoTen TEXT NOT NULL,
                                    TenDN TEXT NOT NULL,
                                    DiaChi TEXT NOT NULL,
                                    NgaySinh TEXT,
                                    MatKhau TEXT NOT NULL);"""
                                    
        # Câu lệnh tạo bảng IMAGES
        create_table_images = """CREATE TABLE IF NOT EXISTS IMAGES(
                                    UserID INTEGER,
                                    ImageID SERIAL PRIMARY KEY,
                                    Images TEXT NOT NULL,
                                    Prediction TEXT NOT NULL,
                                    FOREIGN KEY(UserID) REFERENCES USERS(UserID));"""
        
        # Câu lệnh tạo bảng RESULTS
        create_table_results = """CREATE TABLE IF NOT EXISTS RESULTS(
                                    ResultID SERIAL PRIMARY KEY,
                                    ImageID INTEGER,
                                    NameObject TEXT NOT NULL,
                                    NgayTest TEXT NOT NULL,
                                    DoChinhXac FLOAT NOT NULL,
                                    FOREIGN KEY(ImageID) REFERENCES IMAGES(ImageID));"""

        cursor.execute(create_table_users)
        cursor.execute(create_table_images)
        cursor.execute(create_table_results)
        conn.commit()
        print("PostgreSQL tables created")

        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while creating PostgreSQL tables", error)

# Thêm bản ghi vào bảng USERS
def insert_user(conn, HoTen, TenDN, DiaChi, NgaySinh, MatKhau):
    try:
        cursor = conn.cursor()

        insert_query = """INSERT INTO USERS
                          (HoTen, TenDN, DiaChi, NgaySinh, MatKhau)
                          VALUES (%s, %s, %s, %s, %s);"""

        data = (HoTen, TenDN, DiaChi, NgaySinh, MatKhau)
        cursor.execute(insert_query, data)
        conn.commit()
        print("Record inserted successfully into USERS table")

        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Failed to insert record into USERS table", error)
 
 
# Thêm bản ghi vào bảng IMAGES       
def insert_images(conn, UserID, Images, Prediction):
    try:
        cursor = conn.cursor()
        
        # images = open(Images, 'rb').read()

        insert_query = """INSERT INTO IMAGES
                          ( UserID, Images, Prediction)
                          VALUES ( %s, %s, %s);"""

        data = ( UserID, Images, Prediction)
        cursor.execute(insert_query, data)
        conn.commit()
        print("Record inserted successfully into IMAGES table")

        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Failed to insert record into IMAGES table", error)

# Thêm bản ghi vào bảng RESULTS
def insert_results(conn, ImageID, NameObject, NgayTest, DoChinhXac):
    try:
        cursor = conn.cursor()

        insert_query = """INSERT INTO RESULTS
                          (ImageID, NameObject, NgayTest, DoChinhXac)
                          VALUES (%s, %s, %s, %s);"""

        data = (ImageID, NameObject, NgayTest, DoChinhXac)
        cursor.execute(insert_query, data)
        conn.commit()
        print("Record inserted successfully into RESULTS table")

        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Failed to insert record into RESULTS table", error)
        
# Lấy thông tin người dùng theo UserID
def get_user_by_id(conn, id):
    try:
        cursor = conn.cursor()

        # select_query = """SELECT * FROM RESULTS WHERE UserID = %s;"""
        select_query = """SELECT UserID, ResultID, i.ImageID, Prediction, NameObject, DoChinhXac, Images, r.NgayTest
                            FROM safety_ppe.RESULTS AS r
                            INNER JOIN safety_ppe.IMAGES AS i ON r.ImageID = i.ImageID
                            WHERE UserID = %s;"""
                            
        cursor.execute(select_query, (id,))
        records = cursor.fetchall()
        columns = ("UserID", "ResultID", "ImageID", "Prediction", "NameObject", "DoChinhXac", "Images", "NgayTest")
        results = [dict(zip(columns, record)) for record in records]

        cursor.close()
        return results
    except (Exception, psycopg2.DatabaseError) as error:
        print("Failed to retrieve data from RESULTS table", error)
        
# Đăng nhập 
def Login(conn, user, password):
    try:
        cursor = conn.cursor()

        sql_select_query_1 = """SELECT UserID FROM USERS WHERE TenDN = %s AND MatKhau = %s"""
        sql_select_query_2 = """SELECT * FROM USERS WHERE TenDN = %s AND MatKhau = %s"""

        cursor.execute(sql_select_query_1, (user, password))
        records = cursor.fetchall()

        if len(records) == 0:
            results = {
                "UserID": 0,
                "User": {}
            }
        else:
            cursor.execute(sql_select_query_2, (user, password))
            remarks = cursor.fetchone()
            keys = ("UserID", "HoTen", "TenDN", "DiaChi", "NgaySinh", "MatKhau")
            new_dict = dict(zip(keys, remarks))
            results = {
                "UserID": str(records[0][0]),
                "User": new_dict
            }

        cursor.close()
        return results

    except (Exception, psycopg2.DatabaseError) as error:
        print("Failed to read data from the database", error)

# Cập nhật bản ghi từ bảng user 
def update_table_users(conn, UserID, HoTen, TenDN, DiaChi, NgaySinh, MatKhau):
    try:
        cursor = conn.cursor()

        sql_update_query = """UPDATE USERS SET HoTen = %s, TenDN = %s, DiaChi = %s, NgaySinh = %s, MatKhau = %s WHERE UserID = %s"""
        data = (HoTen, TenDN, DiaChi, NgaySinh, MatKhau, UserID)
        cursor.execute(sql_update_query, data)
        conn.commit()
        print("Record updated successfully")

        cursor.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print("Failed to update PostgreSQL table", error)

# Lấy imageID hiện tại
def get_image_id_current(conn):
    try:
        cursor = conn.cursor()

        query = """SELECT MAX(imageid) AS max_imageid FROM safety_ppe.images;"""

        cursor.execute(query,)
        image_id = cursor.fetchall()[0][0]
        if image_id == None:
            image_id = 1
        
        conn.commit()
        print("Recordsuccessfully from RESULTS table")

        cursor.close()
        return image_id
    except (Exception, psycopg2.DatabaseError) as error:
        print("Failed to delete record from RESULTS table", error)

# Xóa bản ghi từ bảng RESULTS theo ResultID
def delete_result_by_id(conn, id):
    try:
        cursor = conn.cursor()

        delete_query = """DELETE FROM RESULTS WHERE ResultID = %s;"""
        cursor.execute(delete_query, (id,))
        conn.commit()
        print("Record deleted successfully from RESULTS table")

        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Failed to delete record from RESULTS table", error)

if __name__ == '__main__':
    # Kết nối đến cơ sở dữ liệu
    conn = connect()

    create_tables(conn)

    # Thêm người dùng vào bảng USERS
    # insert_user(conn, "Hoàng Cao Minh", "HoangCaoMinh", "Thái Bình", "2001-10-05", "1234")
    # insert_user(conn, "Đỗ Viết Đông", "DoVietDong", "Thái Bình", "2001-10-01", "1234")

    # Thêm image vào bảng IMAGES
    # insert_images(conn, 1, "./", 'DANGEROUS')
    # insert_images(conn, 1, "static/uploads/prediction.jpg", 'DANGEROUS')
    # insert_images(conn, 2, "static/uploads/prediction.jpg", 'SAFETY')
    # insert_images(conn, 2, "static/uploads/prediction.jpg", 'DANGEROUS')
    
    # Thêm kết quả vào bảng RESULTS
    # insert_results(conn, 1, "NO-SafetyVest", "2001-10-05", 0.9262253642)
    # insert_results(conn, 2, "Person", "2001-10-05", 0.9262253642)
    # insert_results(conn, 3, "SafetyVest", "2001-10-05", 0.9262253642)
    # insert_results(conn, 1, "NO-Hardhat", "2001-10-05", 0.9262253642)
    # insert_results(conn, 4, "NO-SafetyVest", "2001-10-05", 0.9262253642)


    # Lấy thông tin người dùng theo UserID
    # user_results = get_user_by_id(conn, 1)
    # print(user_results)

    # Xóa bản ghi từ bảng RESULTS theo ResultID
    # delete_result_by_id(conn, 1)

    # Đóng kết nối đến cơ sở dữ liệu
    image_id = get_image_id_current(conn)
    print(image_id)
    conn.close()
