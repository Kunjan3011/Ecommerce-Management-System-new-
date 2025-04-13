import mysql.connector
import matplotlib.pyplot as plt
from database.db_config import connect_to_database


def plot_inventory():
    """Plot inventory levels for products."""
    try:
        db = connect_to_database()
        cursor = db.cursor()

        query = "SELECT Name, Stock FROM Products"
        cursor.execute(query)
        data = cursor.fetchall()

        names = [row[0] for row in data]
        stocks = [row[1] for row in data]

        plt.bar(names, stocks, color="blue")
        plt.xlabel("Product Names")
        plt.ylabel("Stock Levels")
        plt.title("Inventory Levels")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()

    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def plot_sales_trends():
    """Plot sales trends over time."""
    try:
        db = connect_to_database()
        cursor = db.cursor()

        query = """
        SELECT SaleDate, SUM(Quantity) AS TotalSales
        FROM Sales
        GROUP BY SaleDate
        ORDER BY SaleDate
        """
        cursor.execute(query)
        data = cursor.fetchall()

        dates = [row[0] for row in data]
        sales = [row[1] for row in data]

        plt.plot(dates, sales, marker="o")
        plt.xlabel("Date")
        plt.ylabel("Total Sales")
        plt.title("Sales Trends Over Time")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    finally:
        if db.is_connected():
            cursor.close()
            db.close()


if __name__ == "__main__":
    plot_inventory()
    plot_sales_trends()
# Placeholder for Python script
