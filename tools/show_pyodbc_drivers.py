import traceback
try:
    import pyodbc
    print('Installed ODBC drivers:')
    for d in pyodbc.drivers():
        print('-', d)
except Exception:
    traceback.print_exc()
