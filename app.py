import os
import os.path
import datetime
import re
from helper import helper
from db_operations import db_operations

# connect to playlist database
db_ops = db_operations("playlist.db")
data = helper.data_cleaner("songs.csv")

# SQLify welcome page
def startScreen():
    print('''\nWelcome to SQLify (Spotify but SQL!)
    user symbol key: ! = input error, * = execution check\n''')     # so user knows symbols in output

# checks to see if song table is empty
def is_empty():
    # query to return song count
    query = '''
    SELECT COUNT(*)
    FROM songs
    '''

    result = db_ops.single_record(query)
    return result == 0

# checks to see if song is in playlist
def is_song(song_name):
    # query to return song informaion
    query = '''
    SELECT *
    FROM songs
    WHERE Name =:name
    '''

    # results if song in playlist
    dictionary = {"name":song_name}
    db_ops.cursor.execute(query, dictionary)
    results = db_ops.cursor.fetchall()

    # song isn't in playlist
    if len(results) == 0:
        print("! The song " + song_name + " isn't in the playlist. Try again.")
        return False

    # song is in playlist
    else:
        return True

# checks to make sure ASC or DESC is correct
def ASCorDESC(input):
    if input == "ASC":
        return True
    elif input == "DESC":
        return True
    else:
        print("! Incorrect value. Try again.")
        return False

# will fill songs table if it is empty or ask to load new songs
def pre_process():
    # songs table is empty
    if is_empty():
        attribute_count = len(data[0])
        placeholders = ("?,"*attribute_count)[:-1]  # ?,?,?,...? chop off last comma
        query = "INSERT INTO songs VALUES(" + placeholders + ")"
        db_ops.bulk_insert(query, data)

    # ask to load new songs
    print('''Would you like to load new songs from a file?
    1. Yes
    2. No
    ''')
    num = helper.get_choice([1,2])

    # load new songs
    if num == 1:
        load_songs()

# load songs from existing .csv file
def load_songs():
    while True:
        # ask user for the name of the file
        file_name = input('''Enter song file name: ''')
        csv = ".csv"
        file_path = file_name + csv

        # file does not exist
        if not os.path.isfile(file_path):
            print("! File path doesn't exist. Try Again.")

        # file does exist
        elif os.path.isfile(file_path):
            # open & clean new csv file
            new_data = helper.data_cleaner(file_name + ".csv")
            attribute_count = len(new_data[0])
            placeholders = ("?,"*attribute_count)[:-1]
            query = "INSERT INTO songs VALUES(" + placeholders + ")"
            db_ops.bulk_insert(query, new_data)
            break

# main menu options
def options():
    # output options to user
    print('''\nSelect from the following menu options:
    1. Find songs by artist
    2. Find songs by genre
    3. Find songs by feature
    4. Update song attribute
    5. Remove song in playlist
    6. Remove records w/ null values
    7. Exit
    ''')

    # get user choice
    return helper.get_choice([1,2,3,4,5,6,7])

# function to search songs table by artist
def search_by_artist():
    # get list of all artists in table
    query = '''
    SELECT DISTINCT Artist
    FROM songs
    '''

    # prints all artists
    print("Artists in playlist: ")
    artists = db_ops.single_attribute(query)

    # show all artists, create dictionary of options, and let user choose
    choices = {}
    for i in range(len(artists)):
        print(i, artists[i])
        choices[i] = artists[i]
    index = helper.get_choice(choices.keys())

    # user can ask to see 1, 5, or all songs
    print("How many songs do you want returned for", choices[index]+"?")
    print("Enter 1, 5, or 0 for all songs")
    num = helper.get_choice([1,5,0])

    # print results
    query = '''SELECT DISTINCT name
    FROM songs
    WHERE Artist =:artist ORDER BY RANDOM()
    '''

    # executes artist's list of songs
    dictionary = {"artist":choices[index]}
    if num != 0:
        query +="LIMIT:lim"
        dictionary["lim"] = num
    results = db_ops.name_placeholder_query(query, dictionary)
    helper.pretty_print(results)

# searches the songs table by genre
def search_by_genre():
    # get a list of all genres
    query = '''
    SELECT DISTINCT Genre
    FROM songs
    '''

    # print genre options
    print("Genres in playlist:")
    genres = db_ops.single_attribute(query)

    # show all genres and create a dictionary of choices
    choices = {}
    for i in range(len(genres)):
        print(i, genres[i])
        choices[i] = genres[i]
    index = helper.get_choice(choices.keys())

    # user can ask to see 1, 5, or all songs from result
    print("How many songs do you want returned for", choices[index]+"?")
    print("Enter 1, 5, or 0 for all songs")
    num = helper.get_choice([1,5,0])

    # print results
    query = '''
    SELECT DISTINCT name
    FROM songs
    WHERE Genre =:genre ORDER BY RANDOM()
    '''

    # run query for songs and print results
    dictionary = {"genre":choices[index]}
    if num != 0:
        query +="LIMIT:lim"
        dictionary["lim"] = num
    results = db_ops.name_placeholder_query(query, dictionary)
    helper.pretty_print(results)

