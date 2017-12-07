# Hangman game
#

# -----------------------------------
# Helper code
# You don't need to understand this helper code,
# but you will have to know how to use the functions
# (so be sure to read the docstrings!)

import random
import string

WORDLIST_FILENAME = "words.txt"

def loadWords():
    """
    Returns a list of valid words. Words are strings of lowercase letters.

    Depending on the size of the word list, this function may
    take a while to finish.
    """
    print("Loading word list from file...")
    # inFile: file
    inFile = open(WORDLIST_FILENAME, 'r')
    # line: string
    line = inFile.readline()
    # wordlist: list of strings
    wordlist = line.split()
    print("  ", len(wordlist), "words loaded.")
    return wordlist

def chooseWord(wordlist):
    """
    wordlist (list): list of words (strings)

    Returns a word from wordlist at random
    """
    return random.choice(wordlist)

# end of helper code
# -----------------------------------

# Load the list of words into the variable wordlist
# so that it can be accessed from anywhere in the program
wordlist = loadWords()

def isWordGuessed(secretWord, lettersGuessed):
    '''
    secretWord: string, the word the user is guessing
    lettersGuessed: list, what letters have been guessed so far
    returns: boolean, True if all the letters of secretWord are in lettersGuessed;
      False otherwise
    '''
    # FILL IN YOUR CODE HERE...
    correct_guess = 0

    for letters in secretWord:
        if letters in lettersGuessed:
            correct_guess+=1
    if len(secretWord) == correct_guess:
        return True
    else:
        return False




def getGuessedWord(secretWord, lettersGuessed):
    '''
    secretWord: string, the word the user is guessing
    lettersGuessed: list, what letters have been guessed so far
    returns: string, comprised of letters and underscores that represents
      what letters in secretWord have been guessed so far.
    '''
    # FILL IN YOUR CODE HERE...
    stre = ""
    for letter in secretWord:
        if letter in lettersGuessed:
            stre+=letter +" "
        else:
            stre += "_ "
    return stre



def getAvailableLetters(lettersGuessed):
    '''
    lettersGuessed: list, what letters have been guessed so far
    returns: string, comprised of letters that represents what letters have not
      yet been guessed.
    '''
    # FILL IN YOUR CODE HERE...

    strin = string.ascii_lowercase
    stre = ""
    for i in range(len(strin)):

        if strin[i] in lettersGuessed:
            continue
        else:
            stre += strin[i]

    return stre



def hangman():
    '''
    secretWord: string, the secret word to guess.

    Starts up an interactive game of Hangman.

    * At the start of the game, let the user know how many
      letters the secretWord contains.

    * Ask the user to supply one guess (i.e. letter) per round.

    * The user should receive feedback immediately after each guess
      about whether their guess appears in the computers word.

    * After each round, you should also display to the user the
      partially guessed word so far, as well as letters that the
      user has not yet guessed.

    Follows the other limitations detailed in the problem write-up.
    '''
    # FILL IN YOUR CODE HERE...
    #loadWords()


    secretWord= "c"#chooseWord(wordlist)

    print("Welcome to the game, Hangman!")
    print("I am thining of a word that is {} long.".format(len(secretWord)))
    
    strikes = 8
    lettersGuessed = []
    while strikes >=0:

        print("you have {} guesses  left".format(strikes))
        print("Available letters: {}".format(getAvailableLetters(lettersGuessed)))
        ask = input("type in a letter to guess: ").lower()


        if ask in secretWord and ask not in lettersGuessed:
            lettersGuessed.append(ask)
            print("Available letters: {}".format(getAvailableLetters(lettersGuessed)))
            print("Good guess : {}".format(getGuessedWord(secretWord,lettersGuessed)))
        elif ask in lettersGuessed:
            print("Oops! You've already guessed that letter:".format(getGuessedWord(secretWord,lettersGuessed)))
        else:
            lettersGuessed.append(ask)
            strikes -=1
            print("Available letters: {}".format(getAvailableLetters(lettersGuessed)))
            print("that letter is not in my word : {}".format(getGuessedWord(secretWord,lettersGuessed)))
        print("--------------------")
        if isWordGuessed(secretWord, lettersGuessed):
            print("Congratulations, you won!")
            break
        elif strikes == 0:
            print("Sorry, you ran out of guesses. The word was {}.".format(secretWord))
            break


        #print(getGuessedWord(secretWord,lettersGuessed))







hangman()
# When you've completed your hangman function, uncomment these two lines
# and run this file to test! (hint: you might want to pick your own
# secretWord while you're testing)

# secretWord = chooseWord(wordlist).lower()
# hangman(secretWord)
