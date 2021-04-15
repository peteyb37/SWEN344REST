import unittest
import json
import hashlib
from tests.test_utils import *
import src.db.bechdel_db as bechdel

class TestBechdel(unittest.TestCase):

    def setUp(self):
        bechdel.rebuild_tables()
        bechdel.build_movie_table()
        

    #REST1 Test Methods
    def test_bechdel_list_all_keys(self):
        """Ensures list_all_keys returns the correct size and contains the ID 4648786"""
        expected = 8363
        actual = get_rest_call(self, 'http://localhost:5000/list_all_keys')
        actual_size = len(actual)
        self.assertEqual(expected, actual_size)

        does_value_exist = 0

        if 4648786 in actual.values():
            does_value_exist = 1
        self.assertEqual(1, does_value_exist)


    def test_bechdel_list_details_equal_to_list_all_keys(self):
        """Tests that list_details returns the same number of entries as list_all_keys"""
        details = get_rest_call(self, 'http://localhost:5000/list_details')
        details_size = len(details)

        all_keys = get_rest_call(self, 'http://localhost:5000/list_all_keys')
        all_keys_size = len(all_keys)

        self.assertEqual(details_size, all_keys_size)

    
    def test_bechdel_list_all_details(self):
        """Tests that list_details returns correct details"""
        details = get_rest_call(self, 'http://localhost:5000/list_details')

        result_row = []

        for row in details:
            if all(x in row for x in ['Harriet', 3, 2019, 4648786]):
                result_row = row               

        self.assertEqual(result_row, [8892, 4648786, 3, 'Harriet', 2019])


    def test_bechdel_show(self):
        """Tests that show() returns details about a specific row"""
        results = get_rest_call(self, 'http://localhost:5000/show', params={"id" : 8892})

        self.assertEqual(results, [[8892, 4648786, 3, 'Harriet', 2019]])




    #REST2 Test Methods

    #Login Test Cases
    def test_bechdel_create_new_user(self):
        """
        Create New User Account
        Results:
            Validates that user account has been created        
        """
        post_rest_call(self, 'http://localhost:5000/register', params={"username" : "testuser", "passw" : "testpassword"})
        conn = connect()
        cur = conn.cursor()
        cur.execute("""SELECT * FROM system_users WHERE username = 'testuser'""")
        self.assertNotEqual(cur.fetchall(), [])
        conn.close()
    
    def test_login_non_existent(self):
        """
        Try to login with a non-existent account
        Results:
            Login should return invalid
        """
        results = post_rest_call(self, 'http://localhost:5000/login', params={"username" : "Idontexist", "passw" : "Idontexisteither"})
        self.assertEqual(results[1], 'Login invalid')

    def test_bechdel_login_invalid_pass(self):
        """
        Try to login with a valid user but an invalid password
        Results:
            Login should return invalid
        """
        results = post_rest_call(self, 'http://localhost:5000/login', params={"username" : "blorg", "passw" : "thisisnttherightpassword"})
        self.assertEqual(results[1], 'Login invalid')

    def test_bechdel_login_blorg(self):
        """
        Step 1:
        Ensure that user blorg exists with hashed password
        Results:
            Validates that user blorg exists and that the password is not in plain text
        """
        conn = connect()
        cur = conn.cursor()
        cur.execute("""SELECT * FROM system_users WHERE username = 'blorg'""")
        result = cur.fetchall()
        self.assertNotEqual(result, [])
        actual_result = result[0]
        self.assertNotEqual(actual_result[1], 'saltfatacidheat')
        conn.close()
        
        """
        Step 2:
        Login as user blorg 
        Results:
            Validates that user received successful login message
        """
        results = post_rest_call(self, 'http://localhost:5000/login', params={"username" : "blorg", "passw" : "saltfatacidheat"})
        self.assertEqual(results[1], 'Login was successful')

        """
        Step 3:
        Ensure that user got a session key
        Results:
            Validates that session key received is the same as session key stored by server
        """
        conn = connect()
        cur = conn.cursor()
        cur.execute("""SELECT * FROM system_users WHERE username = 'blorg'""")
        result = cur.fetchall()
        actual_result = result[0]
        conn.close()
        self.assertEqual(results[0], actual_result[2])

    def test_bechdel_nobody_logged_in(self):
        """
        With nobody logged into the system, an HTTP request makes an attempt to delete a movie
        from the database, but the action does not occur because no one is logged in.
        Pre-Condition:
            Nobody is logged in upon setup
            Safe Delete happens because the method itself uses the primary key to delete the movie
        Results:
            Nothing happens
        """
        delete_rest_call(self, 'http://localhost:5000/user', params={"title" : "Resident Evil: Extinction"})

        results = get_rest_call(self, 'http://localhost:5000/list_details')
        result_row = []
        for row in results:
            if all(x in row for x in ['Resident Evil: Extinction']):
                result_row = row   
        self.assertEqual(result_row, [17, 432021, 3, 'Resident Evil: Extinction', 2007])

    def test_bechdel_delete_movie(self):
        """
        Similar to the above case, but this time, somebody logs in and deletes a movie
        Results:
            Movie is deleted from the database
        """

        """Login as blorg"""
        post_rest_call(self, 'http://localhost:5000/login', params={"username" : "blorg", "passw" : "saltfatacidheat"})
        
        """First we check that the movie exists"""
        results = get_rest_call(self, 'http://localhost:5000/list_details')
        result_row = []
        for row in results:
            if all(x in row for x in ['Resident Evil: Extinction']):
                result_row = row   
        self.assertEqual(result_row, [17, 432021, 3, 'Resident Evil: Extinction', 2007])

        """Delete the movie"""
        delete_rest_call(self, 'http://localhost:5000/user', params={"title" : "Resident Evil: Extinction"})

        """Check to ensure that the movie no longer exists with the same check as above"""
        results = get_rest_call(self, 'http://localhost:5000/list_details')
        result_row = []
        for row in results:
            if all(x in row for x in ['Resident Evil: Extinction']):
                result_row = row   
        self.assertEqual(result_row, [])

    #Logout Test Case
    def test_bechdel_logout(self):
        """
        Tests that a user can successfully logout and once logged out will no longer be able to run CRUD operations
        Results:
            Delete method does nothing
        """

        """Login as blorg"""
        post_rest_call(self, 'http://localhost:5000/login', params={"username" : "blorg", "passw" : "saltfatacidheat"})

        """Logout of user blorg's account"""
        post_rest_call(self, 'http://localhost:5000/logout')

        """Attempt to perform delete action"""
        delete_rest_call(self, 'http://localhost:5000/user', params={"title" : "Resident Evil: Extinction"})

        """Ensure record was not deleted"""
        results = get_rest_call(self, 'http://localhost:5000/list_details')
        result_row = []
        for row in results:
            if all(x in row for x in ['Resident Evil: Extinction']):
                result_row = row   
        self.assertEqual(result_row, [17, 432021, 3, 'Resident Evil: Extinction', 2007])

    #Unauthenticated Logout
    def test_bechdel_unauth_logout(self):
        """
        Attempt to logout without the session key
        Results:
            No user is logged out
        """

        """Login as blorg"""
        post_rest_call(self, 'http://localhost:5000/login', params={"username" : "blorg", "passw" : "saltfatacidheat"})

        """Attempt to logout without a session key"""
        bechdel.logout('')

        """Verify that user is still logged in"""
        conn = connect()
        cur = conn.cursor()
        cur.execute("""SELECT * FROM system_users WHERE username = 'blorg'""")
        result = cur.fetchall()
        actual_result = result[0]
        conn.close()
        self.assertNotEqual(actual_result[2], None)

    def test_bechdel_logout_when_not_logged_in(self):
        """
        Try to logout a user who is not logged in
        Results:
            This test is impossible because username and password are not used in the logout method.
            Only the session key is used in the logout method, therefore ensuring that only the user
            itself can be the one to log out with their specific session key.  If the user is not
            logged in in the first place, there is no possible way to log them out (without an admin
            deleting the user's session key from the database (which can't exist without being logged
            in in the first place)).
        """
        pass

    #A new movie
    def test_bechdel_add_movie(self):
        """
        Create a new movie that passes the Bechdel Test
        Results:
            A movie has been created and added to the database
        """

        """Login as user blorg"""
        post_rest_call(self, 'http://localhost:5000/login', params={"username" : "blorg", "passw" : "saltfatacidheat"})

        """Verify that movie doesn't already exist"""
        results = get_rest_call(self, 'http://localhost:5000/list_details')
        result_row = []
        for row in results:
            if all(x in row for x in ['2 Fast 2 Covid']):
                result_row = row   
        self.assertEqual(result_row, [])

        """Create movie"""
        post_rest_call(self, 'http://localhost:5000/user', params={"title" : "2 Fast 2 Covid", "rating" : "3", "year" : "2021"})

        """Verify that movie now exists"""
        results = get_rest_call(self, 'http://localhost:5000/list_details')
        result_row = []
        for row in results:
            if all(x in row for x in ['2 Fast 2 Covid']):
                result_row = row[2:]   
        self.assertEqual(result_row, [3, '2 Fast 2 Covid', 2021])

    #An Update to a rating
    def test_bechdel_update_rating(self):
        """
        Updates the rating for a movie
        Results:
            Verifies that rating for movie 'Speedy' has gone from 0 to 1
        """

        """Check original Rating"""
        results = get_rest_call(self, 'http://localhost:5000/list_details')
        result_row = []
        for row in results:
            if all(x in row for x in ['Speedy']):
                result_row = row[2]   
        self.assertEqual(result_row, 0)

        """Login as user blorg"""
        post_rest_call(self, 'http://localhost:5000/login', params={"username" : "blorg", "passw" : "saltfatacidheat"})

        """Update Rating"""
        post_rest_call(self, 'http://localhost:5000/update_rating', params={"title" : "Speedy", "rating" : "1"})

        """Verify Rating is now 1"""
        results = get_rest_call(self, 'http://localhost:5000/list_details')
        result_row = []
        for row in results:
            if all(x in row for x in ['Speedy']):
                result_row = row[2]   
        self.assertEqual(result_row, 1)


