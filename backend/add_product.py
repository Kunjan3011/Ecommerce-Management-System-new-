# Placeholder for Python script
from database.db_config import connect_to_database

def add_product(name, category, price, stock):
    """Add a new product to the inventory."""
    try:
        db = connect_to_database()
        cursor = db.cursor()

        query = """
        INSERT INTO Products (Name, Category, Price, Stock)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (name, category, price, stock))
        db.commit()
        print(f"Product '{name}' added successfully!")
    except Exception as e:
        print(f"Error adding product: {e}")
    finally:
        if db.is_connected():
            cursor.close()
            db.close()

if __name__ == "__main__":
    # Example usage
    add_product("Laptop", "Electronics", 850.50, 10)
