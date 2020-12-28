import psycopg2 as dbapi2



dsn="""user=postgres password=28101998.ts host=localhost port=5432 dbname=mydatabase_postgres options='--client_encoding=UTF8'"""



with dbapi2.connect(dsn=dsn) as connection:
    cursor = connection.cursor()
    cursor.execute("""select * from genre_scores""")

