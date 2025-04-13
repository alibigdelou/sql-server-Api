import pyodbc

connection_string = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost;"  
    "Database=master;" 
    "Trusted_Connection=yes;"
)


# conn = None  


# try:
#     conn = pyodbc.connect(connection_string)
#     cursor = conn.cursor()

#     cursor.execute("use [uni];") 
    
#     cursor.execute("select * from Properties;")
#     row = cursor.fetchone()
    
#     if row:
#         print("اتصال برقرار شد و داده خوانده شد:", row)
#     else:
#         print("اتصال برقرار شد ولی داده‌ای وجود ندارد.")

# except pyodbc.Error as e:
#     print("خطا در اتصال:", e)

