import unittest
from src.db.bechdel_db import *
from src.db.swen344_db_utils import connect
from tests.test_utils import *

class TestDBSchema(unittest.TestCase):

    def test_rebuild_tables(self):
        """Rebuild the tables"""
        rebuild_tables()
        assert_sql_count(self, "SELECT * FROM movies", 0)

    def test_rebuild_tables_is_idempotent(self):
        """Drop and rebuild the tables twice"""
        rebuild_tables()
        rebuild_tables()
        assert_sql_count(self, "SELECT * FROM movies", 0)

    def test_seed_data_works(self):
        """Attempt to insert the seed data"""
        rebuild_tables()
        build_movie_table()
        assert_sql_count(self, "SELECT * FROM movies", 8363)

    def test_list_all_keys(self):
        """Tests list_all_keys method"""
        rebuild_tables()
        build_movie_table()

        result = list_all_keys()
        size_result = len(result)
        self.assertEqual(size_result, 8363, "Incorrect number of entries")

        does_result_contain_IMDBID = 0

        for row in result:
            if row[1] == 4648786 or row[1] == 'tt4648786':
                does_result_contain_IMDBID = 1
        
        self.assertEqual(does_result_contain_IMDBID, 1, "list_all_keys does not contain 4648786")

    def test_list_details_equal_to_list_all_keys(self):
        """Tests that list_details returns the same number of entries as list_all_keys"""
        rebuild_tables()
        build_movie_table()

        result_details = list_details()
        size_result_details = len(result_details)

        result_list_all = list_all_keys()
        size_result_list_all = len(result_list_all)

        self.assertEqual(size_result_details, size_result_list_all, "Number of entries does not match list_all_keys method")

    def test_list_details(self):
        """Tests that list_details returns correct details"""
        rebuild_tables()
        build_movie_table()
        
        result_row = []

        result = list_details()
        for row in result:
            if all(x in row for x in ['Harriet', 3, 2019, 4648786]):
                result_row = row

        self.assertEqual(result_row, (8892, 4648786, 3, 'Harriet', 2019), "Entry does not exist")
    
    def test_show(self):
        """Tests that show() returns details about a specific row"""
        rebuild_tables()
        build_movie_table()
        
        result = show('8892')
        
        self.assertEqual(result, [(8892, 4648786, 3, 'Harriet', 2019)], "Could not find details about id 8892")




    # All of the test cases for Rest2 are in api/test_bechdel.py
    # ====================================================================================================
    # This file is now where I will test the server functions themselves to ensure they do what they are 
    # supposed to when writing them.  I decided to do this because I created helper functions as well
    # as primary functions that all need to be tested throughout use. Not every single edge case
    # has been explored, but the ones that I feel needed to be tested were.


    def test_create_and_delete_user(self):
        """Attempt to create a user and delete that user"""
        rebuild_tables()
        build_movie_table()

        create_user("tempUser", "insecurepassword")
        results = exec_get_all("""SELECT username FROM system_users WHERE username = 'tempUser'""")
        self.assertEqual(results, [('tempUser',)])

        delete_user("tempUser")
        results = exec_get_all("""SELECT username FROM system_users WHERE username = 'tempUser'""")
        self.assertEqual(results, [])
    
    def test_login_gen_session_key(self):
        """Attempt to generate a session key given a username and pass"""
        rebuild_tables()
        build_movie_table()

        """Failed attempt because user does not exist"""
        results = generate_session_key('idontexist', 'idontexisteither')
        self.assertEqual(results, (0, 'Login invalid'))

        """Successful attempt with user blorg"""
        results = generate_session_key('blorg', 'saltfatacidheat')
        self.assertEqual(results[1], 'Login was successful')

    def test_validate_session_key(self):
        """Validate a session key"""
        rebuild_tables()
        build_movie_table()

        """Generate session key for user blorg"""
        results = generate_session_key('blorg', 'saltfatacidheat')
        session_k = results[0]

        results = validate_session_key(session_k)
        self.assertEqual(results, True)

    def test_create_and_delete_movie(self):
        """Test that movie is created with unique identifiers"""
        rebuild_tables()
        build_movie_table()

        """Generate session key for user blorg"""
        results = generate_session_key('blorg', 'saltfatacidheat')
        session_k = results[0]

        """Attempt to create a movie with an invalid session key"""
        self.assertEqual(create(3, 'A really really cool new movie', '2021', 'whoami'), None)


        """Create the new movie"""
        create(3, 'A really really cool new movie', '2021', session_k)

        """Checks new movie has been created"""
        results = exec_get_all("""SELECT * FROM movies WHERE title = 'A really really cool new movie'""")
        actual_result = results[0]
        self.assertEqual(actual_result[2:], (3, 'A really really cool new movie', 2021))
        """Ensures that this is the only movie with this primary key"""
        results = exec_get_all("""SELECT COUNT(*) FROM movies WHERE id = '%s'""" % (actual_result[0]))
        self.assertEqual(results, [(1,)])
        """Ensures that this is the only movie with this imdbid"""
        results = exec_get_all("""SELECT COUNT(*) FROM movies WHERE imdbid = '%s'""" % (actual_result[1]))
        self.assertEqual(results, [(1,)])

        """Attempt to delete movie with invalid session key"""
        self.assertEqual(delete('A really really cool new movie', 'whoami'), None)

        """Delete the new  movie"""
        delete('A really really cool new movie', session_k)

        """Ensures that the new movie has been deleted"""
        results = exec_get_all("""SELECT COUNT(*) FROM movies WHERE title = 'A really really cool new movie'""")
        self.assertEqual(results, [(0,)])

    def test_update_movie_rating(self):
        """Attempts to update the movie rating"""
        rebuild_tables()
        build_movie_table()

        """Generate session key for user blorg"""
        results = generate_session_key('blorg', 'saltfatacidheat')
        session_k = results[0]

        """Attempts to update rating without valid session key"""
        self.assertEqual(update_movie_rating('1', 'Greed', 'whoami'), None)

        """Gets the current rating of Greed which is 3"""
        before_rating = exec_get_all("""SELECT rating FROM movies WHERE title = 'Greed'""")

        """Updated rating given valid session key"""
        update_movie_rating('1', 'Greed', session_k)

        """Validates that rating was changed"""
        changed_rating = exec_get_all("""SELECT rating FROM movies WHERE title = 'Greed'""")
        self.assertNotEqual(before_rating, changed_rating)

    def test_logout(self):
        """Tests that user is successfully logged out"""
        rebuild_tables()
        build_movie_table()

        """Generate session key for user blorg"""
        results = generate_session_key('blorg', 'saltfatacidheat')
        session_k = results[0]

        """Logout and verify that session key is gone"""
        logout(session_k)
        results = exec_get_all("""SELECT session_key FROM system_users WHERE username = 'blorg'""")
        self.assertEqual(results, [('None',)])