# searches the songs table by feature
def search_by_feature():
    # features we want to search for - added all features
    features = ['Duration','Energy','Danceability','Acousticness','Liveness','Loudness']

    # show features in table and create dictionary
    print("Features in playlist: ")
    choices = {}
    for i in range(len(features)):
        print("   ", i, features[i])
        choices[i] = features[i]
    index = helper.get_choice(choices.keys())

    # user can ask to see 1, 5, or all features from result
    print("How many songs do you want returned for " + choices[index] + "?")
    print("Enter 1, 5, or 0 for all songs")
    num = helper.get_choice([1,5,0])

    # ask what order we want results shown in
    print("Do you want results sorted in ASC or DESC order?")

    # check that ASC or DESC input correct
    while True:
        # get ASC or DESC
        order = input("ASC or DESC: ")

        # user didn't enter correctly
        if not ASCorDESC(order):
            order = input("ASC or DESC: ")

        # user entered correctly
        elif ASCorDESC(order):
            # print results
            query = '''
            SELECT DISTINCT name
            FROM songs
            ORDER BY
            ''' + choices[index] + " " + order

            # run query for songs and print results
            dictionary = {}
            if num != 0:
                query += " LIMIT:lim"
                dictionary["lim"] = num
            results = db_ops.name_placeholder_query(query, dictionary)
            helper.pretty_print(results)
            break

# updates song attribute by song name
def update_song():
    # ask what song to update
    print("What song would you like to update?")

    while True:
        # get song name
        song_name = input("Song name: ")

        # song exists
        if is_song(song_name):
            # query to select all attributes
            query = '''
            SELECT *
            FROM songs
            WHERE Name =:name
            '''

            # execute to select all song attributes
            dictionary = {"name":song_name}
            results = db_ops.name_placeholder_queries(query, dictionary)
            print("Results...") # instead of helper.pretty_print(results)


            # print all attributes to the user
            attributes = ['songID','Name','Artist','Album','releaseDate','Genre','Explicit','Duration','Energy','Danceability','Acousticness','Liveness','Loudness']
            for result in results:
                    for attribute in attributes:
                        value = result[attributes.index(attribute)]
                        print("    "+f'{attribute}: {value}')

            # save song information
            song_id = results[0][0]
            artist = results[0][2]
            album = results[0][3]
            release_date = results[0][4]
            explicit = results[0][6]

            # allow the user to make a choice
            print('''\nWhat attribute would you like to update?
    1. Song Name
    2. Artist Name
    3. Album Name
    4. Release Date
    5. Explicit
    6. None
            ''')    # sorry wonky indenting to keep format uniform
            num = helper.get_choice([1,2,3,4,5,6])

            # update song name
            if num == 1:
                # ask what name to update to
                print("What do you want to update " + song_name + " to?")
                song_update = input("Enter new song name: ")

                # query to update song name
                query = '''
                UPDATE songs
                SET Name =:new_name
                WHERE songID =:songid
                '''

                # update the song name
                dictionary = {"new_name":song_update, "songid":song_id}
                db_ops.cursor.execute(query, dictionary)
                db_ops.connection.commit()

                # output results
                print("* " + song_name + " was changed to " + song_update + ".")
                break

            # update artist name
            if num == 2:
                # ask what artist to update to
                print("What do you want to update", artist, "to?")
                updated_artist = input("Enter new artist: ")

                # query to update artist name
                query = '''
                UPDATE songs
                SET Artist =:new_artist
                WHERE songID =:songid
                '''

                # update the song name
                dictionary = {"new_artist":updated_artist, "songid":song_id}
                db_ops.cursor.execute(query, dictionary)
                db_ops.connection.commit()

                # output results
                print("* " + artist + " was changed to " + updated_artist + ".")
                break

            # update album name
            if num == 3:
                # ask what album to update to
                print("What do you want to update '" + album + "' to?")
                updated_album = input("Enter new album: ")

                # query to update album name
                query = '''
                UPDATE songs
                SET Album =:new_album
                WHERE songID =:songid
                '''

                # update the album name
                dictionary = {"new_album":updated_album, "songid":song_id}
                db_ops.cursor.execute(query, dictionary)
                db_ops.connection.commit()

                # output results
                print("* " + album + " was changed to " + updated_album + ".")
                break

            # update release date
            if num == 4:

                # use to identify the correct date pattern
                date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')

                # ask what release date to update to
                print("What do you want to update", release_date, "to?")

                while True:
                    # get user input
                    updated_date = input("Enter new date (YYYY-MM-DD): ")

                    # not in YYYY-MM-DD format
                    if not date_pattern.match(updated_date):
                        print("! Incorrect date format. Try Again.")
                        # updated_date = input("Enter new date (YYYY-MM-DD): ")

                    # in YYYY-MM-DD format
                    elif date_pattern.match(updated_date):
                        # query to update release date
                        query = '''
                        UPDATE songs
                        SET releaseDate =:new_date
                        WHERE songID =:songid
                        '''

                        # update the release date
                        dictionary = {"new_date":updated_date, "songid":song_id}
                        db_ops.cursor.execute(query, dictionary)
                        db_ops.connection.commit()

                        # output results
                        print("* " + release_date + " was changed to " + updated_date + ".")
                        break
                break

            # update explicit
            if num == 5:
                # song is explicit
                if explicit == "True":
                    expl_txt = "Explicit"
                    opp_expl_txt = "not Explicit"
                    opp_expl_bool = "False"

                # song is not explicit
                else:
                    expl_txt = "not Explicit"
                    opp_expl_txt = "Explicit"
                    opp_expl_bool = "True"

                # ask to change explicit content
                print("Do you want to change " + song_name + " to " + opp_expl_txt + "?")
                print('''1. Yes\n2. No''')
                explicit_update = helper.get_choice([1,2])

                # user wants to change explicit content
                if explicit_update == 1:
                    # query to update explicit
                    query = '''
                    UPDATE songs
                    SET Explicit =:new_exp
                    WHERE songID =:songid
                    '''

                    # update explicit
                    dictionary = {"new_exp":opp_expl_bool, "songid":song_id}
                    db_ops.cursor.execute(query, dictionary)
                    db_ops.connection.commit()

                    # output results
                    print("* " + song_name + " was changed to " + opp_expl_txt + ".")
                    break

                # user doesn't want to change explicit content
                else:
                    print("* Explicit content not changed.")
                    break

            # back to main menu
            if num == 6:
                print("Returning to the main menu...\n")
                break
            break

