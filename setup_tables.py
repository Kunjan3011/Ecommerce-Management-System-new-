import mysql
import mysql.connector

from db_config import connect_to_database

def create_tables():
    """Create all necessary tables in the database."""
    try:
        db = connect_to_database()
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

        # Create other tables
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

        suppliers_table = """
        CREATE TABLE IF NOT EXISTS Suppliers (
            SupplierID INT PRIMARY KEY AUTO_INCREMENT,
            Name VARCHAR(255),
            ContactInfo VARCHAR(255)
        );
        """
        cursor.execute(suppliers_table)

        users_table = """
        CREATE TABLE IF NOT EXISTS Users (
            UserID INT PRIMARY KEY AUTO_INCREMENT,
            Username VARCHAR(50) UNIQUE NOT NULL,
            PasswordHash VARCHAR(255) NOT NULL,
            Role ENUM('admin', 'customer') NOT NULL
        );
        """
        cursor.execute(users_table)

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

        db.commit()
        print("Tables created successfully!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if db.is_connected():
            cursor.close()
            db.close()

if __name__ == "__main__":
    create_tables()