# -*- coding: utf-8 -*-
"""Sarcastic Comments.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/129-yhx0ARgaVqzZ8YqB0Mej5D-_U7_lk
"""

from google.colab import drive
drive.mount('/content/drive')

!ln -s /content/drive/MyDrive /mygdrive

!ls /mygdrive

!cp /mygdrive/Sarcasm_Headlines_Dataset_v2.json ./
!cp /mygdrive/Sarcasm_Headlines_Dataset.json ./

"""# Import Libraries"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
# %matplotlib inline
from matplotlib import pyplot as plt
import seaborn as sns
import re
from collections import Counter
from wordcloud import WordCloud, STOPWORDS
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve, confusion_matrix, auc, accuracy_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import pickle
import cv2
import tensorflow as tf
import tensorflow_hub as hub
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.callbacks import *
from tensorflow.keras import Model, Input, Sequential
from datetime import datetime
from tensorflow.keras import Input, Model
from tensorflow.keras.layers import *
from tensorflow.keras.utils import plot_model
from google.colab.patches import cv2_imshow
from tqdm import tqdm

tf.__version__, xgb.__version__, cv2.__version__, hub.__version__

"""# Load data"""

test = pd.read_json("Sarcasm_Headlines_Dataset.json", lines=True)
test.head()

test.info()

train = pd.read_json("Sarcasm_Headlines_Dataset_v2.json", lines=True)
train.head()

train.info()

plt.figure()
sns.countplot(data = train, x = "is_sarcastic")
plt.title("Class distribution")
plt.show()

def length(phrase):
  return len(phrase.split())

train["length"] = train["headline"].apply(length)
train.head()

plt.figure()
sns.displot(data = train, x = "length", kde = True)
plt.title("distribution of number of words in headlines")
plt.show()

for i in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
  print("{0}th percentile is {1}".format(i, np.percentile(train["length"], i)))
print()
for i in [90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100]:
  print("{0}th percentile is {1}".format(i, np.percentile(train["length"], i)))
print()
for i in [99, 99.10, 99.20, 99.30, 99.40, 99.50, 99.60, 99.70, 99.80, 99.90]:
  print("{0}th percentile is {1}".format(i, np.percentile(train["length"], i)))
print()

# Reference: https://stackoverflow.com/a/47091490/6645883

def decontracted(phrase):
    # specific
    phrase = re.sub(r"won\'t", "will not", phrase)
    phrase = re.sub(r"can\'t", "can not", phrase)

    # general
    phrase = re.sub(r"n\'t", " not", phrase)
    phrase = re.sub(r"\'re", " are", phrase)
    phrase = re.sub(r"\'s", " is", phrase)
    phrase = re.sub(r"\'d", " would", phrase)
    phrase = re.sub(r"\'ll", " will", phrase)
    phrase = re.sub(r"\'t", " not", phrase)
    phrase = re.sub(r"\'ve", " have", phrase)
    phrase = re.sub(r"\'m", " am", phrase)
    #phrase = re.sub(r"[^A-Za-z0-9 ]+", "", phrase)
    return phrase.lower()

train["headline"] = train["headline"].apply(decontracted)
test["headline"] = test["headline"].apply(decontracted)

# Reference: # https://www.geeksforgeeks.org/generating-word-cloud-python/

def wordcloud_plot(df):
  comment_words = ""
  stopwords = set(STOPWORDS)

  # iterate through the csv file
  for val in df.headline:
    
    # typecaste each val to string
    val = str(val)

    # split the value
    tokens = val.split()
    
    # Converts each token into lowercase
    for i in range(len(tokens)):
      tokens[i] = tokens[i].lower()
    
    comment_words += " ".join(tokens)+" "

  wordcloud = WordCloud(width = 800, height = 800,
          background_color = "white",
          stopwords = stopwords,
          min_font_size = 10).generate(comment_words)

  # plot the WordCloud image					
  plt.figure(figsize = (8, 8), facecolor = None)
  plt.imshow(wordcloud)
  plt.axis("off")
  plt.tight_layout(pad = 0)
  plt.show()

