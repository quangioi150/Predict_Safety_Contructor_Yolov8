import psycopg2

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
                                    NgaySinh DATE,
                                    MatKhau TEXT NOT NULL);"""

        # Câu lệnh tạo bảng RESULTS
        create_table_results = """CREATE TABLE IF NOT EXISTS RESULTS(
                                    ResultID SERIAL PRIMARY KEY,
                                    UserID INTEGER,
                                    LinkImg TEXT NOT NULL,
                                    TenBenh TEXT NOT NULL,
                                    NgayTest DATE NOT NULL,
                                    DoChinhXac FLOAT NOT NULL,
                                    FOREIGN KEY(UserID) REFERENCES USERS(UserID));"""

        cursor.execute(create_table_users)
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

# Thêm bản ghi vào bảng RESULTS
def insert_results(conn, UserID, LinkImg, TenBenh, NgayTest, DoChinhXac):
    try:
        cursor = conn.cursor()

        insert_query = """INSERT INTO RESULTS
                          (UserID, LinkImg, TenBenh, NgayTest, DoChinhXac)
                          VALUES (%s, %s, %s, %s, %s);"""

        data = (UserID, LinkImg, TenBenh, NgayTest, DoChinhXac)
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

        select_query = """SELECT * FROM RESULTS WHERE UserID = %s;"""
        cursor.execute(select_query, (id,))
        records = cursor.fetchall()
        columns = ("ResultID", "UserID", "LinkImg", "TenBenh", "NgayTest", "DoChinhXac")
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
    insert_user(conn, "Hoàng Cao Minh", "HoangCaoMinh", "Thái Bình", "2001-10-05", "1234")
    insert_user(conn, "Đỗ Viết Đông", "DoVietDong", "Thái Bình", "2001-10-01", "1234")

    # Thêm kết quả vào bảng RESULTS
    insert_results(conn, 1, "http.com.net", "Bệnh lá trắng", "2001-10-05", 99.83)
    insert_results(conn, 1, "http.com.net", "Bệnh lá nâu", "2001-10-05", 99.83)
    insert_results(conn, 2, "http.com.net", "Bệnh lá đen", "2001-10-05", 99.83)
    insert_results(conn, 2, "http.com.net", "Bệnh lá vàng", "2001-10-05", 99.83)

    # Lấy thông tin người dùng theo UserID
    # user_results = get_user_by_id(conn, 1)
    # print(user_results)

    # Xóa bản ghi từ bảng RESULTS theo ResultID
    # delete_result_by_id(conn, 1)

    # Đóng kết nối đến cơ sở dữ liệu
    conn.close()
