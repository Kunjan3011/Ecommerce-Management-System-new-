# Placeholder for Python script
import mysql.connector

def create_tables():
    """Create tables for the database."""
    try:
        # Establish connection to the MySQL database
        db = mysql.connector.connect(
            host="localhost",
            user="root",  # Replace with your MySQL username
            password="123",  # Replace with your MySQL password
            database="ecommerce_management_db",  # Replace with your database name
            port=3306  # Adjust if necessary
        )
        cursor = db.cursor()

        # Create Products table
        products_table = """
        CREATE TABLE IF NOT EXISTS Products (
            ProductID INT PRIMARY KEY AUTO_INCREMENT,
            Name VARCHAR(255) NOT NULL,
            Category VARCHAR(100),
            Price DECIMAL(10, 2),
            Stock INT
        );
        """
        cursor.execute(products_table)
        print("Products table created successfully.")

        # Create Sales table
        sales_table = """
        CREATE TABLE IF NOT EXISTS Sales (
            SaleID INT PRIMARY KEY AUTO_INCREMENT,
            ProductID INT,
            Quantity INT,
            SaleDate DATE,
            FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
        );
        """
        cursor.execute(sales_table)
        print("Sales table created successfully.")

        # Create Suppliers table
        suppliers_table = """
        CREATE TABLE IF NOT EXISTS Suppliers (
            SupplierID INT PRIMARY KEY AUTO_INCREMENT,
            Name VARCHAR(255),
            ContactInfo VARCHAR(255)
        );
        """
        cursor.execute(suppliers_table)
        print("Suppliers table created successfully.")

        # Create Users table
        users_table = """
        CREATE TABLE IF NOT EXISTS Users (
            UserID INT PRIMARY KEY AUTO_INCREMENT,
            Username VARCHAR(50) UNIQUE NOT NULL,
            Password VARCHAR(255) NOT NULL,
            Role ENUM('admin', 'customer') NOT NULL
        );
        """
        cursor.execute(users_table)
        print("Users table created successfully.")

        # Create Orders table
        orders_table = """
        CREATE TABLE IF NOT EXISTS Orders (
            OrderID INT PRIMARY KEY AUTO_INCREMENT,
            CustomerID INT,
            ProductID INT,
            Quantity INT,
            OrderDate DATE,
            FOREIGN KEY (CustomerID) REFERENCES Users(UserID),
            FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
        );
        """
        cursor.execute(orders_table)
        print("Orders table created successfully.")

        # Commit changes to the database
        db.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        # Close the database connection
        if db.is_connected():
            cursor.close()
            db.close()
            print("Database connection closed.")

if __name__ == "__main__":
    create_tables()