wordcloud_plot(train)

wordcloud_plot(test)

"""# BoW"""

vectorizer = CountVectorizer(min_df = 10, max_df = 5000, ngram_range = (1, 3))

vectorizer.fit(train["headline"])
x_train = vectorizer.transform(train["headline"])
x_test = vectorizer.transform(test["headline"])

y_train = train["is_sarcastic"]
y_test = test["is_sarcastic"]

x_train.shape, x_test.shape

"""### Logistic Regression"""

model = LogisticRegression(n_jobs = -1)
params = {"C" : [0.0001, .00033, .001, .0033, .01, .033, .1, .33, 1, 3.3, 10, 33, 100]}

gridsearch = GridSearchCV(model, params, cv = 5, scoring = "accuracy", return_train_score = True)
gridsearch.fit(x_train, y_train)

results = pd.DataFrame.from_dict(gridsearch.cv_results_)
results = results.sort_values(['param_C'])
results.head()

train_auc= results['mean_train_score']
train_auc_std= results['std_train_score']
cv_auc = results['mean_test_score']
cv_auc_std= results['std_test_score']
K = results['param_C']
plt.plot(K, train_auc, "bo-", label='Train accuracy')
plt.plot(K, cv_auc, "ro-", label='CV accuracy')
plt.xscale("log")
plt.legend()
plt.xlabel("C: hyperparameter")
plt.ylabel("accuracy")
plt.title("Hyper parameter Vs accuracy plot")
plt.grid()
plt.show()

model = LogisticRegression(C = 1, max_iter = 200)
model.fit(x_train, y_train)
y_pred = model.predict(x_test)
print("Accuracy:", 100*accuracy_score(y_test, y_pred))

cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot = True, fmt = "d")
plt.xlabel("predicted label")
plt.ylabel("actual label")
plt.title("test confusion matrix")
plt.show()

"""### Naive Bayes"""

model = MultinomialNB(class_prior = [.5, .5])
params = {"alpha" : [0.0001, .00033, .001, .0033, .01, .033, .1, .33, 1, 3.3, 10, 33, 100]}

gridsearch = GridSearchCV(model, params, cv = 5, scoring = "accuracy", return_train_score = True)
gridsearch.fit(x_train, y_train)

results = pd.DataFrame.from_dict(gridsearch.cv_results_)
results = results.sort_values(['param_alpha'])
results.head()

train_auc= results['mean_train_score']
train_auc_std= results['std_train_score']
cv_auc = results['mean_test_score']
cv_auc_std= results['std_test_score']
K = results['param_alpha']
plt.plot(K, train_auc, "bo-", label='Train accuracy')
plt.plot(K, cv_auc, "ro-", label='CV accuracy')
plt.xscale("log")
plt.legend()
plt.xlabel("alpha: hyperparameter")
plt.ylabel("accuracy")
plt.title("Hyper parameter Vs accuracy plot")
plt.grid()
plt.show()

model = MultinomialNB(alpha = .033)
model.fit(x_train, y_train)
y_pred = model.predict(x_test)
print("Accuracy:", 100*accuracy_score(y_test, y_pred))

cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot = True, fmt = "d")
plt.xlabel("predicted label")
plt.ylabel("actual label")
plt.title("test confusion matrix")
plt.show()

"""### Random Forest"""

# Commented out IPython magic to ensure Python compatibility.
# %%time
# 
# model = RandomForestClassifier()
# params = {"n_estimators" : [10, 50, 100, 150]}
# 
# gridsearch = GridSearchCV(model, params, 
#                           cv = 5, scoring = "accuracy", 
#                           return_train_score = True, 
#                           verbose = 1, n_jobs = -1)
# gridsearch.fit(x_train, y_train)