# removes song from the table
def remove_song():
    # ask what song to remove
    print("What song would you like to remove?")

    # check song exists
    while True:
        song_name = input("Song name: ")
        # song does not exist
        # if not is_song(song_name):
        #     # user should be prompted again
            # song_name = input("Song name: ")

        # song exists
        if is_song(song_name):
            # query to select all attributes
            query = '''
            SELECT *
            FROM songs
            WHERE Name =:name
            '''

            # print all attributes to the user
            dictionary = {"name":song_name}
            results = db_ops.name_placeholder_queries(query, dictionary)

            # save song information
            song_id = results[0][0]

            # query to remove the song
            query = '''
            DELETE FROM songs
            WHERE songID =:songid
            '''

            # remove the song from the table
            dictionary = {"songid":song_id}
            db_ops.cursor.execute(query, dictionary)
            db_ops.connection.commit()

            # output deletion to user
            print("* " + song_name + " was removed from playlist.")
            break

# removes all records that have at least 1 NULL value
def remove_null_values():
    # query to remove records w/ null values
    query = '''
    DELETE FROM songs
    WHERE songID IS NULL OR
          Name IS NULL OR
          Artist IS NULL OR
          Album IS NULL OR
          releaseDate IS NULL OR
          Genre IS NULL OR
          Explicit IS NULL OR
          Duration IS NULL OR
          Energy IS NULL OR
          Danceability IS NULL OR
          Acousticness IS NULL OR
          Liveness IS NULL OR
          Loudness IS NULL
    '''

    # remove rows w/ 1+ null values
    dictionary = {}
    db_ops.cursor.execute(query, dictionary)
    db_ops.connection.commit()

    # output deletion to user
    print("* Null values were removed.")

# Main Program
startScreen()
pre_process()
#db_ops.create_songs_table() - run once then delete!
# print("is empty?", is_empty()) - debug

# Main loop
while True:
    user_choice = options()
    if user_choice == 1:
        search_by_artist()
    if user_choice == 2:
        search_by_genre()
    if user_choice == 3:
        search_by_feature()
    if user_choice == 4:
        update_song()
    if user_choice == 5:
        remove_song()
    if user_choice == 6:
        remove_null_values()
    if user_choice == 7:
        print("Goodbye!")
        break

# deconstruct at end
db_ops.destructor()
