from database.db_config import connect_to_database


def update_stock(product_id, new_stock):
    """Update stock levels for a specific product."""
    try:
        db = connect_to_database()
        cursor = db.cursor()

        query = """
        UPDATE Products
        SET Stock = %s
        WHERE ProductID = %s
        """
        cursor.execute(query, (new_stock, product_id))
        db.commit()
        print(f"Stock updated for Product ID {product_id}. New stock: {new_stock}.")
    except Exception as e:
        print(f"Error updating stock: {e}")
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


if __name__ == "__main__":
    # Example usage
    update_stock(1, 25)
# Placeholder for Python script