results = pd.DataFrame.from_dict(gridsearch.cv_results_)
results = results.sort_values(['param_n_estimators'])
results.head()

train_auc= results['mean_train_score']
train_auc_std= results['std_train_score']
cv_auc = results['mean_test_score']
cv_auc_std= results['std_test_score']
K = results['param_n_estimators']
plt.plot(K, train_auc, "bo-", label='Train accuracy')
plt.plot(K, cv_auc, "ro-", label='CV accuracy')
plt.legend()
plt.xlabel("number of trees: hyperparameter")
plt.ylabel("accuracy")
plt.title("Hyper parameter Vs accuracy plot")
plt.grid()
plt.show()

model = RandomForestClassifier(n_estimators = 50)
model.fit(x_train, y_train)
y_pred = model.predict(x_test)
print("Accuracy:", 100*accuracy_score(y_test, y_pred))

cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot = True, fmt = "d")
plt.xlabel("predicted label")
plt.ylabel("actual label")
plt.title("test confusion matrix")
plt.show()

"""### GBDT"""

model = xgb.XGBClassifier(verbosity = 1, use_label_encoder = False)
params = {"n_estimators" : [10, 50, 100, 150], 
          "max_depth" : [4, 8, 16, 32]}

gridsearch = GridSearchCV(model, params, 
                          cv = 5, scoring = "accuracy", 
                          return_train_score = True, 
                          verbose = 1, n_jobs = -1)
gridsearch.fit(x_train, y_train)

results = pd.DataFrame.from_dict(gridsearch.cv_results_)
results.head()

hmap = results.pivot("param_max_depth", "param_n_estimators", "mean_train_score")
sns.heatmap(hmap, linewidth = 1, annot = True)
plt.ylabel("max_depth")
plt.xlabel("n_estimators")
plt.title("train accuracy in heatmap")
plt.show()

hmap = results.pivot("param_max_depth", "param_n_estimators", "mean_test_score")
sns.heatmap(hmap, linewidth = 1, annot = True)
plt.ylabel("max_depth")
plt.xlabel("n_estimators")
plt.title("cv accuracy in heatmap")
plt.show()

model = xgb.XGBClassifier(n_estimators = 150, max_depth = 32, verbosity = 1, use_label_encoder = False)
model.fit(x_train, y_train)
y_pred = model.predict(x_test)
print("Accuracy:", 100*accuracy_score(y_test, y_pred))

cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot = True, fmt = "d")
plt.xlabel("predicted label")
plt.ylabel("actual label")
plt.title("test confusion matrix")
plt.show()

"""# TFIDF"""

vectorizer = TfidfVectorizer(min_df = 10, max_df = 5000, ngram_range = (1, 3))

vectorizer.fit(train["headline"])
x_train = vectorizer.transform(train["headline"])
x_test = vectorizer.transform(test["headline"])

y_train = train["is_sarcastic"]
y_test = test["is_sarcastic"]

x_train.shape, x_test.shape

"""### Logistic Regression"""

model = LogisticRegression(n_jobs = -1)
params = {"C" : [0.0001, .00033, .001, .0033, .01, .033, .1, .33, 1, 3.3, 10, 33, 100]}

gridsearch = GridSearchCV(model, params, cv = 5, scoring = "accuracy", return_train_score = True)
gridsearch.fit(x_train, y_train)

results = pd.DataFrame.from_dict(gridsearch.cv_results_)
results = results.sort_values(['param_C'])
results.head()

train_auc= results['mean_train_score']
train_auc_std= results['std_train_score']
cv_auc = results['mean_test_score']
cv_auc_std= results['std_test_score']
K = results['param_C']
plt.plot(K, train_auc, "bo-", label='Train accuracy')
plt.plot(K, cv_auc, "ro-", label='CV accuracy')
plt.xscale("log")
plt.legend()
plt.xlabel("C: hyperparameter")
plt.ylabel("accuracy")
plt.title("Hyper parameter Vs accuracy plot")
plt.grid()
plt.show()

