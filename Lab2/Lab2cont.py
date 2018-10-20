from nltk.corpus import stopwords
from stemming.porter2 import stem
import nltk
import re
idlist = []

#The dictionary here has the word as keys, and another dictionary as the values
#Which have the document IDs as keys and a list of occurences for that word in
#the document as value
dict = {}

'''Module 1 - creating the indexes for the words in the document'''

with open("CW1collection/trec.5000.txt") as fp, open("preprocess.txt", "w") as fr:

    #Get all the lines in the document in a dictionary with ID as key and HEADLINE/TEXT as value
    lis = {}

    #If we come to the ID line, store the next two lines in the dictionary
    #Store the document ID as the key and the HEADLINE and TEXT lines as value
    #Also create a list of all documents
    for line in fp:
        if line [0] == "I":
            headtext = ""
            for i in range(2):
                headtext = headtext + fp.next() + " "
            lis.update({line[4:].rstrip() : headtext})
            idlist.append(line[4:].rstrip())

    #The dictionary here has the word as keys, and another dictionary as the values
    #Which have the document IDs as keys and a list of occurences for that word in
    #the document as value

    #For each of the text lines (documents) (headline plus text)
    for ele in lis:

        #Break out the words in the line, convert to lowercase and preprocess (alphanumeric, lowercase, stopwrods, stemming)
        linewo = nltk.word_tokenize(lis[ele])
        linewo = [wo for wo in linewo if wo!="TEXT" and wo != "HEADLINE"]
        linewo = [wo.lower() for wo in linewo if wo.isalpha() or wo.isdigit() and wo not in stopwords.words('english')]
        linewo = [stem(wo) for wo in linewo]

        #Here we get the respective document index
        doc_index = ele
        #print (doc_index)

        #If a word is in a document, add all of its positions in that document to the dictionary
        #If word already in the dictionary, update the positions
        for wo in linewo:
            if wo not in dict:
                dict[wo] = {doc_index: [i + 1 for i, x in enumerate(linewo) if x == wo]}
            else:
                dict[wo].update({doc_index: [i + 1 for i, x in enumerate(linewo) if x == wo]})

    #Write the first file
    '''
    for x in dict:
            #Writing the word
            fr.write (str(x) + ":")
            fr.write ("\n")
            #Now we write it's document IDs and it's occurences in them
            for y in dict[x]:
                fr.write("\t")
                fr.write(str(y) + ":" + " ")
                fr.write(",".join([str(i) for i in dict[x][y]]))
                fr.write("\n")
            fr.write("\n")'''

fp.close()
fr.close()

'''Module 2 - reloading the index into memory and running boolean, phrase and prximity search'''

