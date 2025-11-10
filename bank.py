import sqlite3
import random
import time
from datetime import datetime, timedelta

conn = sqlite3.connect("bank_sim.db")
cur = conn.cursor()

def setup_database():
    cur.execute("DROP TABLE IF EXISTS customers")
    
    cur.execute("""
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        CreditScore INTEGER,
        Age INTEGER,
        Tenure INTEGER,
        Balance REAL,
        NumOfProducts INTEGER,
        HasCrCard INTEGER,
        IsActiveMember INTEGER,
        EstimatedSalary REAL,
        Geography TEXT,
        Gender TEXT,
        churn_day TEXT,         -- hidden ground truth
        churned INTEGER DEFAULT 0
    )
    """)
    conn.commit()

def add_customer(name):
    cs = random.randint(350, 850)
    age = random.randint(18, 70)
    tenure = random.randint(0, 10)
    balance = random.randint(0, 250000)
    products = random.randint(1, 4)
    card = random.choice([0, 1])
    active = random.choice([0, 1])
    salary = random.randint(20000, 150000)
    geo = random.choice(["Germany", "Spain", "France"])
    gender = random.choice(["Male", "Female"])
    
    churn_gap = random.randint(1, 10)
    churn_time = (datetime.now() + timedelta(minutes=churn_gap)).isoformat()
    
    cur.execute("""
    INSERT INTO customers (name, CreditScore, Age, Tenure, Balance, NumOfProducts,
                           HasCrCard, IsActiveMember, EstimatedSalary, Geography, Gender, churn_day)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, cs, age, tenure, balance, products, card, active, salary, geo, gender, churn_time))
    conn.commit()

def update_customers():
    cur.execute("SELECT * FROM customers WHERE churned=0")
    rows = cur.fetchall()
    for row in rows:
        cid = row[0]
        balance = max(0, row[5] + random.randint(-2000, 5000))
        tenure = row[4] + 1
        active = row[7] if random.random() > 0.1 else 1 - row[7]
        cs = max(300, min(850, row[2] + random.randint(-10, 10)))
        
        # Check if churn_time has passed → mark churned
        churn_time = datetime.fromisoformat(row[12])
        if datetime.now() >= churn_time:
            cur.execute("UPDATE customers SET churned=1 WHERE id=?", (cid,))
            print(f"Customer {row[1]} has churned!")
        else:
            cur.execute("""
            UPDATE customers
            SET Balance=?, Tenure=?, IsActiveMember=?, CreditScore=?
            WHERE id=?
            """, (balance, tenure, active, cs, cid))
    conn.commit()

def display_stats():
    cur.execute("SELECT COUNT(*) FROM customers")
    total = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM customers WHERE churned=1")
    churned = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM customers WHERE churned=0")
    active = cur.fetchone()[0]
    
    print(f"Total Customers: {total}, Active: {active}, Churned: {churned}")

def run_simulation():
    setup_database()
    
    print("Creating 15 initial customers...")
    for i in range(15):
        add_customer(f"Customer_{i+1}")
    
    print("Initial setup complete. Starting simulation...")
    
    iteration = 0
    while True:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")
        update_customers()
        display_stats()
        print("Last update at:", datetime.now())
        time.sleep(10)  

run_simulation()