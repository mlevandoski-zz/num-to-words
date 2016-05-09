import re

# general plan of program:
#   main body of program for i/o,
#   one function for parsing / regexes
#   one function for number to word translation, given boolean values from the parser

# predefined global arrays for the ones, teens, and twenties cases, as well as dates
ones = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
teens = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
twenties = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
regdates = ["", "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "nineth"]
teendates = ["", "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth", "sixteenth", "seventeenth", "eighteenth", "ninteenth"]
moredates = ["tenth", "twentieth", "thirtieth", "fourtieth", "fiftieth", "sixtieth", "seventieth", "eightieth", "ninetieth"]

# this function converts an integer number into written english words
# parameter n is the float number to be converted
# other parameters are booleans specifying whether or not the number falls under a certain case
def numstowords(n, isdate, isyear, plusdecimal, ismoney):
    # find numdigits and parse number into each digit
    words = "" # base case, words is the empty string
    words2 = ""
    stringified = str(n)
    stringified = stringified.replace(',', '') # remove commas from number if there are any
    if '.' in stringified:
        stringified, secondstring = stringified.split('.') # if there's a decimal point, split it there
        if secondstring and ismoney:
            words2 = numstowords(int(secondstring),0,0,1,1);
        elif secondstring:
            words2 = numstowords(int(secondstring),0,0,1,0)
    numdigits = len(stringified)
    if isdate:
        # note: for length 2, stringified[0] is tens digit, stringified[1] is ones digit
        if numdigits == 1:
            words = regdates[int(stringified[0])]
        else:
        # date is 2 digits: either one of moredates, teendates, or twenties + "-" + regdates
            if int(stringified[1]) == 0:
                words = moredates[int(stringified[0])]
            elif int(stringified[0]) == 1:
                words = teendates[int(stringified[1])]
            else:
                words = twenties[int(stringified[0])] + "-" + regdates[int(stringified[1])]
    elif isyear:
        # handle nineteen ninety-one versus two thousand fifteen.
        if int(stringified[0]) == 2 and int(stringified[1]) == 0: # ex. 20xx
            words = "two thousand"
        elif int(stringified[0]) == 1: # ex. 18xx
            words = teens[int(stringified[1])];
        if int(stringified[2]) == 1: # ex. xx19
            words = words + " " + teens[int(stringified[3])]
        else: # ex. xx25
            words = words + " " + twenties[int(stringified[2])] + "-" + ones[int(stringified[3])]

    # ELSE: deal with regular number
    # going to assume less than 1,000,000,000,000
    else:
        if plusdecimal and ismoney:
            words = words + " dollars and "
        elif plusdecimal:
            words = words + " point "
        if numdigits > 9:
            if numdigits >= 12:
                words, allzeroes = passinthree(words, stringified[-12], stringified[-11], stringified[-10])
            elif numdigits == 11:
                words, allzeroes = passinthree(words, '0', stringified[-11], stringified[-10])
            else:
                words, allzeroes = passinthree(words, '0','0', stringified[-10])
            words = words + " billion "
        if numdigits > 6:
            if numdigits >= 9:
                words, allzeroes = passinthree(words, stringified[-9], stringified[-8], stringified[-7])
            elif numdigits == 8:
                words, allzeroes = passinthree(words, '0', stringified[-8], stringified[-7])
            else:
                words, allzeroes = passinthree(words, '0', '0', stringified[-7])
            if not allzeroes:
                words = words + " million "
        if numdigits > 3:
            if numdigits >= 6:
                words, allzeroes = passinthree(words, stringified[-6], stringified[-5], stringified[-4])
            elif numdigits == 5:
                words, allzeroes = passinthree(words, '0', stringified[-5], stringified[-4])
            else:
                words, allzeroes = passinthree(words, '0', '0', stringified[-4])
            if not allzeroes:
                words = words + " thousand "
        if numdigits >=3:
            words, allzeroes = passinthree(words, stringified[-3], stringified[-2], stringified[-1])
        elif numdigits == 2:
            words, allzeroes = passinthree(words, '0', stringified[-2], stringified[-1])
        else:
            words, allzeroes = passinthree(words, '0', '0', stringified[-1])

    if words2 and ismoney:
        words = words + words2 + " cents"
    elif words2:
        if not words:
            words = 'zero'
        words = words + words2
    return words;
# end numtowords

# passes in three numbers, the hundreds place, the tens place, and the ones place
def passinthree(words, three, two, one):
    allzeroes = True;
    if int(three) != 0:
        words = words + ones[int(three)] + " hundred "
        allzeroes = False;
    if int(two) != 0 and int(two) != 1:
        words = words + twenties[int(two)]
        allzeroes = False;
        if int(one) != 0:
            words = words + "-"
    if int(two) == 1:
        words = words + teens[int(one)]
        allzeroes = False;
    else:
        if int(one) != 0:
            words = words + ones[int(one)]
            allzeroes = False;
    return (words, allzeroes)
# end passinthree

# this function takes a line of text to be converted and returns a line of text after conversion
def parser(orig_line):
    index = 0
    split = orig_line.split()
    converted_line = list(split)

    for word in split:
        # CASE 1: DATES
        # if we see Jan. Feb. Mar. ... next word should be date,
        date_patterns = ['Jan.', 'Feb.', 'Mar.', 'Apr.', 'Aug.', 'Sept.', 'Oct.', 'Nov.', 'Dec.', 'Jan', 'Feb', 'Mar', 'Apr', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec',
        'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        for pattern in date_patterns:
            if (word == pattern):
                numdigits = len(split[index+2])
                if (numdigits == 4): # this is the case for January , 2014
                    wordsnumber = numstowords(split[index+2],0,1,0,0)
                    converted_line[index+1] = wordsnumber
                    split[index+2] = ''
                    converted_line[index+2] = ''
                else: # this is the case for January 14 , 1992
                    wordsnumber = numstowords(split[index+1],1,0,0,0) # the day
                    converted_line[index+1] = wordsnumber
                    split[index+1] = ''
                    try:
                        split[index+3]
                        year = re.match('^\d+$', split[index+3], flags=0) #
                        if year:
                            wordsnumber = numstowords(split[index+3],0,1,0,0) # the year
                            converted_line[index+2] = ','
                            converted_line[index+3] = wordsnumber
                            split[index+3] = ''
                    except IndexError:
                        year = ''
        # CASE 2: DOLLAR AMOUNTS
        # if we see a $, next word should be number, change to 'X dollars'
        if (word == '$'):
            if split[index+2] == 'million' or split[index+2] == 'billion':
                wordsnumber = numstowords(split[index+1],0,0,0,0)
                converted_line[index] = wordsnumber
                converted_line[index+1] = split[index+2] + " dollars"
                converted_line[index+2] = ''
            else:
                wordsnumber = numstowords(split[index+1],0,0,0,1)
                converted_line[index] = wordsnumber
                converted_line[index+1] = ''
            split[index+1] = ''
        # CASE 3: PERCENTAGES
        #if we see %, prev word should be number, change to 'number percent'
        elif (word == '%'):
            if split[index-1]:
                wordsnumber = numstowords(split[index-1],0,0,0,0)
                converted_line[index-1] = wordsnumber
            converted_line[index] = ' percent'
        # basic numbers, fractions, misc
        else:
            # check for basic numbers with or without commas
            matchobj = re.match('(^\d+|\d{1,3}(,\d{3})*)(\.\d+)?$', word, flags=0)
            if matchobj:
                wordsnumber = numstowords(split[index],0,0,0,0)
                converted_line[index] = wordsnumber

            # check for fractions
            matchobj = re.match('^\d+\\\/\d+?$', word, flags=0)
            if matchobj:
                num, denom = word.split('\/')
                topnumber = numstowords(num,0,0,0,0)
                botnumber = numstowords(denom,1,0,0,0)
                if topnumber == 'one' and botnumber == 'second':
                    botnumber = 'half'
                elif botnumber == 'second':
                    botnumber = 'halves'
                elif topnumber != 'one':
                    botnumber = botnumber + "s"
                mixed = re.match('^\d+$', split[index-1], flags=0) # if prev item was a number, this is a mixed fraction
                if mixed:
                    converted_line[index] = "and " + topnumber + " " + botnumber
                else:
                    converted_line[index] = topnumber + " " + botnumber
                split[index] = ''

            # additional cases, like streets
            matchobj = re.match('^\d+((st)|(nd)|(rd)|(th))$', word, flags=0)
            if matchobj:
                justthenumber = word[:-2]
                wordsnumber = numstowords(justthenumber,1,0,0,0)
                converted_line[index] = wordsnumber
            #handles case with hyphen like 343-point
            matchobj = re.match('^\d+(.\d+)?-', word, flags=0)
            if matchobj:
                num, extra = word.split('-')
                wordsnumber = numstowords(num,0,0,0,0)
                converted_line[index] = wordsnumber + "-" + extra
            #handles case with hyphen like C-12
            matchobj = re.match('^[A-Z]+-\d+$', word, flags=0)
            if matchobj:
                extra, num = word.split('-')
                wordsnumber = numstowords(num,0,0,0,0)
                converted_line[index] = extra + "-" + wordsnumber
        converted_line[index] = converted_line[index] + " "
        index = index + 1
    return converted_line
# end parser

# main program, handles I/O
open("output.txt", 'w').close()
inputname = raw_input("Please enter name of input text file: ");
# opens file and passes each line to the parser() function
with open(inputname, "r+") as f:
    fout = open("output.txt", "wb")
    for line in f:
        newline = parser(line)
        for word in newline:
            fout.write(''.join(word))
        fout.write('\n')
    fout.close();
    print("Done! Output in \"output.txt\"")
#end main
