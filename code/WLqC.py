# run Quality Check against new sub data

import os
import sys
import pandas as pd
import sys

def parse_cmd_args():
    import argparse
    parser = argparse.ArgumentParser(description='QC for ATS')
    parser.add_argument('-s', type=str, help='Path to submission')
    parser.add_argument('-o', type=str, help='Path to output for QC plots and Logs')
    parser.add_argument('-sub', type=str, help='Subject ID')

    return parser.parse_args()

def df(submission):
    submission = pd.read_csv(submission)
    return submission

def qc(submission):
    errors = []
    submission = df(submission)
    # Check if submission is a DataFrame
    if not isinstance(submission, pd.DataFrame):
        errors.append('Submission is not a DataFrame. Could not run QC')
    
    # Check if submission is empty
    if len(submission) == 0:
        errors.append('Submission is empty')
    
    #Check if submission has correct number of rows (within 5% of expected = 618)
    if len(submission) < 587 or len(submission) > 649:
        errors.append('Submission has incorrect number of rows')
    # If there are any errors, print them and exit
    if errors:
        for error in errors:
            print(error)
        sys.exit(1)

    print("All QC checks passed.")
        
    
def plots(submission, output, sub, version):
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from math import pi
    from fuzzywuzzy import fuzz
    from fuzzywuzzy import process

    df = pd.read_csv(submission)

    listA = [['book', 'flower', 'train', 'rug', 'meadow', 'harp', 'salt', 'finger', 'apple', 'log', 'button', 'key', 'gold', 'rattle'],['bowl', 'dawn', 'judge', 'grant', 'insect', 'plane', 'county', 'pool', 'seed', 'sheep', 'meal', 'coat', 'bottle', 'peach', 'chair']]
    listB = [['street', 'grass', 'door', 'arm', 'star', 'wife', 'window', 'city', 'pupil', 'cabin', 'lake', 'pipe', 'skin', 'fire', 'clock'],['baby', 'ocean', 'palace', 'lip', 'bar', 'dress', 'steam', 'coin', 'rock', 'army', 'building', 'friend', 'storm', 'village', 'cell']]
    listC = [['tower', 'wheat', 'queen', 'sugar', 'home', 'boy', 'doctor', 'camp', 'flag', 'letter', 'corn', 'nail', 'cattle', 'shore', 'body'],['sky', 'dollar', 'valley', 'butter', 'hall', 'diamond', 'winter', 'mother', 'christmas', 'meat', 'forest', 'tool', 'plant', 'money', 'hotel']]
    
    #for text in version, assign variable version to corresponding list, if .csv is in version, remove it
    if '.csv' in version:
        version = version[:-4]
    
    if 'A' in version:
        key = listA
    elif 'B' in version:
        key = listB
    elif 'C' in version:
        key = listC


    test = df[df['block_c'] != 'prac']
    test = test[1:]


    #dist/immed = if 'condition' is distr or immed

    dist = test[test['condition'] == 'distr']
    immed = test[test['condition'] == 'immed']



    #if 'enter' in response, store the line numbers for before either the enter before or the beginning of the df (for the first word) in a list of lists

    dist_words = []
    immed_words = []

    for i in range(len(dist)):
        if i == 0:
            for j in range(len(dist)):
                if dist.iloc[j]['response'] == 'enter':
                    dist_words.append([0, j])
                    break
        elif dist.iloc[i]['response'] == 'enter':
            for j in range(i+1, len(dist)):
                if dist.iloc[j]['response'] == 'enter':
                    dist_words.append([i+1, j])
                    break
        
    for i in range(len(immed)):
        if i == 0:
            for j in range(len(immed)):
                if immed.iloc[j]['response'] == 'enter':
                    immed_words.append([0, j])
                    break
        elif immed.iloc[i]['response'] == 'enter':
            for j in range(i+1, len(immed)):
                if immed.iloc[j]['response'] == 'enter':
                    immed_words.append([i+1, j])
                    break
    # for ranges in dist and immed, add the characters before the string 'enter' in 'multichar_response' to the beginning of each list in list of lists

    for i in range(len(dist_words)):
        dist_words[i].insert(0, dist.iloc[dist_words[i][1]]['multichar_response'][:-5])

    for i in range(len(immed_words)):
        immed_words[i].insert(0, immed.iloc[immed_words[i][1]]['multichar_response'][:-5])


    # for the ranges in each list of lists, if the string 'backspace' is in 'response' add a 1 to the end of the list, else add a 0
    count = 0
    for i in range(len(dist_words)):
        for j in range(dist_words[i][1], dist_words[i][2]):
            if 'backspace' in dist.iloc[j]['response']:
                count = 1
        dist_words[i].append(count)
        count = 0


    count = 0
    for i in range(len(immed_words)):
        for j in range(immed_words[i][1], immed_words[i][2]):
            if 'backspace' in immed.iloc[j]['response']:
                count = 1
        immed_words[i].append(count)
        count = 0
        

    # for the ranges in each list of lists, subtract the block_dur of the last line number from the block_dur of the first line number and add the result to the end of the list
    for i in range(len(dist_words)):
        dist_words[i].append(dist.iloc[dist_words[i][2]]['block_dur']-dist.iloc[dist_words[i][1]]['block_dur'])

    for i in range(len(immed_words)):
        immed_words[i].append(immed.iloc[immed_words[i][2]]['block_dur']-immed.iloc[immed_words[i][1]]['block_dur'])
    
    print(dist_words)
    print(immed_words)

    def fuzzy(sub_list, word_list):

        from fuzzywuzzy import fuzz
        from fuzzywuzzy import process

        count =0
        used = []
        passed =[]
        #iterate through the list of lists and compare the first element of each list to all in list of words
        #the word in sub_list that has the highest ratio to a word in word_list is the word that is most similar
        #if that ratio is greater than 80, add 1 to count
        
        for i in range(len(sub_list)):
            for j in range(len(word_list)):
                ratio = fuzz.ratio(sub_list[i][0], word_list[j])
                if ratio > 80 and word_list[j] not in used:
                    count += 1
                    used.append(word_list[j])
                    passed.append(sub_list[i][0])
                    break
        return count/len(word_list), passed 

    def absolute(sub_list, word_list):

        count = 0
        used = []
        passed = []
        for i in range(len(sub_list)):
            for j in range(len(word_list)):
                if sub_list[i][0] == word_list[j] and word_list[j] not in used:
                    count += 1
                    used.append(word_list[j])
                    passed.append(sub_list[i][0])
                    break
        return count/len(word_list), passed 

    dist_fuzzy = fuzzy(dist_words, key[1])
    immed_fuzzy = fuzzy(immed_words, key[0])
    print(dist_fuzzy)
    print(immed_fuzzy)

    import matplotlib.pyplot as plt
    import seaborn as sb

    # create a dataframe with the list of lists
    df_dist = pd.DataFrame(dist_words, columns = ['word', 'start', 'end', 'backspace', 'duration'])
    df_immed = pd.DataFrame(immed_words, columns = ['word', 'start', 'end', 'backspace', 'duration'])




    #plot the duratiion of each word for dist where blue is no backspace and red is backspace
    plt.figure(figsize=(12,6))
    sb.scatterplot(x = 'word', y = 'duration', data = df_dist, hue = 'backspace', s=75)
    sb.set(rc={'figure.figsize':(20,10)})
    plt.title('Distraction Condition')
    #add an x if the word is wrong
    for i in range(len(df_dist)):
        if df_dist.iloc[i]['word'] not in dist_fuzzy[1]:
            plt.text(i, df_dist.iloc[i]['duration'], 'x', fontsize=12, color='black')
    plt.savefig(os.path.join(output, f'{sub}_rt_acc_fuzzy_dist.png'))
    plt.close()
    plt.figure(figsize=(12, 6))
    sb.scatterplot(x = 'word', y = 'duration', data = df_immed, hue = 'backspace', s=75)
    sb.set(rc={'figure.figsize':(20,10)})
    plt.title('Immediate Condition')
    #add an x if the word is wrong
    for i in range(len(df_immed)):
        if df_immed.iloc[i]['word'] not in immed_fuzzy[1]:
            plt.text(i, df_immed.iloc[i]['duration'], 'x', fontsize=12, color='black')
    plt.savefig(os.path.join(output, f'{sub}_rt_acc_fuzzy_immed.png'))

        
def main():

    #parse command line arguments
    args = parse_cmd_args()
    submission = args.s
    output = args.o
    sub = args.sub

    # check if submission is a csv
    if not submission.endswith('.csv'):
        raise ValueError('Submission is not a csv')
    # check if submission exists
    if not os.path.exists(submission):
        raise ValueError('Submission does not exist')
    # run QC
    qc(submission)
    
    print(f'QC passed for {submission}, generating plots...')
    version = submission.split('_')[2]
    # generate plots
    plots(submission, output, sub, version)
    return submission, print('Plots generated')
    
    
if __name__ == '__main__':
    main()



    
    


