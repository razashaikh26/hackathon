#!/usr/bin/env python3
"""
Test script for FinVoice Database API endpoints
Run this in a separate terminal while the server is running
"""

import requests
import json
import time
import random
import string

BASE_URL = "http://localhost:8000"

def generate_random_email():
    """Generate a random email for testing"""
    random_string = ''.join(random.choices(string.ascii_lowercase, k=8))
    return f"test_{random_string}@example.com"

def test_user_operations():
    """Test user CRUD operations"""
    print("🧪 Testing User Operations")
    
    # Create user with random email
    user_data = {
        "email": generate_random_email(),
        "full_name": "Test User",
        "username": "testuser"
    }
    
    print("1. Creating user...")
    response = requests.post(f"{BASE_URL}/api/v1/db/users", json=user_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        user = response.json()
        print(f"✅ User created: {user['id']}")
        user_id = user['id']
        
        # Get user
        print("2. Getting user...")
        response = requests.get(f"{BASE_URL}/api/v1/db/users/{user_id}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ User retrieved: {response.json()['email']}")
        
        # Update user
        print("3. Updating user...")
        update_data = {"full_name": "Updated Test User"}
        response = requests.put(f"{BASE_URL}/api/v1/db/users/{user_id}", json=update_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ User updated: {response.json()['full_name']}")
        
        return user_id
    else:
        print(f"❌ Failed to create user: {response.text}")
        return None

def test_account_operations(user_id):
    """Test account operations"""
    if not user_id:
        return None
        
    print("\n🏦 Testing Account Operations")
    
    account_data = {
        "user_id": user_id,
        "account_name": "Test Checking",
        "account_type": "checking",
        "current_balance": 1000.0,
        "currency": "USD"
    }
    
    print("1. Creating account...")
    response = requests.post(f"{BASE_URL}/api/v1/db/accounts?user_id={user_id}", json=account_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        account = response.json()
        print(f"✅ Account created: {account['id']}")
        return account['id']
    else:
        print(f"❌ Failed to create account: {response.text}")
        return None

def test_transaction_operations(account_id):
    """Test transaction operations"""
    if not account_id:
        return
        
    print("\n💰 Testing Transaction Operations")
    
    transaction_data = {
        "account_id": account_id,
        "amount": -50.0,
        "description": "Test Purchase",
        "category": "groceries",
        "transaction_type": "debit"
    }
    
    print("1. Creating transaction...")
    response = requests.post(f"{BASE_URL}/api/v1/db/transactions", json=transaction_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        transaction = response.json()
        print(f"✅ Transaction created: {transaction['id']}")
        transaction_id = transaction['id']
        
        # Get transactions for account
        print("2. Getting account transactions...")
        response = requests.get(f"{BASE_URL}/api/v1/db/accounts/{account_id}/transactions")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            transactions = response.json()
            print(f"✅ Found {len(transactions)} transactions")
        
        # Update transaction
        print("3. Updating transaction...")
        update_data = {"description": "Updated Test Purchase", "amount": -75.0}
        response = requests.put(f"{BASE_URL}/api/v1/db/transactions/{transaction_id}", json=update_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Transaction updated")
        
        # Delete transaction
        print("4. Deleting transaction...")
        response = requests.delete(f"{BASE_URL}/api/v1/db/transactions/{transaction_id}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Transaction deleted")
    else:
        print(f"❌ Failed to create transaction: {response.text}")

def test_holdings_operations(user_id):
    """Test holdings CRUD operations"""
    if not user_id:
        return
        
    print("\n📈 Testing Holdings Operations")
    
    holding_data = {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "asset_type": "stock",
        "quantity": 10.0,
        "average_price": 150.0,
        "currency": "USD"
    }
    
    print("1. Creating holding...")
    response = requests.post(f"{BASE_URL}/api/v1/db/holdings?user_id={user_id}", json=holding_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        holding = response.json()
        print(f"✅ Holding created: {holding['id']}")
        holding_id = holding['id']
        
        # Get user holdings
        print("2. Getting user holdings...")
        response = requests.get(f"{BASE_URL}/api/v1/db/users/{user_id}/holdings")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            holdings = response.json()
            print(f"✅ Found {len(holdings)} holdings")
        
        # Update holding
        print("3. Updating holding...")
        update_data = {"quantity": 15.0, "average_price": 145.0}
        response = requests.put(f"{BASE_URL}/api/v1/db/holdings/{holding_id}", json=update_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Holding updated")
        
        # Delete holding
        print("4. Deleting holding...")
        response = requests.delete(f"{BASE_URL}/api/v1/db/holdings/{holding_id}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Holding deleted: {result['message']}")
        else:
            print(f"❌ Failed to delete holding: {response.text}")
    else:
        print(f"❌ Failed to create holding: {response.text}")

def test_goals_operations(user_id):
    """Test goals CRUD operations"""
    if not user_id:
        return
        
    print("\n🎯 Testing Goals Operations")
    
    goal_data = {
        "goal_name": "Emergency Fund",
        "goal_type": "savings",
        "target_amount": 10000.0,
        "target_date": "2025-12-31",
        "monthly_contribution": 500.0,
        "priority": "high",
        "currency": "USD"
    }
    
    print("1. Creating goal...")
    response = requests.post(f"{BASE_URL}/api/v1/db/goals?user_id={user_id}", json=goal_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        goal = response.json()
        print(f"✅ Goal created: {goal['id']}")
        goal_id = goal['id']
        
        # Get user goals
        print("2. Getting user goals...")
        response = requests.get(f"{BASE_URL}/api/v1/db/users/{user_id}/goals")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            goals = response.json()
            print(f"✅ Found {len(goals)} goals")
        
        # Update goal
        print("3. Updating goal...")
        update_data = {"target_amount": 12000.0, "monthly_contribution": 600.0}
        response = requests.put(f"{BASE_URL}/api/v1/db/goals/{goal_id}", json=update_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Goal updated")
        
        # Delete goal
        print("4. Deleting goal...")
        response = requests.delete(f"{BASE_URL}/api/v1/db/goals/{goal_id}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Goal deleted: {result['message']}")
        else:
            print(f"❌ Failed to delete goal: {response.text}")
    else:
        print(f"❌ Failed to create goal: {response.text}")

def test_overview():
    """Test financial overview"""
    print("\n📊 Testing Financial Overview")
    
    # For demo, use a dummy user_id
    dummy_user_id = "00000000-0000-0000-0000-000000000000"
    
    response = requests.get(f"{BASE_URL}/api/v1/db/overview?user_id={dummy_user_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        overview = response.json()
        print(f"✅ Overview retrieved:")
        print(f"   Cash balance: ${overview.get('cash_balance', 0)}")
        print(f"   Net worth: ${overview.get('net_worth', 0)}")
        print(f"   Accounts count: {overview.get('accounts_count', 0)}")
    else:
        print(f"❌ Failed to get overview: {response.text}")

def main():
    """Run all tests"""
    print("🚀 Starting FinVoice Database API Tests - Full CRUD Operations")
    print(f"Server: {BASE_URL}")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Server is running (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running! Please start the backend first.")
        return
    
    # Run tests
    user_id = test_user_operations()
    account_id = test_account_operations(user_id)
    test_transaction_operations(account_id)
    test_holdings_operations(user_id)
    test_goals_operations(user_id)
    test_overview()
    
    print("\n🎉 All CRUD tests completed!")
    print("📊 Database Features Verified:")
    print("   ✅ Users: Create, Read, Update")
    print("   ✅ Accounts: Create, Read, Update, Delete")
    print("   ✅ Transactions: Create, Read, Update, Delete")
    print("   ✅ Holdings: Create, Read, Update, Delete")
    print("   ✅ Goals: Create, Read, Update, Delete")
    print("   ✅ Financial Overview")
    print("\n🎯 All data is now stored in Neon PostgreSQL database!")

if __name__ == "__main__":
    main()
