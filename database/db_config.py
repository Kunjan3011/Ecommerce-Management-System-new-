# Placeholder for Python script
import mysql.connector



def connect_to_database():
    """Connect to the MySQL database."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123",  # Replace with your database password
        database="ecommerce_management_db",
        port=3306
    )

