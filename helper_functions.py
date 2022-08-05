# These functions are being used in different notebooks. 
# Thats why we decided to write them in an extzra .py file, so we can import them when needed 


def file_name(current_movie):
    """
    translates the name of the movie into the version that is identical with the title of the saved scripts
  
    Parameters:
    current_movie (dataFrame): all the entries of our Dataframe that correspond to the movie currently assessed
  
    Returns:
    str: the path where we have the script saved, so that we can later easily access each movie (only if we have the script saved)
    None: if we dont have the corresponding script to the movie (should never happen here, cause the datasets only has those movies, for which a script)
  
    """

    # dropping the index, so we can access each movie in a general manner
    current_movie = current_movie.reset_index(drop=True)
    
    # getting the actual file name of the movie
    # If the movie name starts with 'The', the script file has the 'The' after the rest of the title
    movie = current_movie.at[0, "title_of_movie"]
    print(movie)
    if movie.startswith("The"):
        movie = movie.replace("The","")
        movie = movie + "the"
        
    # Script file namesare without spaces
    movie_new = movie.replace(" ", "")
    
    # getting the genres for the current movie
    genres = ["genre1", "genre2", "genre3"]

    # because we have the movie scripts saved under a corresponding genre folder, we search for the movie script
    # in all of the three genre (folders) which we have saved for it
    for genre in genres:
        g = current_movie.at[0, genre]
        # creating a string with the path to the corresponding movie script (all file names have the same ending)
        path = r"imsdb_scenes_dialogs_nov_2015/imsdb_scenes_dialogs_nov_2015/dialogs/{gen}/{name}_dialog.txt".format(gen=g, name=movie_new.lower())
        
        # if we have the script of the movie
        if os.path.exists(path):
            return path

    return(None)

########################################################################## NEXT FUNCTION ##########################################################################

def first_criterion(current_movie):
    """
    Checks if there is more than one actress in the cast of the movie
  
    Parameters:
    current_movie (dataFrame): all the entries of our Dataframe that correspond to the movie currently assessed
  
    Returns:
    boolean: True if criterion is met, else False
  
    """
    nr_females = 0
    
    # for each row that encodes the gender female we increment our count by 1
    for r in current_movie['gender']:
        if r == 1.0:
            nr_females += 1
    if nr_females > 1:
        return True 
    else: 
        return False

########################################################################## NEXT FUNCTION ##########################################################################

def same_name(name_script, name_table):
    """
    Checks if the character-name in the table corresponds to the name in the script line.

    Parameters:
    name_script (str): current line of our script with the potential name of the character
    name_table (str): the current character-name in the table
  
    Returns:
    boolean: True if they match, else False
  
    """
    
    # strippes the string from any writing in brackets and empty spaces at the end
    stripped_name = re.sub("[\([].*?[\)\]]", "", name_script).strip()
    # if there is nothing left after stripping the string, return false
    if stripped_name == "":
        return False
        
    # Depending on the script and movie we are dealing with, there are different ways of referencing the movie-characters
    # we remove all extra chars, so we have a uniform way of referencing them
    name_table = name_table.replace(".", "")
    stripped_name = stripped_name.replace(".", "").replace("(", "").replace(")", "").replace("*", "").replace("?", "").replace("[", "").replace("//", "")
    
    # compile a regular expression that matches any string that includes the name that is left from the script line
    r = re.search(r'.*{}.*'.format(stripped_name), name_table.upper())
    if r:
        return True
    else:
        return False 

########################################################################## NEXT FUNCTION ##########################################################################

def second_and_third_criterion(lines, current_movie):
    """
    Checks if the second and thrid criterion of the bechdel test are met. 
    Namely, if there are two female-characters talking with each other and more than 3 sentences
  
    Parameters:
    lines (str): the lines of the script we are currently assessing
    current_movie(dataFrame): all the entries of our Dataframe that correspond to the movie currently assessed
  
    Returns:
    dict: dictionary with criterion as entries and their respective boolean values
  
    """
    # helper variables 
    criterions = {"Second": False, "Third": False, "Talking": ""}
    female_last = False
    index_female = 0
    nr_sentences = 0
    occurences = 0
    last_person = ""
    named_character = False
    talking_ppl_list = []
    
    # Second Criterion
    # going through the lines of the script
    for i, line in enumerate(lines):
        
            # only interested in upper case lines (as they mark the new speaking charcater)
            if line.isupper(): 

                # going through the rows of the table with the named characters of our dataset
                for index, row in enumerate(current_movie['character']):
                    
                    # if a name of the table matches the name of the line in the script
                        if same_name(line, row):
                            
                            # helper variable so we later on know that this line includes a named character
                            named_character = True
                            # check if the character this line contains is female with help of our Dataframe
                            if current_movie.at[index, 'gender'] == 1.0: 
                                
                                # check if the last speaking person was female 
                                # (so we would have two consecutive female characters)
                                # also checks if the last speaking person isn't the same character that is currently speaking
                                if (female_last == True) and not same_name(last_person, row): 
                                    
                                    # SECOND CRITERION is met
                                    criterions['Second'] = True
                                    occurences += 1

                                    # counter for THIRD CRITERION (speaking at least 3 sentences) 
                                    for l in lines[index_female: i]:
                                        nr_sentences += l.count(".")
                                        nr_sentences += l.count("?")
                                        nr_sentences += l.count("!")
                                        
                                    talking_ppl = last_person + " talks " + str(nr_sentences) + " sentence(s) with " + str(row) + " from line: " + str(index_female) + " till line: " + str(i)
                                    talking_ppl_list.append(talking_ppl)

                                    if nr_sentences >=3:
                                        # THIRD CRITERION is met
                                        criterions['Third'] = True
                                    # need to set the counter back to zero for the next speaking character
                                    nr_sentences = 0
                                    
                                # helper variable so we know the gender of this character in the next round
                                female_last = True
                                index_female = i
                                
                            else:
                                female_last = False
                            # helper variable so we know who previously talked, when we are in the next round
                            last_person = line
                            break
                            
                        else:
                            named_character = False               
            
            # In case we have a character speaking that is not listed in our dataframe,
            # we set female_last to False, as it is not a named female character 
            if not named_character:
                
                female_last = False
                last_person = line 
            
                      
    criterions['Talking'] = talking_ppl_list
    print("There are/is", occurences, "occurence(s) in this movie, where women talk with each other.")
    return(criterions)

########################################################################## NEXT FUNCTION ##########################################################################

def bechdel_test(current_movie):
    """
    Checks if the criterions for the bechdel test are met 
    Namely, if there are two female-characters talking with each other more than 3 sentences
  
    Parameters:
    current_movie(dataFrame): all the entries of our Dataframe that correspond to the movie currently assessed
  
    Returns:
    dict: dictionary with criterions as entries and their respective boolean values
  
    """

    with open(file_name(current_movie), 'r') as file:
        lines = file.readlines()
    
        # important variables
        bechdel_test = {'Named_Character': False, 'Consecutive_dialog': False, 'More_than_two_sentences': False, "Who_is_talking": ""}
    
    
        # First Criterion
        bechdel_test['Named_Character'] = first_criterion(current_movie)
    
        # Second and Third Criterion
        criterions = second_and_third_criterion(lines, current_movie)
        bechdel_test['Consecutive_dialog'] = criterions['Second']
        bechdel_test['More_than_two_sentences'] = criterions['Third']
        bechdel_test['Who_is_talking'] = criterions['Talking']
        
        return bechdel_test