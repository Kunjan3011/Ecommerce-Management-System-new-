from database.db_config import connect_to_database


def generate_sales_report():
    """Generate a sales report summarizing product sales."""
    try:
        db = connect_to_database()
        cursor = db.cursor()

        query = """
        SELECT p.Name AS ProductName, SUM(s.Quantity) AS TotalSold, SUM(s.Quantity * p.Price) AS TotalRevenue
        FROM Sales s
        JOIN Products p ON s.ProductID = p.ProductID
        GROUP BY p.Name
        ORDER BY TotalSold DESC
        """
        cursor.execute(query)

        print("Sales Report:")
        for row in cursor.fetchall():
            print(f"Product: {row[0]}, Total Sold: {row[1]}, Total Revenue: {row[2]:.2f}")
    except Exception as e:
        print(f"Error generating sales report: {e}")
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


if __name__ == "__main__":
    generate_sales_report()
# Placeholder for Python script
