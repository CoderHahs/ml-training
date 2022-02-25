# Introduction

# Dataset

-   Describe what part of the dataset you will use

## About the Dataset

The dataset that was used was _Paraphrase and Semantic Similarity in Twitter_. This was a dataset used in an international competition at SemEval 2015. This was a workshop on Semantic Evaluation.

The dataset has multiple examples of two sentence inputs. A panel of five judges examined these two inputs and determined if they are paraphrases of each other or not. The decision of the judges was also provided in terms of votes. For example if three judges voted saying the two inputs are paraphrases and the other two did not, then the provided decision was `(3,2)`.

The entire dataset was used for the assignment. The dataset curator did suggest that inputs that have a "debatable" decision like `(3,2)` or `(2,3)` can be removed from any training and testing so that there is no uncertainty present in the training data. However, I chose to keep it in so that there would be more data to train on.

-   Give your method for changing from graded evaluations to binary (you don’t
    have to follow what is mentioned on the github page, you can decide what
    you want)

# Converting Votes to a Binary Class

The method used to convert graded evaluations, the decisions made by judges, into a binary classification was relatively simple. The binary classification was decided based on majority. If there was a greater number of positive votes in favor of "paraphrase" then the class "P" was assigned. The converse is also true and the class "NP" was assigned in this case.

The below code was used to assign the new class. The previous votes were also tracked.

```py
c = []
p_votes = []
n_votes = []
for row in train_data.iterrows():
    row = row[1]
    p_votes.append(row['Label'][1])
    n_votes.append(row['Label'][4])
    if (int(row['Label'][1]) > int(row['Label'][4])):
        c.append("P")
    else:
        c.append("NP")

train_data['Class'] = c
train_data['Positive votes'] = p_votes
train_data['Negative votes'] = n_votes
```

Here are some examples of paraphrases ("P") and non-paraphrases ("NP"):

|     |                               Sentence 1 |                                        Sentence 2 | Class |
| --: | ---------------------------------------: | ------------------------------------------------: | ----- |
|   0 | EJ Manuel the 1st QB to go in this draft | But my bro from the 757 EJ Manuel is the 1st Q... | P     |
|   1 | EJ Manuel the 1st QB to go in this draft | Can believe EJ Manuel went as the 1st QB in th... | P     |
|   2 | EJ Manuel the 1st QB to go in this draft |                      EJ MANUEL IS THE 1ST QB what | P     |
|   4 | EJ Manuel the 1st QB to go in this draft |               Manuel is the 1st QB to get drafted | P     |
|   5 | EJ Manuel the 1st QB to go in this draft |                         EJ da 1st QB off da board | NP    |
|   6 |     EJ Manuel is the 1st QB in the draft |                            1st QB of the board is | NP    |
|   7 |     EJ Manuel is the 1st QB in the draft | Bills take EJ Manuel QBFlorida State 1st QB of... | NP    |
|   8 |     EJ Manuel is the 1st QB in the draft | EJ Manuel 1st QB off the board taken by the Bills | NP    |
|   9 |     EJ Manuel is the 1st QB in the draft |                      Lol and 1st QB off the board | NP    |

# Methods

To predict if two sentence inputs are paraphrases or not, three different methods were used. The first was designated as the baseline algorithm as it was relatively simple and did not use any classification algorithms. The second and third algorithm are similar in terms of the classification algorithm that was employed, however the features used to train the model were different.

-   Describe your baseline algorithm, provide an example to illustrate what it
    does

## Baseline Algorithm

The baseline approach is straightforward. Each input sentence is transformed into lowercase form, and then the sentence is split into an array of words. The array is then converted into a set, so duplicate words are removed. Then the number of common words between the two sentences is found. This number if multiplied by two, since it occurs in the first sentence set as well as the second sentence set. It is then divide by the total number of words of the two sentences. When divided, if the output is greater than or equal to 0.5, then the sentences are classified as paraphrases of each other. Otherwise they are classified as non-paraphrases.

Here is the code that does what is described above:

```py
def baseline(input1, input2):
    pred = []
    for row in zip(input1, input2):
        words1 = set(row[0].lower().split())
        words2 = set(row[1].lower().split())
        same = words1.intersection(words2)
        score = 2*len(same)/(len(words1) + len(words2))
        if score >= 0.5:
            pred.append('P')
        else:
            pred.append('NP')
    return pred
```

An example of the baseline approach is as follows:

1. Sentence 1 = "There was a motorist crossing the intersection", Sentence 2 = "A car was crossing the intersection"
2. The sentences is transformed to lowercase and split up. Sentence 1 = ['there', 'was, 'a', 'motorist', 'crossing', 'the', 'intersection'], Sentence 2 = ['a', 'car', 'was', 'crossing', 'the', 'intersection']
3. The intersection of the two sentences becomes ['a', 'was', 'crossing', 'the', 'intersection']
4. The score is calculated as `2*(number of common words) / total number of words in two sentences = 2*5/13 = 0.77`.
5. Given the score, the two sentences would be classified as paraphrases as one another.

-   Describe your method 1 algorithm, also provide an example
-   Describe your method 2 algorithm, also provide an example

# Results

# Conclusion

# References