model = LogisticRegression(C = 3.3, max_iter = 200)
model.fit(x_train, y_train)
y_pred = model.predict(x_test)
print("Accuracy:", 100*accuracy_score(y_test, y_pred))

cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot = True, fmt = "d")
plt.xlabel("predicted label")
plt.ylabel("actual label")
plt.title("test confusion matrix")
plt.show()

"""### Naive Bayes"""

model = MultinomialNB(class_prior = [.5, .5])
params = {"alpha" : [0.0001, .00033, .001, .0033, .01, .033, .1, .33, 1, 3.3, 10, 33, 100]}

gridsearch = GridSearchCV(model, params, cv = 5, scoring = "accuracy", return_train_score = True)
gridsearch.fit(x_train, y_train)

results = pd.DataFrame.from_dict(gridsearch.cv_results_)
results = results.sort_values(['param_alpha'])
results.head()

train_auc= results['mean_train_score']
train_auc_std= results['std_train_score']
cv_auc = results['mean_test_score']
cv_auc_std= results['std_test_score']
K = results['param_alpha']
plt.plot(K, train_auc, "bo-", label='Train accuracy')
plt.plot(K, cv_auc, "ro-", label='CV accuracy')
plt.xscale("log")
plt.legend()
plt.xlabel("alpha: hyperparameter")
plt.ylabel("accuracy")
plt.title("Hyper parameter Vs accuracy plot")
plt.grid()
plt.show()

model = MultinomialNB(alpha = .01)
model.fit(x_train, y_train)
y_pred = model.predict(x_test)
print("Accuracy:", 100*accuracy_score(y_test, y_pred))

cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot = True, fmt = "d")
plt.xlabel("predicted label")
plt.ylabel("actual label")
plt.title("test confusion matrix")
plt.show()

"""### Random Forest"""

# Commented out IPython magic to ensure Python compatibility.
# %%time
# 
# model = RandomForestClassifier()
# params = {"n_estimators" : [10, 50, 100, 150]}
# 
# gridsearch = GridSearchCV(model, params, 
#                           cv = 5, scoring = "accuracy", 
#                           return_train_score = True, 
#                           verbose = 1, n_jobs = -1)
# gridsearch.fit(x_train, y_train)

results = pd.DataFrame.from_dict(gridsearch.cv_results_)
results = results.sort_values(['param_n_estimators'])
results.head()

train_auc= results['mean_train_score']
train_auc_std= results['std_train_score']
cv_auc = results['mean_test_score']
cv_auc_std= results['std_test_score']
K = results['param_n_estimators']
plt.plot(K, train_auc, "bo-", label='Train accuracy')
plt.plot(K, cv_auc, "ro-", label='CV accuracy')
plt.legend()
plt.xlabel("number of trees: hyperparameter")
plt.ylabel("accuracy")
plt.title("Hyper parameter Vs accuracy plot")
plt.grid()
plt.show()

model = RandomForestClassifier(n_estimators = 50)
model.fit(x_train, y_train)
y_pred = model.predict(x_test)
print("Accuracy:", 100*accuracy_score(y_test, y_pred))

cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot = True, fmt = "d")
plt.xlabel("predicted label")
plt.ylabel("actual label")
plt.title("test confusion matrix")
plt.show()

"""### GBDT"""

model = xgb.XGBClassifier(verbosity = 1, use_label_encoder = False)
params = {"n_estimators" : [10, 50, 100, 150], 
          "max_depth" : [4, 8, 16, 32]}

gridsearch = GridSearchCV(model, params, 
                          cv = 5, scoring = "accuracy", 
                          return_train_score = True, 
                          verbose = 1, n_jobs = -1)
gridsearch.fit(x_train, y_train)

results = pd.DataFrame.from_dict(gridsearch.cv_results_)
results.head()

