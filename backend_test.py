#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Shaomacao.com P2P Offsetting Platform
Tests all core functionality including user registration, transactions, matching, chat, ratings, and admin features.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

# Backend URL from frontend .env
BASE_URL = "https://8f9ee9ec-038b-4e63-84a3-0e79befb5ce6.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.test_users = []
        self.test_transactions = []
        self.test_matches = []
        self.test_messages = []
        self.test_ratings = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def make_request(self, method: str, endpoint: str, data: dict = None, params: dict = None) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, params=params, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, params=params, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, params=params, timeout=10)
            else:
                return False, f"Unsupported method: {method}", 400
                
            if response.status_code < 400:
                try:
                    return True, response.json(), response.status_code
                except:
                    return True, response.text, response.status_code
            else:
                try:
                    error_data = response.json()
                    return False, error_data, response.status_code
                except:
                    return False, response.text, response.status_code
                    
        except requests.exceptions.RequestException as e:
            return False, f"Request failed: {str(e)}", 500

    def test_cities_management(self) -> bool:
        """Test Cities Management System"""
        self.log("=== Testing Cities Management ===")
        
        # Test GET /api/cities
        success, data, status = self.make_request("GET", "/cities")
        if not success:
            self.log(f"FAIL: GET /cities failed - {data}", "ERROR")
            return False
            
        if "cities" not in data:
            self.log("FAIL: Cities response missing 'cities' key", "ERROR")
            return False
            
        cities = data["cities"]
        if not isinstance(cities, list) or len(cities) < 50:
            self.log(f"FAIL: Expected major cities list, got {len(cities) if isinstance(cities, list) else 'non-list'}", "ERROR")
            return False
            
        # Check for major cities
        expected_cities = ["New York", "London", "Tokyo", "Paris", "Berlin"]
        missing_cities = [city for city in expected_cities if city not in cities]
        if missing_cities:
            self.log(f"FAIL: Missing expected cities: {missing_cities}", "ERROR")
            return False
            
        self.log(f"PASS: Cities management working - {len(cities)} cities available")
        return True

    def test_user_registration(self) -> bool:
        """Test User Registration System"""
        self.log("=== Testing User Registration System ===")
        
        # Test user creation
        user1_data = {
            "username": "alice_trader",
            "email": "alice@example.com", 
            "phone": "+1-555-0101",
            "id_document": "US-DL-123456789",
            "city": "New York"
        }
        
        user2_data = {
            "username": "bob_exchanger",
            "email": "bob@example.com",
            "phone": "+44-20-7946-0958", 
            "id_document": "UK-PP-987654321",
            "city": "London"
        }
        
        # Create first user
        success, user1, status = self.make_request("POST", "/users", user1_data)
        if not success:
            self.log(f"FAIL: User creation failed - {user1}", "ERROR")
            return False
            
        if not all(key in user1 for key in ["id", "username", "email", "city", "rating"]):
            self.log("FAIL: User response missing required fields", "ERROR")
            return False
            
        self.test_users.append(user1)
        self.log(f"PASS: Created user {user1['username']} with ID {user1['id']}")
        
        # Create second user
        success, user2, status = self.make_request("POST", "/users", user2_data)
        if not success:
            self.log(f"FAIL: Second user creation failed - {user2}", "ERROR")
            return False
            
        self.test_users.append(user2)
        self.log(f"PASS: Created user {user2['username']} with ID {user2['id']}")
        
        # Test duplicate username validation
        duplicate_data = user1_data.copy()
        duplicate_data["email"] = "different@example.com"
        success, error, status = self.make_request("POST", "/users", duplicate_data)
        if success:
            self.log("FAIL: Duplicate username should be rejected", "ERROR")
            return False
        self.log("PASS: Duplicate username properly rejected")
        
        # Test duplicate email validation
        duplicate_data = user2_data.copy()
        duplicate_data["username"] = "different_user"
        success, error, status = self.make_request("POST", "/users", duplicate_data)
        if success:
            self.log("FAIL: Duplicate email should be rejected", "ERROR")
            return False
        self.log("PASS: Duplicate email properly rejected")
        
        # Test GET user by ID
        success, retrieved_user, status = self.make_request("GET", f"/users/{user1['id']}")
        if not success or retrieved_user["id"] != user1["id"]:
            self.log(f"FAIL: GET user by ID failed - {retrieved_user}", "ERROR")
            return False
        self.log("PASS: GET user by ID working")
        
        # Test GET all users
        success, users_list, status = self.make_request("GET", "/users")
        if not success or len(users_list) < 2:
            self.log(f"FAIL: GET all users failed - {users_list}", "ERROR")
            return False
        self.log(f"PASS: GET all users working - {len(users_list)} users found")
        
        return True

    def test_transaction_system(self) -> bool:
        """Test Transaction Posting System"""
        self.log("=== Testing Transaction System ===")
        
        if len(self.test_users) < 2:
            self.log("FAIL: Need at least 2 users for transaction testing", "ERROR")
            return False
            
        # Create transaction from NYC to London
        tx1_data = {
            "title": "Send money to London for business",
            "description": "Need to transfer $5000 to London for business expenses",
            "amount": 5000.0,
            "currency": "USD",
            "from_city": "New York",
            "to_city": "London", 
            "recipient_name": "John Smith",
            "recipient_details": "Account: UK-BANK-123456, Sort: 12-34-56"
        }
        
        # Create transaction from London to NYC (offsetting)
        tx2_data = {
            "title": "Transfer funds to New York",
            "description": "Need to send £4000 to NYC for investment",
            "amount": 4000.0,
            "currency": "GBP",
            "from_city": "London",
            "to_city": "New York",
            "recipient_name": "Sarah Johnson", 
            "recipient_details": "Account: US-BANK-789012, Routing: 021000021"
        }
        
        # Create first transaction
        success, tx1, status = self.make_request("POST", "/transactions", tx1_data, {"user_id": self.test_users[0]["id"]})
        if not success:
            self.log(f"FAIL: Transaction creation failed - {tx1}", "ERROR")
            return False
            
        required_fields = ["id", "user_id", "title", "amount", "from_city", "to_city", "status"]
        if not all(key in tx1 for key in required_fields):
            self.log("FAIL: Transaction response missing required fields", "ERROR")
            return False
            
        if tx1["status"] != "active":
            self.log(f"FAIL: New transaction should have 'active' status, got '{tx1['status']}'", "ERROR")
            return False
            
        self.test_transactions.append(tx1)
        self.log(f"PASS: Created transaction {tx1['id']} - {tx1['from_city']} to {tx1['to_city']}")
        
        # Create second transaction (offsetting)
        success, tx2, status = self.make_request("POST", "/transactions", tx2_data, {"user_id": self.test_users[1]["id"]})
        if not success:
            self.log(f"FAIL: Second transaction creation failed - {tx2}", "ERROR")
            return False
            
        self.test_transactions.append(tx2)
        self.log(f"PASS: Created offsetting transaction {tx2['id']} - {tx2['from_city']} to {tx2['to_city']}")
        
        # Test GET transactions
        success, all_transactions, status = self.make_request("GET", "/transactions")
        if not success or len(all_transactions) < 2:
            self.log(f"FAIL: GET all transactions failed - {all_transactions}", "ERROR")
            return False
        self.log(f"PASS: GET all transactions working - {len(all_transactions)} transactions found")
        
        # Test GET transactions by city filter
        success, nyc_transactions, status = self.make_request("GET", "/transactions", params={"city": "New York"})
        if not success:
            self.log(f"FAIL: GET transactions by city failed - {nyc_transactions}", "ERROR")
            return False
        self.log(f"PASS: GET transactions by city filter working - {len(nyc_transactions)} NYC transactions")
        
        # Test GET transactions by status filter
        success, active_transactions, status = self.make_request("GET", "/transactions", params={"status": "active"})
        if not success:
            self.log(f"FAIL: GET transactions by status failed - {active_transactions}", "ERROR")
            return False
        self.log(f"PASS: GET transactions by status filter working - {len(active_transactions)} active transactions")
        
        # Test GET user transactions
        success, user_transactions, status = self.make_request("GET", f"/transactions/user/{self.test_users[0]['id']}")
        if not success or len(user_transactions) < 1:
            self.log(f"FAIL: GET user transactions failed - {user_transactions}", "ERROR")
            return False
        self.log(f"PASS: GET user transactions working - {len(user_transactions)} transactions for user")
        
        # Test GET single transaction
        success, single_tx, status = self.make_request("GET", f"/transactions/{tx1['id']}")
        if not success or single_tx["id"] != tx1["id"]:
            self.log(f"FAIL: GET single transaction failed - {single_tx}", "ERROR")
            return False
        self.log("PASS: GET single transaction working")
        
        return True

    def test_matching_system(self) -> bool:
        """Test Counterparty Matching System (Core Feature)"""
        self.log("=== Testing Counterparty Matching System ===")
        
        if len(self.test_transactions) < 2:
            self.log("FAIL: Need at least 2 transactions for matching testing", "ERROR")
            return False
            
        tx1 = self.test_transactions[0]  # NYC -> London
        tx2 = self.test_transactions[1]  # London -> NYC
        
        # Test finding matches for first transaction
        success, matches, status = self.make_request("GET", f"/transactions/{tx1['id']}/matches")
        if not success:
            self.log(f"FAIL: Find matches failed - {matches}", "ERROR")
            return False
            
        if len(matches) == 0:
            self.log("FAIL: Should find at least one match (offsetting transaction)", "ERROR")
            return False
            
        # Verify the match is the offsetting transaction
        match_found = False
        for match in matches:
            if (match["from_city"] == tx1["to_city"] and 
                match["to_city"] == tx1["from_city"] and
                match["id"] == tx2["id"]):
                match_found = True
                break
                
        if not match_found:
            self.log("FAIL: Matching algorithm not finding correct offsetting transaction", "ERROR")
            return False
            
        self.log(f"PASS: Matching system found {len(matches)} potential matches")
        
        # Test creating a match
        match_tx = matches[0]
        success, match_result, status = self.make_request("POST", f"/transactions/{tx1['id']}/match/{match_tx['id']}", 
                                                         params={"user_id": self.test_users[1]["id"]})
        if not success:
            self.log(f"FAIL: Create match failed - {match_result}", "ERROR")
            return False
            
        self.log("PASS: Match creation successful")
        
        # Verify both transactions are now matched
        success, updated_tx1, status = self.make_request("GET", f"/transactions/{tx1['id']}")
        if not success or updated_tx1["status"] != "matched":
            self.log(f"FAIL: First transaction not updated to matched status - {updated_tx1}", "ERROR")
            return False
            
        success, updated_tx2, status = self.make_request("GET", f"/transactions/{tx2['id']}")
        if not success or updated_tx2["status"] != "matched":
            self.log(f"FAIL: Second transaction not updated to matched status - {updated_tx2}", "ERROR")
            return False
            
        if (updated_tx1["matched_transaction_id"] != tx2["id"] or 
            updated_tx2["matched_transaction_id"] != tx1["id"]):
            self.log("FAIL: Matched transaction IDs not properly linked", "ERROR")
            return False
            
        self.log("PASS: Both transactions properly matched with correct status and links")
        
        # Store match info for later tests
        self.test_matches.append({
            "tx1": updated_tx1,
            "tx2": updated_tx2,
            "user1": self.test_users[0],
            "user2": self.test_users[1]
        })
        
        return True

    def test_chat_system(self) -> bool:
        """Test Private Chat System"""
        self.log("=== Testing Private Chat System ===")
        
        if len(self.test_matches) == 0:
            self.log("FAIL: Need matched transactions for chat testing", "ERROR")
            return False
            
        match_info = self.test_matches[0]
        tx1 = match_info["tx1"]
        user1 = match_info["user1"]
        user2 = match_info["user2"]
        
        # Test sending messages
        message1_data = {
            "transaction_id": tx1["id"],
            "receiver_id": user2["id"],
            "message": "Hi! I see we have a match. Let's coordinate the transfer details."
        }
        
        success, msg1, status = self.make_request("POST", "/chat", message1_data, {"sender_id": user1["id"]})
        if not success:
            self.log(f"FAIL: Send message failed - {msg1}", "ERROR")
            return False
            
        required_fields = ["id", "transaction_id", "sender_id", "receiver_id", "message", "timestamp"]
        if not all(key in msg1 for key in required_fields):
            self.log("FAIL: Chat message response missing required fields", "ERROR")
            return False
            
        self.test_messages.append(msg1)
        self.log(f"PASS: Message sent successfully - ID: {msg1['id']}")
        
        # Send reply message
        message2_data = {
            "transaction_id": tx1["id"],
            "receiver_id": user1["id"],
            "message": "Great! I can transfer the funds tomorrow. What's your preferred timing?"
        }
        
        success, msg2, status = self.make_request("POST", "/chat", message2_data, {"sender_id": user2["id"]})
        if not success:
            self.log(f"FAIL: Send reply message failed - {msg2}", "ERROR")
            return False
            
        self.test_messages.append(msg2)
        self.log(f"PASS: Reply message sent successfully - ID: {msg2['id']}")
        
        # Test retrieving chat history
        success, chat_history, status = self.make_request("GET", f"/chat/{tx1['id']}")
        if not success:
            self.log(f"FAIL: Get chat history failed - {chat_history}", "ERROR")
            return False
            
        if len(chat_history) < 2:
            self.log(f"FAIL: Expected at least 2 messages, got {len(chat_history)}", "ERROR")
            return False
            
        # Verify messages are in chronological order
        timestamps = [msg["timestamp"] for msg in chat_history]
        if timestamps != sorted(timestamps):
            self.log("FAIL: Chat messages not in chronological order", "ERROR")
            return False
            
        self.log(f"PASS: Chat history retrieved successfully - {len(chat_history)} messages")
        
        # Verify message content
        found_messages = 0
        for msg in chat_history:
            if msg["message"] in [message1_data["message"], message2_data["message"]]:
                found_messages += 1
                
        if found_messages < 2:
            self.log("FAIL: Not all sent messages found in chat history", "ERROR")
            return False
            
        self.log("PASS: All sent messages properly stored and retrieved")
        return True

    def test_admin_system(self) -> bool:
        """Test Admin Moderation System"""
        self.log("=== Testing Admin Moderation System ===")
        
        if len(self.test_matches) == 0:
            self.log("FAIL: Need matched transactions for admin testing", "ERROR")
            return False
            
        match_info = self.test_matches[0]
        tx1 = match_info["tx1"]
        tx2 = match_info["tx2"]
        
        # Test request approval
        success, approval_result, status = self.make_request("POST", "/admin/request-approval", 
                                                           params={"transaction_id": tx1["id"], "match_id": tx2["id"]})
        if not success:
            self.log(f"FAIL: Request approval failed - {approval_result}", "ERROR")
            return False
            
        self.log("PASS: Approval request submitted successfully")
        
        # Verify both transactions are now pending approval
        success, pending_tx1, status = self.make_request("GET", f"/transactions/{tx1['id']}")
        if not success or pending_tx1["status"] != "pending_approval":
            self.log(f"FAIL: Transaction 1 not updated to pending_approval status - {pending_tx1}", "ERROR")
            return False
            
        success, pending_tx2, status = self.make_request("GET", f"/transactions/{tx2['id']}")
        if not success or pending_tx2["status"] != "pending_approval":
            self.log(f"FAIL: Transaction 2 not updated to pending_approval status - {pending_tx2}", "ERROR")
            return False
            
        self.log("PASS: Both transactions updated to pending_approval status")
        
        # Create a moderator user for approval testing
        moderator_data = {
            "username": "admin_moderator",
            "email": "admin@shaomacao.com",
            "phone": "+1-555-ADMIN",
            "id_document": "ADMIN-ID-001",
            "city": "New York"
        }
        
        success, moderator, status = self.make_request("POST", "/users", moderator_data)
        if not success:
            self.log(f"FAIL: Moderator creation failed - {moderator}", "ERROR")
            return False
            
        # Note: In a real system, we'd need to update the user's role to moderator
        # For testing purposes, we'll test the approval endpoint with a non-moderator
        # to verify access control, then note that role assignment would be needed
        
        # Test approval with non-moderator (should fail)
        success, approval_error, status = self.make_request("POST", f"/admin/approve/{tx1['id']}", 
                                                          params={"moderator_id": self.test_users[0]["id"]})
        if success:
            self.log("FAIL: Non-moderator should not be able to approve transactions", "ERROR")
            return False
            
        if status != 403:
            self.log(f"FAIL: Expected 403 Forbidden for non-moderator, got {status}", "ERROR")
            return False
            
        self.log("PASS: Access control working - non-moderators cannot approve")
        
        # Note: To fully test approval, we'd need to manually update the moderator's role in the database
        # or have an endpoint to promote users to moderator status
        self.log("NOTE: Full approval testing requires moderator role assignment functionality")
        
        return True

    def test_rating_system(self) -> bool:
        """Test User Rating System"""
        self.log("=== Testing User Rating System ===")
        
        if len(self.test_users) < 2:
            self.log("FAIL: Need at least 2 users for rating testing", "ERROR")
            return False
            
        if len(self.test_transactions) < 2:
            self.log("FAIL: Need transactions for rating testing", "ERROR")
            return False
            
        user1 = self.test_users[0]
        user2 = self.test_users[1]
        tx1 = self.test_transactions[0]
        
        # Test creating a rating
        rating_data = {
            "rated_user_id": user2["id"],
            "transaction_id": tx1["id"],
            "rating": 5,
            "comment": "Excellent communication and fast transfer. Highly recommended!"
        }
        
        success, rating, status = self.make_request("POST", "/ratings", rating_data, {"rater_id": user1["id"]})
        if not success:
            self.log(f"FAIL: Create rating failed - {rating}", "ERROR")
            return False
            
        required_fields = ["id", "rater_id", "rated_user_id", "transaction_id", "rating", "comment"]
        if not all(key in rating for key in required_fields):
            self.log("FAIL: Rating response missing required fields", "ERROR")
            return False
            
        if rating["rating"] != 5:
            self.log(f"FAIL: Rating value incorrect - expected 5, got {rating['rating']}", "ERROR")
            return False
            
        self.test_ratings.append(rating)
        self.log(f"PASS: Rating created successfully - ID: {rating['id']}, Rating: {rating['rating']}/5")
        
        # Create another rating for the same user
        rating2_data = {
            "rated_user_id": user2["id"],
            "transaction_id": tx1["id"],
            "rating": 4,
            "comment": "Good service, minor delay but overall satisfied."
        }
        
        success, rating2, status = self.make_request("POST", "/ratings", rating2_data, {"rater_id": user1["id"]})
        if not success:
            self.log(f"FAIL: Create second rating failed - {rating2}", "ERROR")
            return False
            
        self.test_ratings.append(rating2)
        self.log(f"PASS: Second rating created - Rating: {rating2['rating']}/5")
        
        # Test retrieving user ratings
        success, user_ratings, status = self.make_request("GET", f"/ratings/{user2['id']}")
        if not success:
            self.log(f"FAIL: Get user ratings failed - {user_ratings}", "ERROR")
            return False
            
        if len(user_ratings) < 2:
            self.log(f"FAIL: Expected at least 2 ratings, got {len(user_ratings)}", "ERROR")
            return False
            
        self.log(f"PASS: Retrieved {len(user_ratings)} ratings for user")
        
        # Verify average rating calculation
        success, updated_user, status = self.make_request("GET", f"/users/{user2['id']}")
        if not success:
            self.log(f"FAIL: Get updated user failed - {updated_user}", "ERROR")
            return False
            
        expected_avg = (5 + 4) / 2  # 4.5
        if abs(updated_user["rating"] - expected_avg) > 0.1:
            self.log(f"FAIL: Average rating calculation incorrect - expected ~{expected_avg}, got {updated_user['rating']}", "ERROR")
            return False
            
        self.log(f"PASS: Average rating calculation working - User rating: {updated_user['rating']}")
        
        return True

    def run_comprehensive_test(self) -> Dict[str, bool]:
        """Run all backend tests and return results"""
        self.log("🚀 Starting Comprehensive Backend Testing for Shaomacao.com")
        self.log(f"Testing against: {self.base_url}")
        
        results = {}
        
        # Test in logical order
        test_functions = [
            ("Cities Management", self.test_cities_management),
            ("User Registration System", self.test_user_registration),
            ("Transaction Posting System", self.test_transaction_system),
            ("Counterparty Matching System", self.test_matching_system),
            ("Private Chat System", self.test_chat_system),
            ("Admin Moderation System", self.test_admin_system),
            ("User Rating System", self.test_rating_system),
        ]
        
        for test_name, test_function in test_functions:
            self.log(f"\n{'='*60}")
            try:
                results[test_name] = test_function()
                if results[test_name]:
                    self.log(f"✅ {test_name}: PASSED")
                else:
                    self.log(f"❌ {test_name}: FAILED")
            except Exception as e:
                self.log(f"❌ {test_name}: ERROR - {str(e)}", "ERROR")
                results[test_name] = False
            
            time.sleep(1)  # Brief pause between tests
        
        return results

    def print_summary(self, results: Dict[str, bool]):
        """Print test summary"""
        self.log(f"\n{'='*60}")
        self.log("🏁 BACKEND TESTING SUMMARY")
        self.log(f"{'='*60}")
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{status}: {test_name}")
        
        self.log(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            self.log("🎉 ALL TESTS PASSED! Backend is fully functional.")
        else:
            failed_tests = [name for name, result in results.items() if not result]
            self.log(f"⚠️  Failed tests: {', '.join(failed_tests)}")

if __name__ == "__main__":
    tester = BackendTester()
    results = tester.run_comprehensive_test()
    tester.print_summary(results)