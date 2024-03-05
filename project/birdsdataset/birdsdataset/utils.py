import pymssql as msql

#Create connection
def connectDB():
    server='sertc30035.database.windows.net'
    user='jazz'
    password='serv_1234'
    database='Ejemplo'
    conn = msql.connect(server,user,password,database,as_dict=True)
    
    return conn