hmap = results.pivot("param_max_depth", "param_n_estimators", "mean_train_score")
sns.heatmap(hmap, linewidth = 1, annot = True)
plt.ylabel("max_depth")
plt.xlabel("n_estimators")
plt.title("train accuracy in heatmap")
plt.show()

hmap = results.pivot("param_max_depth", "param_n_estimators", "mean_test_score")
sns.heatmap(hmap, linewidth = 1, annot = True)
plt.ylabel("max_depth")
plt.xlabel("n_estimators")
plt.title("test accuracy in heatmap")
plt.show()

model = xgb.XGBClassifier(n_estimators = 150, max_depth = 32, verbosity = 1, use_label_encoder = False)
model.fit(x_train, y_train)
y_pred = model.predict(x_test)
print("Accuracy:", 100*accuracy_score(y_test, y_pred))

cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot = True, fmt = "d")
plt.xlabel("predicted label")
plt.ylabel("actual label")
plt.title("test confusion matrix")
plt.show()

"""# Deep learning"""

label_encoder = OneHotEncoder()

label_encoder.fit(np.array(train["is_sarcastic"]).reshape(-1, 1))
y_train_ohe = label_encoder.transform(np.array(train["is_sarcastic"]).reshape(-1, 1))
y_test_ohe = label_encoder.transform(np.array(test["is_sarcastic"]).reshape(-1, 1))

y_train_ohe.shape, y_test_ohe.shape

with open("/mygdrive/glove_vectors", "rb") as fi:
  glove_model = pickle.load(fi)
  glove_words = set(glove_model.keys())

t = Tokenizer()
t.fit_on_texts(train["headline"])

encoded_train = t.texts_to_sequences(train["headline"])
encoded_test = t.texts_to_sequences(test["headline"])

max_length = 25

padded_train = pad_sequences(encoded_train, 
                             maxlen = max_length, 
                             padding = "post", 
                             truncating = "post")

padded_test = pad_sequences(encoded_test, 
                            maxlen = max_length, 
                            padding = "post", 
                            truncating = "post")

print(padded_train.shape, padded_test.shape, type(padded_train))

vocab_size = len(t.word_index) + 1
vocab_size

embedding_matrix = np.zeros((vocab_size, 300)) # vector len of each word is 300

for word, i in t.word_index.items():
  if word in glove_words:
    vec = glove_model[word]
    embedding_matrix[i] = vec

embedding_matrix.shape

"""### callbacks"""

# Commented out IPython magic to ensure Python compatibility.
# %load_ext tensorboard

def checkpoint_path():
  return "./model/weights.{epoch:02d}-{val_accuracy:.4f}.hdf5"

def log_dir():
  return "./logs/fit/" + datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

earlystop = EarlyStopping(monitor = "val_accuracy", 
                          patience = 7, 
                          verbose = 1,  
                          restore_best_weights = True, 
                          mode = 'max')

reduce_lr = ReduceLROnPlateau(monitor = "val_accuracy", 
                              factor = .4642,
                              patience = 3,
                              verbose = 1, 
                              min_delta = 0.001,
                              mode = 'max')

"""### model building"""

tf.keras.backend.clear_session()
input = Input(shape = (max_length, ), name = "input")

embedding = Embedding(input_dim = vocab_size, 
                      output_dim = 300, # glove vector size
                      weights = [embedding_matrix], 
                      trainable = False)(input)

lstm = LSTM(32)(embedding)
flatten = Flatten()(lstm)

dense = Dense(16, activation = None, 
              kernel_initializer = "he_uniform")(flatten)

dropout = Dropout(.25)(dense)
activation = Activation("relu")(dropout)
output = Dense(2, activation = "softmax", name = "output")(activation)
model = Model(inputs = input, outputs = output)

model.compile(optimizer = "adam", loss = "sparse_categorical_crossentropy", metrics = ["accuracy"])

