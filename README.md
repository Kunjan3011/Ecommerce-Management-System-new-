

# E-commerce Management System

## Project Overview

The **E-commerce Management System** is a desktop-based application built to streamline inventory, user, and order management processes. Designed for both admins and customers, the system allows users to register, log in, and interact with product data and orders through a user-friendly graphical interface. The project leverages **Tkinter** for GUI design and **MySQL** for backend data storage and operations.

---

## Features

### User Registration and Authentication
- **Register**:
  - Customers can create an account by entering a unique username and password.
  - The registration data is securely stored in the database.
- **Login**:
  - Existing admins and customers can log in using valid credentials.
  - Role-based dashboards are provided based on user type.

### Admin Functionalities
Admins have access to the following features:
1. **View Stocks**:
   - See all products in the inventory.
   - Delete products as needed.
2. **Add Product**:
   - Add new products to the inventory by specifying name, category, price, and stock.
3. **View Customer Orders**:
   - Access all customer orders with details like customer name, product name, quantity, and order date.
4. **Logout**:
   - Exit the admin dashboard and return to the login page.

### Customer Functionalities
Customers can interact with the system through the following features:
1. **View Products**:
   - Browse through available products (only items with stock > 0 are shown).
2. **Place Order**:
   - Select a product and specify the quantity to place an order.
   - Orders are saved in the database for further processing.
3. **Logout**:
   - Exit the customer dashboard and return to the login page.

---

## Technology Stack

- **Python**: Core programming language for backend and GUI functionalities.
- **Tkinter**: Used to create the graphical user interface (GUI).
- **MySQL**: Database management for storing and retrieving user, product, and order data.

---

## Project Structure

```
Ecommerce Management System/
├── database/
│   ├── setup.py             # SQL script for database and table creation
│   ├── db_config.py         # Handles database connection configuration
│   ├── setup_tables.py      # Additional database setup scripts
├── backend/
│   ├── add_product.py       # Backend scripts for product management
│   ├── update_stock.py
│   ├── sales_report.py
├── frontend/
│   ├── gui_directed.py      # Main GUI interface
│   ├── visualizations.py
│   ├── templates/           # Optional frontend templates
├── resources/
│   ├── styles.css           # Styling resources
│   ├── assets/              # Static assets like images
├── tests/
│   ├── test_queries.py      # Unit tests for database queries
│   ├── test_gui_direct.py
├── logs/
│   ├── app.log              # Log files for debugging
├── main.py
├── requirements.txt         # Required Python libraries
├── README.md                # Project documentation
```

---

## Installation and Setup

### Prerequisites
1. Install **Python 3.x**.
2. Install MySQL server.
3. Install required Python libraries:
   ```bash
   pip install mysql-connector-python
   ```

---

### Database Configuration
Set up the following tables in your MySQL database:

#### Users Table
Stores admin and customer user data.
```sql
CREATE TABLE Users (
    UserID INT PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(50) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Role ENUM('admin', 'customer') NOT NULL
);
```

#### Products Table
Stores product inventory data.
```sql
CREATE TABLE Products (
    ProductID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    Category VARCHAR(100),
    Price DECIMAL(10,2),
    Stock INT NOT NULL
);
```

#### Orders Table
Stores customer order information.
```sql
CREATE TABLE Orders (
    OrderID INT PRIMARY KEY AUTO_INCREMENT,
    CustomerID INT,
    ProductID INT,
    Quantity INT,
    OrderDate DATE,
    FOREIGN KEY (CustomerID) REFERENCES Users(UserID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);
```

---

### Inserting Sample Data

**Users Table**:
```sql
INSERT INTO Users (Username, Password, Role)
VALUES ('admin', 'admin123', 'admin'), ('customer1', 'cust123', 'customer');
```

**Products Table**:
```sql
INSERT INTO Products (Name, Category, Price, Stock)
VALUES
('Laptop', 'Electronics', 1200.50, 10),
('Smartphone', 'Electronics', 800.00, 5),
('Book', 'Education', 15.00, 50);
```

---

### Running the Application

1. Open the project folder.
2. Run the main application script:
   ```bash
   python main.py
   ```

---

## Usage

### Login Page
- Existing users can log in with valid credentials to access their dashboards.
- New users can register by creating an account.

### Admin Dashboard
1. Click **View Stocks** to view or manage inventory.
2. Click **Add Product** to add new products to the database.
3. Click **View Customer Orders** to view order history.
4. Click **Logout** to exit the dashboard.

### Customer Dashboard
1. Click **View Products** to browse the available product catalog.
2. Click **Place Order** to select a product and place an order.
3. Click **Logout** to exit the dashboard.

---

## Future Enhancements

1. **Order Tracking**:
   - Add a feature for customers to track the status of their orders.
2. **Search Products**:
   - Include a search bar for customers to filter products by name, category, or price.
3. **Admin Reports**:
   - Generate monthly sales reports for the admin dashboard.

---

## License
This project is open-source and available for modification and enhancement.

---

## Support
If you encounter issues or need assistance with the project, feel free to reach out!

---

You can copy and paste this content into your `README.md` file. Let me know if you'd like additional features or changes included! 🚀
