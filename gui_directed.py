import sys
import tkinter as tk
from idlelib import tree
from tkinter import messagebox
from tkinter import ttk
from database.db_config import connect_to_database
from datetime import datetime
import os


def generate_receipt(order_id, customer_id):
    """Generate a PDF receipt for the placed order."""
    try:
        db = connect_to_database()
        cursor = db.cursor(dictionary=True)

        # Get order details
        cursor.execute("""
            SELECT o.OrderID, o.OrderDate, o.Quantity, 
                   p.Name AS ProductName, p.Price, 
                   u.Username AS CustomerName
            FROM Orders o
            JOIN Products p ON o.ProductID = p.ProductID
            JOIN Users u ON o.CustomerID = u.UserID
            WHERE o.OrderID = %s AND o.CustomerID = %s
        """, (order_id, customer_id))
        order = cursor.fetchone()

        if not order:
            return None, "Order not found!"

        # Calculate total
        total = order['Quantity'] * order['Price']

        # Create receipts directory if it doesn't exist
        if not os.path.exists('receipts'):
            os.makedirs('receipts')

        # Generate PDF receipt
        from fpdf import FPDF

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Receipt header
        pdf.cell(200, 10, txt="ORDER RECEIPT", ln=1, align='C')
        pdf.cell(200, 10, txt="-" * 50, ln=1, align='C')

        # Order details
        pdf.cell(200, 10, txt=f"Order ID: {order['OrderID']}", ln=1)
        pdf.cell(200, 10, txt=f"Date: {order['OrderDate']}", ln=1)
        pdf.cell(200, 10, txt=f"Customer: {order['CustomerName']}", ln=1)
        pdf.cell(200, 10, txt="-" * 50, ln=1)

        # Product details
        pdf.cell(100, 10, txt="Product", border=1)
        pdf.cell(30, 10, txt="Price", border=1)
        pdf.cell(30, 10, txt="Qty", border=1)
        pdf.cell(30, 10, txt="Subtotal", border=1, ln=1)

        pdf.cell(100, 10, txt=order['ProductName'], border=1)
        pdf.cell(30, 10, txt=f"${order['Price']:.2f}", border=1)
        pdf.cell(30, 10, txt=str(order['Quantity']), border=1)
        pdf.cell(30, 10, txt=f"${total:.2f}", border=1, ln=1)

        # Total
        pdf.cell(160, 10, txt="TOTAL:", border=1)
        pdf.cell(30, 10, txt=f"${total:.2f}", border=1, ln=1)

        # Footer
        pdf.cell(200, 10, txt="Thank you for your order!", ln=1, align='C')

        # Save the PDF
        filename = f"receipts/Order_{order_id}_{customer_id}.pdf"
        pdf.output(filename)

        return filename, None

    except Exception as e:
        return None, f"Error generating receipt: {e}"
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def view_past_orders(parent_window, customer_id):
    """Display a window showing the customer's past orders."""
    try:
        db = connect_to_database()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT o.OrderID, o.OrderDate, p.Name AS ProductName, 
                   o.Quantity, p.Price, (o.Quantity * p.Price) AS Total
            FROM Orders o
            JOIN Products p ON o.ProductID = p.ProductID
            WHERE o.CustomerID = %s
            ORDER BY o.OrderDate DESC
        """, (customer_id,))
        orders = cursor.fetchall()

        if not orders:
            messagebox.showinfo("Info", "You haven't placed any orders yet!")
            return

        orders_window = tk.Toplevel(parent_window)
        orders_window.title("Your Order History")
        orders_window.geometry("800x500")

        tk.Label(orders_window, text="Your Order History", font=("Arial", 16)).pack(pady=10)

        # Create treeview with scrollbars
        frame = tk.Frame(orders_window)
        frame.pack(fill=tk.BOTH, expand=True)

        tree = ttk.Treeview(frame, columns=("OrderID", "OrderDate", "ProductName", "Quantity", "Price", "Total"),
                            show="headings")

        # Define headings
        tree.heading("OrderID", text="Order ID")
        tree.heading("OrderDate", text="Date")
        tree.heading("ProductName", text="Product")
        tree.heading("Quantity", text="Qty")
        tree.heading("Price", text="Unit Price")
        tree.heading("Total", text="Total")

        # Set column widths
        tree.column("OrderID", width=80, anchor='center')
        tree.column("OrderDate", width=100, anchor='center')
        tree.column("ProductName", width=200)
        tree.column("Quantity", width=60, anchor='center')
        tree.column("Price", width=80, anchor='center')
        tree.column("Total", width=80, anchor='center')

        # Add scrollbars
        vscroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hscroll = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vscroll.set, xscrollcommand=hscroll.set)

        tree.grid(row=0, column=0, sticky="nsew")
        vscroll.grid(row=0, column=1, sticky="ns")
        hscroll.grid(row=1, column=0, sticky="ew")

        # Configure grid weights
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Insert order data
        for order in orders:
            tree.insert("", tk.END, values=(
                order['OrderID'],
                order['OrderDate'],
                order['ProductName'],
                order['Quantity'],
                f"${order['Price']:.2f}",
                f"${order['Total']:.2f}"
            ))

        # Add button to view receipt
        def view_receipt():
            selected = tree.focus()
            if not selected:
                messagebox.showerror("Error", "Please select an order first!")
                return

            order_id = tree.item(selected)['values'][0]
            filename, error = generate_receipt(order_id, customer_id)

            if error:
                messagebox.showerror("Error", error)
            else:
                try:
                    import subprocess
                    if os.name == 'nt':  # Windows
                        os.startfile(filename)
                    else:  # macOS and Linux
                        subprocess.run(['open', filename] if sys.platform == 'darwin' else ['xdg-open', filename])
                except Exception as e:
                    messagebox.showinfo("Receipt Generated",
                                        f"Receipt saved as:\n{filename}\n\n(No PDF viewer found to open automatically)")

        btn_frame = tk.Frame(orders_window)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="View Receipt", command=view_receipt).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Close", command=orders_window.destroy).pack(side=tk.LEFT, padx=5)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch orders: {e}")
    finally:
        if db.is_connected():
            cursor.close()
            db.close()
def authenticate_user(username, password):
    """Authenticate the user by checking credentials in the database."""
    try:
        db = connect_to_database()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM Users WHERE Username = %s AND Password = %s", (username, password))
        user = cursor.fetchone()

        if user:
            return user["Role"], user["UserID"], None  # Return role, user ID, and no error
        else:
            return None, None, "Invalid username or password!"
    except Exception as e:
        return None, None, f"Authentication error: {e}"
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def add_product():
    """Open a new window to add a product."""

    def save_product():
        """Save the product to the database."""
        name = name_entry.get()
        category = category_entry.get()
        price = price_entry.get()
        stock = stock_entry.get()

        if not name or not price or not stock:
            messagebox.showerror("Error", "Please fill in all required fields!")
            return

        try:
            db = connect_to_database()
            cursor = db.cursor()

            cursor.execute("""
                INSERT INTO Products (Name, Category, Price, Stock)
                VALUES (%s, %s, %s, %s)
            """, (name, category, float(price), int(stock)))
            db.commit()

            messagebox.showinfo("Success", f"Product '{name}' added successfully!")
            add_product_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add product: {e}")
        finally:
            if db.is_connected():
                cursor.close()
                db.close()

    add_product_window = tk.Toplevel()
    add_product_window.title("Add Product")
    add_product_window.geometry("400x300")

    tk.Label(add_product_window, text="Product Name").pack()
    name_entry = tk.Entry(add_product_window)
    name_entry.pack()

    tk.Label(add_product_window, text="Category").pack()
    category_entry = tk.Entry(add_product_window)
    category_entry.pack()

    tk.Label(add_product_window, text="Price").pack()
    price_entry = tk.Entry(add_product_window)
    price_entry.pack()

    tk.Label(add_product_window, text="Stock").pack()
    stock_entry = tk.Entry(add_product_window)
    stock_entry.pack()

    tk.Button(add_product_window, text="Save Product", command=save_product).pack(pady=10)


def view_stocks(admin_app):
    """Open a new window to view stocks and delete products."""

    def delete_product():
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a product to delete!")
            return

        product_id = tree.item(selected_item)["values"][0]
        try:
            db = connect_to_database()
            cursor = db.cursor()

            cursor.execute("DELETE FROM Products WHERE ProductID = %s", (product_id,))
            db.commit()

            messagebox.showinfo("Success", f"Product ID {product_id} deleted successfully!")
            tree.delete(selected_item)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete product: {e}")
        finally:
            if db.is_connected():
                cursor.close()
                db.close()

    try:
        db = connect_to_database()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM Products")
        products = cursor.fetchall()

        view_stocks_window = tk.Toplevel(admin_app)
        view_stocks_window.title("View Stocks")
        view_stocks_window.geometry("600x400")

        tk.Label(view_stocks_window, text="Stock Details", font=("Arial", 16)).pack(pady=10)

        tree = ttk.Treeview(view_stocks_window, columns=("ProductID", "Name", "Category", "Price", "Stock"),
                            show="headings")
        tree.heading("ProductID", text="Product ID")
        tree.heading("Name", text="Name")
        tree.heading("Category", text="Category")
        tree.heading("Price", text="Price")
        tree.heading("Stock", text="Stock")

        tree.pack(fill=tk.BOTH, expand=True)

        for product in products:
            tree.insert("", tk.END, values=product)

        tk.Button(view_stocks_window, text="Delete Product", command=delete_product).pack(pady=10)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch stock data: {e}")
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def view_products(parent_window, is_admin=False):
    """Open a new window to view available products with stock quantities."""
    try:
        db = connect_to_database()
        cursor = db.cursor()

        if is_admin:
            # Admin sees all products, even those with 0 stock
            cursor.execute("SELECT ProductID, Name, Category, Price, Stock FROM Products")
        else:
            # Customer only sees products with stock > 0
            cursor.execute("SELECT ProductID, Name, Category, Price, Stock FROM Products WHERE Stock > 0")

        products = cursor.fetchall()

        view_products_window = tk.Toplevel(parent_window)
        view_products_window.title("Available Products")
        view_products_window.geometry("600x400")

        title = "Product Inventory" if is_admin else "Available Products"
        tk.Label(view_products_window, text=title, font=("Arial", 16)).pack(pady=10)

        columns = ("ProductID", "Name", "Category", "Price", "Stock")
        tree = ttk.Treeview(view_products_window, columns=columns, show="headings")

        # Configure columns
        tree.heading("ProductID", text="Product ID")
        tree.heading("Name", text="Name")
        tree.heading("Category", text="Category")
        tree.heading("Price", text="Price")
        tree.heading("Stock", text="In Stock")

        # Set column widths
        tree.column("ProductID", width=80, anchor='center')
        tree.column("Name", width=150)
        tree.column("Category", width=100)
        tree.column("Price", width=80, anchor='center')
        tree.column("Stock", width=80, anchor='center')

        tree.pack(fill=tk.BOTH, expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(view_products_window, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        # Insert data with stock quantity highlighting
        for product in products:
            stock = product[4]
            if stock <= 0 and not is_admin:
                continue  # Skip out-of-stock items for customers

            tags = ()
            if stock <= 0:
                tags = ('out-of-stock',)
            elif stock < 5:
                tags = ('low-stock',)

            tree.insert("", tk.END, values=product, tags=tags)

        # Configure tag styles
        tree.tag_configure('out-of-stock', foreground='red')
        tree.tag_configure('low-stock', foreground='orange')

    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch products: {e}")
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def place_order(parent_window, customer_id):
    """Open a new window for the customer to place an order with stock visibility."""
    try:
        db = connect_to_database()
        cursor = db.cursor()

        cursor.execute("SELECT ProductID, Name, Category, Price, Stock FROM Products WHERE Stock > 0")
        products = cursor.fetchall()

        place_order_window = tk.Toplevel(parent_window)
        place_order_window.title("Place Order")
        place_order_window.geometry("700x500")

        tk.Label(place_order_window, text="Available Products (Stock shown)", font=("Arial", 16)).pack(pady=10)

        # Create treeview with scrollbars
        frame = tk.Frame(place_order_window)
        frame.pack(fill=tk.BOTH, expand=True)

        tree = ttk.Treeview(frame, columns=("ProductID", "Name", "Category", "Price", "Stock"),
                            show="headings")

        # Define headings
        tree.heading("ProductID", text="Product ID")
        tree.heading("Name", text="Name")
        tree.heading("Category", text="Category")
        tree.heading("Price", text="Price")
        tree.heading("Stock", text="In Stock")

        # Set column widths
        tree.column("ProductID", width=80, anchor='center')
        tree.column("Name", width=200)
        tree.column("Category", width=120)
        tree.column("Price", width=80, anchor='center')
        tree.column("Stock", width=80, anchor='center')

        # Add scrollbars
        vscroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hscroll = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vscroll.set, xscrollcommand=hscroll.set)

        tree.grid(row=0, column=0, sticky="nsew")
        vscroll.grid(row=0, column=1, sticky="ns")
        hscroll.grid(row=1, column=0, sticky="ew")

        # Configure grid weights
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Insert products with stock highlighting
        for product in products:
            stock = product[4]
            tags = ()
            if stock < 5:  # Highlight low stock items
                tags = ('low-stock',)
            tree.insert("", tk.END, values=product, tags=tags)

        # Configure tag style
        tree.tag_configure('low-stock', foreground='orange')

        # Quantity input frame
        input_frame = tk.Frame(place_order_window)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Enter Quantity:").pack(side=tk.LEFT)
        quantity_entry = tk.Entry(input_frame, width=10)
        quantity_entry.pack(side=tk.LEFT, padx=10)

        # Button frame
        btn_frame = tk.Frame(place_order_window)
        btn_frame.pack(pady=10)

        # Place Order button
        tk.Button(btn_frame, text="Place Order", command=lambda: submit_order()).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=place_order_window.destroy).pack(side=tk.LEFT, padx=5)

        def submit_order():
            selected_item = tree.focus()
            if not selected_item:
                messagebox.showerror("Error", "Please select a product!")
                return

            product_id = tree.item(selected_item)["values"][0]
            current_stock = tree.item(selected_item)["values"][4]
            quantity = quantity_entry.get()

            if not quantity or not quantity.isdigit() or int(quantity) <= 0:
                messagebox.showerror("Error", "Please enter a valid quantity!")
                return

            if int(quantity) > current_stock:
                messagebox.showerror("Error", f"Not enough stock! Only {current_stock} available.")
                return

            try:
                db = connect_to_database()
                cursor = db.cursor()

                # Update order and stock in a transaction
                cursor.execute("START TRANSACTION")

                # Place the order
                cursor.execute("""
                    INSERT INTO Orders (CustomerID, ProductID, Quantity, OrderDate)
                    VALUES (%s, %s, %s, CURDATE())
                """, (customer_id, product_id, int(quantity)))

                # Get the auto-generated order ID
                order_id = cursor.lastrowid

                # Update stock
                cursor.execute("""
                    UPDATE Products 
                    SET Stock = Stock - %s 
                    WHERE ProductID = %s
                """, (int(quantity), product_id))

                db.commit()

                # Generate and show receipt
                filename, error = generate_receipt(order_id, customer_id)
                if error:
                    messagebox.showerror("Error", f"Order placed but receipt generation failed: {error}")
                else:
                    try:
                        import subprocess
                        if os.name == 'nt':  # Windows
                            os.startfile(filename)
                        else:  # macOS and Linux
                            subprocess.run(['open', filename] if sys.platform == 'darwin' else ['xdg-open', filename])
                    except:
                        messagebox.showinfo("Order Placed",
                                            f"Order #{order_id} placed successfully!\n\nReceipt saved as:\n{filename}")

                place_order_window.destroy()
            except Exception as e:
                db.rollback()
                messagebox.showerror("Error", f"Failed to place order: {e}")
            finally:
                if db.is_connected():
                    cursor.close()
                    db.close()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch products: {e}")
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def view_customer_orders(admin_app):
    """Open a new window to view customer orders."""
    try:
        db = connect_to_database()
        cursor = db.cursor()

        query = """
        SELECT o.OrderID, u.Username AS CustomerName, p.Name AS ProductName, o.Quantity, o.OrderDate
        FROM Orders o
        JOIN Users u ON o.CustomerID = u.UserID
        JOIN Products p ON o.ProductID = p.ProductID
        ORDER BY o.OrderDate DESC
        """
        cursor.execute(query)
        orders = cursor.fetchall()

        orders_window = tk.Toplevel(admin_app)
        orders_window.title("View Customer Orders")
        orders_window.geometry("600x400")

        tk.Label(orders_window, text="Customer Orders", font=("Arial", 16)).pack(pady=10)

        tree = ttk.Treeview(orders_window, columns=("OrderID", "CustomerName", "ProductName", "Quantity", "OrderDate"),
                            show="headings")
        tree.heading("OrderID", text="Order ID")
        tree.heading("CustomerName", text="Customer Name")
        tree.heading("ProductName", text="Product Name")
        tree.heading("Quantity", text="Quantity")
        tree.heading("OrderDate", text="Order Date")

        tree.pack(fill=tk.BOTH, expand=True)

        for order in orders:
            tree.insert("", tk.END, values=order)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch customer orders: {e}")
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def admin_dashboard():
    """Admin dashboard with modern styling."""
    admin_app = tk.Tk()
    admin_app.title("Admin Dashboard")
    admin_app.geometry("450x400")
    admin_app.configure(bg="#f0f2f5")

    # ... (previous admin dashboard code remains the same until buttons)

    # Buttons - modify the View Products button
    buttons = [
        ("View Stocks", lambda: view_stocks(admin_app)),
        ("View Product Inventory", lambda: view_products(admin_app, is_admin=True)),
        ("Add Product", add_product),
        ("View Customer Orders", lambda: view_customer_orders(admin_app)),
        ("Logout", lambda: [admin_app.destroy(), login_screen()])
    ]

    # ... (rest of admin dashboard code remains the same)


def customer_dashboard(customer_id):
    """Customer dashboard with modern styling."""
    customer_app = tk.Tk()
    customer_app.title("Customer Dashboard")
    customer_app.geometry("450x400")
    customer_app.configure(bg="#f0f2f5")

    # Custom colors
    bg_color = "#f0f2f5"
    button_color = "#4a6fa5"
    button_hover = "#3a5a80"
    text_color = "#333333"

    # Main frame
    main_frame = tk.Frame(customer_app, bg=bg_color)
    main_frame.pack(pady=30, padx=30, fill="both", expand=True)

    # Title
    tk.Label(main_frame, text="Customer Dashboard", font=("Arial", 20, "bold"),
             bg=bg_color, fg=text_color).pack(pady=(0, 30))

    # Buttons - added View Past Orders button
    buttons = [
        ("View Available Products", lambda: view_products(customer_app)),
        ("Place New Order", lambda: place_order(customer_app, customer_id)),
        ("View Past Orders", lambda: view_past_orders(customer_app, customer_id)),
        ("Logout", lambda: [customer_app.destroy(), login_screen()])
    ]

    for text, command in buttons:
        btn = tk.Button(main_frame, text=text, font=("Arial", 12),
                        bg=button_color, fg="white", activebackground=button_hover,
                        activeforeground="white", bd=0, padx=20, pady=10,
                        command=command)
        btn.pack(fill="x", pady=8)
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg=button_hover))
        btn.bind("<Leave>", lambda e, b=btn: b.config(bg=button_color))

    customer_app.mainloop()

# ... (keep all previous imports and functions until login_screen)

def login_screen():
    """Create the login screen with modern styling."""
    global root, username_entry, password_entry

    root = tk.Tk()
    root.title("Login Page")
    root.geometry("350x300")
    root.configure(bg="#f0f2f5")  # Light gray background

    # Custom colors
    bg_color = "#f0f2f5"
    button_color = "#4a6fa5"  # Nice blue
    button_hover = "#3a5a80"
    text_color = "#333333"
    accent_color = "#6c8fc7"

    # Main frame
    main_frame = tk.Frame(root, bg=bg_color)
    main_frame.pack(pady=20, padx=20, fill="both", expand=True)

    # Title
    tk.Label(main_frame, text="Login", font=("Arial", 18, "bold"),
             bg=bg_color, fg=text_color).pack(pady=(0, 20))

    # Username
    tk.Label(main_frame, text="Username", font=("Arial", 10),
             bg=bg_color, fg=text_color).pack(anchor="w", padx=10)
    username_entry = tk.Entry(main_frame, font=("Arial", 12))
    username_entry.pack(fill="x", padx=10, pady=(0, 15))

    # Password
    tk.Label(main_frame, text="Password", font=("Arial", 10),
             bg=bg_color, fg=text_color).pack(anchor="w", padx=10)
    password_entry = tk.Entry(main_frame, show="*", font=("Arial", 12))
    password_entry.pack(fill="x", padx=10, pady=(0, 20))

    # Login button
    login_btn = tk.Button(main_frame, text="Login", font=("Arial", 12, "bold"),
                          bg=button_color, fg="white", activebackground=button_hover,
                          activeforeground="white", bd=0, padx=20, pady=8,
                          command=lambda: perform_login())
    login_btn.pack(fill="x", padx=10, pady=(0, 10))
    login_btn.bind("<Enter>", lambda e: login_btn.config(bg=button_hover))
    login_btn.bind("<Leave>", lambda e: login_btn.config(bg=button_color))

    # Register button
    register_btn = tk.Button(main_frame, text="Register New Account", font=("Arial", 10),
                             bg=bg_color, fg=accent_color, activebackground=bg_color,
                             activeforeground=accent_color, bd=0,
                             command=registration_window)
    register_btn.pack(pady=5)
    register_btn.bind("<Enter>", lambda e: register_btn.config(fg="#5a7db5"))
    register_btn.bind("<Leave>", lambda e: register_btn.config(fg=accent_color))

    def perform_login():
        username = username_entry.get()
        password = password_entry.get()
        role, user_id, error = authenticate_user(username, password)

        if error:
            messagebox.showerror("Error", error)
            return

        root.destroy()
        if role == "admin":
            admin_dashboard()
        elif role == "customer":
            customer_dashboard(user_id)

    root.mainloop()


def register_user(username, password, confirm_password):
    """Register a new user in the database."""
    if not username or not password:
        return "Username and password are required!"

    if password != confirm_password:
        return "Passwords do not match!"

    try:
        db = connect_to_database()
        cursor = db.cursor()

        # Check if username already exists
        cursor.execute("SELECT * FROM Users WHERE Username = %s", (username,))
        if cursor.fetchone():
            return "Username already exists!"

        # Insert new user with 'customer' role by default
        cursor.execute("""
            INSERT INTO Users (Username, Password, Role)
            VALUES (%s, %s, 'customer')
        """, (username, password))
        db.commit()

        return None  # No error means success

    except Exception as e:
        return f"Registration error: {e}"
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def registration_window():
    """Registration window with modern styling."""
    register_window = tk.Toplevel()
    register_window.title("Register New Account")
    register_window.geometry("350x350")
    register_window.configure(bg="#f0f2f5")

    # Custom colors
    bg_color = "#f0f2f5"
    button_color = "#4a6fa5"
    button_hover = "#3a5a80"
    text_color = "#333333"
    accent_color = "#6c8fc7"

    # Main frame
    main_frame = tk.Frame(register_window, bg=bg_color)
    main_frame.pack(pady=20, padx=20, fill="both", expand=True)

    # Title
    tk.Label(main_frame, text="Register", font=("Arial", 18, "bold"),
             bg=bg_color, fg=text_color).pack(pady=(0, 15))

    # Username
    tk.Label(main_frame, text="Username", font=("Arial", 10),
             bg=bg_color, fg=text_color).pack(anchor="w", padx=10)
    username_entry = tk.Entry(main_frame, font=("Arial", 12))
    username_entry.pack(fill="x", padx=10, pady=(0, 10))

    # Password
    tk.Label(main_frame, text="Password", font=("Arial", 10),
             bg=bg_color, fg=text_color).pack(anchor="w", padx=10)
    password_entry = tk.Entry(main_frame, show="*", font=("Arial", 12))
    password_entry.pack(fill="x", padx=10, pady=(0, 10))

    # Confirm Password
    tk.Label(main_frame, text="Confirm Password", font=("Arial", 10),
             bg=bg_color, fg=text_color).pack(anchor="w", padx=10)
    confirm_password_entry = tk.Entry(main_frame, show="*", font=("Arial", 12))
    confirm_password_entry.pack(fill="x", padx=10, pady=(0, 20))

    # Register button
    register_btn = tk.Button(main_frame, text="Register", font=("Arial", 12, "bold"),
                             bg=button_color, fg="white", activebackground=button_hover,
                             activeforeground="white", bd=0, padx=20, pady=8,
                             command=lambda: perform_registration())
    register_btn.pack(fill="x", padx=10, pady=(0, 10))
    register_btn.bind("<Enter>", lambda e: register_btn.config(bg=button_hover))
    register_btn.bind("<Leave>", lambda e: register_btn.config(bg=button_color))

    # Back to login
    back_btn = tk.Button(main_frame, text="Back to Login", font=("Arial", 10),
                         bg=bg_color, fg=accent_color, activebackground=bg_color,
                         activeforeground=accent_color, bd=0,
                         command=register_window.destroy)
    back_btn.pack(pady=5)
    back_btn.bind("<Enter>", lambda e: back_btn.config(fg="#5a7db5"))
    back_btn.bind("<Leave>", lambda e: back_btn.config(fg=accent_color))

    def perform_registration():
        username = username_entry.get()
        password = password_entry.get()
        confirm_password = confirm_password_entry.get()

        error = register_user(username, password, confirm_password)
        if error:
            messagebox.showerror("Registration Error", error)
        else:
            messagebox.showinfo("Success", "Registration successful! Please login.")
            register_window.destroy()


def admin_dashboard():
    """Admin dashboard with modern styling."""
    admin_app = tk.Tk()
    admin_app.title("Admin Dashboard")
    admin_app.geometry("450x400")
    admin_app.configure(bg="#f0f2f5")

    # Custom colors
    bg_color = "#f0f2f5"
    button_color = "#4a6fa5"
    button_hover = "#3a5a80"
    text_color = "#333333"

    # Main frame
    main_frame = tk.Frame(admin_app, bg=bg_color)
    main_frame.pack(pady=30, padx=30, fill="both", expand=True)

    # Title
    tk.Label(main_frame, text="Admin Dashboard", font=("Arial", 20, "bold"),
             bg=bg_color, fg=text_color).pack(pady=(0, 30))

    # Buttons
    buttons = [
        ("View Stocks", lambda: view_stocks(admin_app)),
        ("Add Product", add_product),
        ("View Customer Orders", lambda: view_customer_orders(admin_app)),
        ("Logout", lambda: [admin_app.destroy(), login_screen()])
    ]

    for text, command in buttons:
        btn = tk.Button(main_frame, text=text, font=("Arial", 12),
                        bg=button_color, fg="white", activebackground=button_hover,
                        activeforeground="white", bd=0, padx=20, pady=10,
                        command=command)
        btn.pack(fill="x", pady=8)
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg=button_hover))
        btn.bind("<Leave>", lambda e, b=btn: b.config(bg=button_color))

    admin_app.mainloop()


def customer_dashboard(customer_id):
    """Customer dashboard with modern styling."""
    customer_app = tk.Tk()
    customer_app.title("Customer Dashboard")
    customer_app.geometry("450x400")
    customer_app.configure(bg="#f0f2f5")

    # Custom colors
    bg_color = "#f0f2f5"
    button_color = "#4a6fa5"
    button_hover = "#3a5a80"
    text_color = "#333333"

    # Main frame
    main_frame = tk.Frame(customer_app, bg=bg_color)
    main_frame.pack(pady=30, padx=30, fill="both", expand=True)

    # Title
    tk.Label(main_frame, text="Customer Dashboard", font=("Arial", 20, "bold"),
             bg=bg_color, fg=text_color).pack(pady=(0, 30))

    # Buttons
    buttons = [
        ("View Products", lambda: view_products(customer_app)),
        ("Place Order", lambda: place_order(customer_app, customer_id)),
        ("Logout", lambda: [customer_app.destroy(), login_screen()])
    ]

    for text, command in buttons:
        btn = tk.Button(main_frame, text=text, font=("Arial", 12),
                        bg=button_color, fg="white", activebackground=button_hover,
                        activeforeground="white", bd=0, padx=20, pady=10,
                        command=command)
        btn.pack(fill="x", pady=8)
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg=button_hover))
        btn.bind("<Leave>", lambda e, b=btn: b.config(bg=button_color))

    customer_app.mainloop()


# ... (keep all other functions the same)

def main():
    """Main function to start the application."""
    login_screen()


if __name__ == "__main__":
    main()