with open("preprocess.txt") as fr,  open("CW1collection/queries.boolean.txt") as fq, open("output.txt", "w") as fil:

    qlis = []

    #First we extract the queries and remove the newline in the beginning
    for line in fq:
        queries = line.split(" ", 1)
        qlis.append(queries[1].rstrip())
    #print (qlis)

    for query in qlis:
        retrievedocs = [[]]
        retrivindex = 0

        #If we have a Boolean seach query
        if "AND" in query or "OR" in query or "NOT" in query:
            words = re.split(" +(AND|OR) +", query)
            print (words)
            i = 0
            andor = 0
            while (i < len(words)):

                #Here we cover the NOT word condition, and iterate the counter by 2 then continue
                #We take out the documents containing this word
                #By subtracting the list of documents containing this word from the list of all document IDs
                if (words[i] == "NOT"):
                    nextwor = words[i+1]
                    nextwor = nextwor.lower()
                    nextwor = stem(nextwor)
                    #Retrivindex can be updated inside the loop since we will only find the word once.
                    #Subtract the list of documents containing the word from list of all documents
                    for x in dict:
                        if x == nextwor:
                            docslist = list(set(idlist) - set(dict[x].keys()))
                            retrievedocs.insert(retrivindex, dict[x].keys())
                    retrivindex = retrivindex + 1
                    i = i + 2
                    continue

                #Here we cover the phrase condition
                elif (words[i][0] == "\""):
                    #Remove the quotes in the string and preprocess
                    phrasewords = words[i].replace('"', '')
                    phraselist = phrasewords.split()
                    phraselist = [prh.lower() for prh in phraselist]
                    phraselist = [stem(prh) for prh in phraselist]
                    for x in dict:
                        #If we have found the first word in the dictionary
                        if x == phraselist[0]:
                            #If we have found the second word in the dictionary
                            for y in dict:
                                if y == phraselist[1]:
                                    #For all the document IDs in the first  phrase word
                                    #If it is in the list of document IDs for the second phrase word
                                    for srdoc in dict[x]:
                                        if srdoc in dict[y].keys():
                                            #Use that document ID to check the list of occurences
                                            #x + 1 because the first word in the phrase will be
                                            #before the second word in the document
                                            indexlis = [x+1 for x in dict[x][srdoc]]
                                            findlis = [x for x in dict[y][srdoc]]
                                            #If both the lists contain the same position, we have a phrase match
                                            if len([x for x in indexlis if x in findlis]) != 0:
                                                #If we have already found one document ID for this phrase
                                                #extend that list with more indexes
                                                if (retrievedocs[retrivindex]):
                                                    retrievedocs[retrivindex].extend([srdoc])
                                                #if we haven't, create a list of indexes
                                                else:
                                                    retrievedocs.insert(retrivindex, [srdoc])
                    retrivindex = retrivindex + 1
                    i = i + 1
                    continue

                elif(words[i] == "AND"):
                    andor = 0
                    i = i + 1
                    continue

                elif(words[i] == "OR"):
                    andor = 1
                    i = i + 1
                    continue

                #If we come accross just a simple string
                #Find all the documents that have it
                else:
                    wor = words[i]
                    wor = wor.lower()
                    wor = stem(wor)
                    #Retrivindex can be updated inside the loop since we will only find the word once.
                    for x in dict:
                        if x == wor:
                            print (retrivindex)
                            print (x)
                            retrievedocs.insert(retrivindex, dict[x].keys())
                    retrivindex = retrivindex + 1
                    i = i + 1
                    continue

            #After we have parsed through the entire query
            finalist = []
            if (andor == 0):
                finalist = list(set(retrievedocs[0]) & set(retrievedocs[1]))
            elif (andor == 1):
                finalist = list(set().union(retrievedocs[0], retrievedocs[1]))

            #Write the document IDs to the file
            for docs in finalist:
                    fil.write (str(docs) + ",")
            fil.write("\n")

        #Here we implement proximity search. We first extract the number out from the query
        #Then we get the individual words and search for the common document
        #containg both words, the same way we did phrase search
        elif (query[0] == "#"):
            #Get the number out by splitting on the opening bracket and replacing the hash
            proxindex = query.split('(')[0]
            proxindex = proxindex.replace('#', '')
            #Replace the comma between the words with a space and split on that.
            proxwords = query.replace('#', '').replace('(', '').replace(')', '').replace(',', ' ')
            proxlist = proxwords.split()
            #Then do the preprocessing on the words
            proxlist = [prh.lower() for prh in proxlist]
            proxlist = [stem(prh) for prh in proxlist]
            for x in dict:
                #If we have found the first word in the dictionary
                if x == proxlist[0]:
                    #If we have found the second word in the dictionary
                    for y in dict:
                        if y == proxlist[1]:
                            #For all the document IDs in the first word
                            #If it is in the list of document IDs for the second word
                            for srdoc in dict[x]:
                                if srdoc in dict[y].keys():
                                    #Use that document ID to check the list of occurences
                                    indexlis = [x for x in dict[x][srdoc]]
                                    findlis = [x for x in dict[y][srdoc]]
                                    #If the difference in position for any two ocurences is less than 15
                                    #We have a proximity match
                                    for a in indexlis:
                                        for b in findlis:
                                            if abs(a-b) <=15:
                                                retrievedocs[0].extend(srdoc)

            #Write the document IDs to the file
            for docs in retrievedocs[0]:
                    fil.write (str(docs) + ",")
            fil.write("\n")

        #We have a simple string only to match
        else:
            wor = query
            wor = wor.lower()
            wor = stem(wor)
            #Retrivindex does not need to be updated
            for x in dict:
                if x == wor:
                    retrievedocs[0] = dict[x].keys()

            #Write the document IDs to the file
            for docs in retrievedocs[0]:
                    fil.write (str(docs) + ",")
            fil.write("\n")