plot_model(model, to_file = "./model.png", show_shapes = True)

model.summary()

cv2_imshow(cv2.imread("./model.png"))

# Commented out IPython magic to ensure Python compatibility.
!rm -rf ./logs/
# %tensorboard --logdir logs/fit

"""### training model"""

tensorboard_callback = TensorBoard(log_dir = log_dir(), 
                                   histogram_freq = 1, 
                                   write_images = True)

checkpoint = ModelCheckpoint(filepath = checkpoint_path(), 
                             monitor='val_accuracy', 
                             verbose = 1, 
                             save_best_only = True, 
                             mode = "max")

callbacks_list = [checkpoint, tensorboard_callback, earlystop, reduce_lr]

history = model.fit(padded_train, y_train, 
                    validation_data = (padded_test, y_test), 
                    epochs = 30, 
                    batch_size = 32, 
                    callbacks = callbacks_list)

plt.figure()
L = len(history.history["loss"]) + 1
plt.plot(range(1, L), history.history["loss"], "bo-", label = "loss")
plt.plot(range(1, L), history.history["accuracy"], "g*-", label = "accuracy")
plt.plot(range(1, L), history.history["val_loss"], "y^-", label = "val_loss")
plt.plot(range(1, L), history.history["val_accuracy"], "ro-", label = "val_accuracy")
plt.legend()
plt.xlabel("epoch")
plt.grid()
plt.show()

"""### testing model"""

y_pred_softmax = model.predict(padded_test)
y_pred = []
for i in range(len(y_pred_softmax)):
  if  y_pred_softmax[i][0] >= 0.5:
    y_pred.append(0)
  else:
    y_pred.append(1)


print("Accuracy:", 100*accuracy_score(y_test, y_pred))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot = True, fmt = "d")
plt.xlabel("predicted label")
plt.ylabel("actual label")
plt.title("test confusion matrix")
plt.show()

"""# BERT encodings

### creating BERT model
"""

max_length = 27

tf.keras.backend.clear_session()

input_word_ids = Input(shape = (max_length,), dtype = tf.int32, name = "input_word_ids")
input_mask = Input(shape = (max_length,), dtype = tf.int32, name = "input_mask")
segment_ids = Input(shape = (max_length,), dtype = tf.int32, name = "segment_ids")
bert_layer = hub.KerasLayer("https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/1", trainable = False)
pooled_output, sequence_output = bert_layer([input_word_ids, input_mask, segment_ids])
bert_model = Model(inputs = [input_word_ids, input_mask, segment_ids], outputs = pooled_output)

bert_model.summary()

bert_model.output

"""### tokenization"""

vocab_file = bert_layer.resolved_object.vocab_file.asset_path.numpy()
do_lower_case = bert_layer.resolved_object.do_lower_case.numpy()

!pip install sentencepiece
from tokenization import FullTokenizer

tokenizer = FullTokenizer(vocab_file, do_lower_case)

def my_tokens_util(series, max_length): 
  x_tokens = np.zeros((series.shape[0], max_length))
  x_mask = np.ones((series.shape[0], max_length))
  x_segment = np.zeros((series.shape[0], max_length))
  for i in range(series.shape[0]): 
    tokens = tokenizer.tokenize(series.values[0])
    if len(tokens) >= max_length - 2:
      tokens = tokens[: (max_length - 2)]
    tokens = ["[CLS]", *tokens, "[SEP]"]
    pe_tokens = np.array(tokenizer.convert_tokens_to_ids(tokens))
    length = len(tokens)
    if length >= max_length:
      x_tokens[i] = pe_tokens[:max_length]
    else:
      x_tokens[i, :length] = pe_tokens
      x_mask[i, length:] = list(np.zeros(max_length - length))
  
  return np.array(series), x_tokens, x_mask, x_segment

