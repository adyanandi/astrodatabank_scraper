import sqlite3

# Connect to the SQLite database (replace 'your_database.db' with your database file)
conn = sqlite3.connect('as_data.db')

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Execute a query to fetch all data from a table (replace 'your_table' with your table name)
cursor.execute("SELECT * FROM scraped_data")

# Fetch all results
rows = cursor.fetchall()

# Print the results
for row in rows:
    print(row)

# Close the connection
conn.close()