X_train, X_train_tokens, X_train_mask, X_train_segment = my_tokens_util(train["headline"], max_length)
X_test, X_test_tokens, X_test_mask, X_test_segment = my_tokens_util(test["headline"], max_length)

pickle.dump((X_train, X_train_tokens, X_train_mask, X_train_segment, y_train),open('/mygdrive/train_data.pkl','wb'))
pickle.dump((X_test, X_test_tokens, X_test_mask, X_test_segment, y_test),open('/mygdrive/test_data.pkl','wb'))

X_train, X_train_tokens, X_train_mask, X_train_segment, y_train = pickle.load(open("/mygdrive/train_data.pkl", 'rb'))
X_test, X_test_tokens, X_test_mask, X_test_segment, y_test = pickle.load(open("/mygdrive/test_data.pkl", 'rb'))

"""### embeddings from BERT model"""

X_train_pooled_output = bert_model.predict([X_train_tokens, X_train_mask, X_train_segment])
X_test_pooled_output = bert_model.predict([X_test_tokens, X_test_mask, X_test_segment])

pickle.dump((X_train_pooled_output, X_test_pooled_output),open('/mygdrive/final_output.pkl','wb'))

X_train_pooled_output, X_test_pooled_output = pickle.load(open('/mygdrive/final_output.pkl', 'rb'))

X_train_pooled_output.shape, X_test_pooled_output.shape, y_train.shape, y_test.shape

scaler = StandardScaler()

scaler.fit(X_train_pooled_output)
x_train = scaler.transform(X_train_pooled_output)
x_test = scaler.transform(X_test_pooled_output)

x_train.shape, x_test.shape

"""### training a NN with 768 features"""

tf.keras.backend.clear_session()
model = Sequential()
model.add(Dense(128, activation = "relu", kernel_initializer = "he_uniform", input_shape = (768, )))
model.add(Dropout(.5))
model.add(Dense(32, activation = "relu", kernel_initializer = "he_uniform"))
model.add(Dropout(.5))
model.add(Dense(2, activation = "softmax"))
model.compile(loss = "sparse_categorical_crossentropy", optimizer = "adam", metrics = ["accuracy"])
plot_model(model, to_file = "./model.png", show_shapes = True)

model.summary()

cv2_imshow(cv2.imread("./model.png"))

# Commented out IPython magic to ensure Python compatibility.
# %tensorboard --logdir logs/fit

tensorboard_callback = TensorBoard(log_dir = log_dir(), 
                                   histogram_freq = 1, 
                                   write_images = True)

checkpoint = ModelCheckpoint(filepath = checkpoint_path(), 
                             monitor='val_accuracy', 
                             verbose = 1, 
                             save_best_only = True, 
                             mode = "max")

callbacks_list = [checkpoint, tensorboard_callback, earlystop, reduce_lr]

history = model.fit(x_train, y_train, 
                    validation_data = (x_test, y_test), 
                    epochs = 30, 
                    batch_size = 32, 
                    callbacks = callbacks_list)

plt.figure()
L = len(history.history["loss"]) + 1
plt.plot(range(1, L), history.history["loss"], "bo-", label = "loss")
plt.plot(range(1, L), history.history["accuracy"], "g*-", label = "accuracy")
plt.plot(range(1, L), history.history["val_loss"], "y^-", label = "val_loss")
plt.plot(range(1, L), history.history["val_accuracy"], "ro-", label = "val_accuracy")
plt.legend()
plt.xlabel("epoch")
plt.grid()
plt.show()

"""### testing model"""

y_pred_softmax = model.predict(x_test)
y_pred = []
for i in range(len(y_pred_softmax)):
  if  y_pred_softmax[i][0] >= 0.5:
    y_pred.append(0)
  else:
    y_pred.append(1)


print("Accuracy:", 100*accuracy_score(y_test, y_pred))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot = True, fmt = "d")
plt.xlabel("predicted label")
plt.ylabel("actual label")
plt.title("test confusion matrix")
plt.show()