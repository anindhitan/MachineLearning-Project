# -*- coding: utf-8 -*-
"""NLP TensorFlow Anindhita

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1cbzJ-0SpkLmoEOwZ_8cGMGQ4-E8CSpAf

Nama : Anindhita Nisitasari

# Intro and Importing Dataset
"""

from google.colab import files
import io

# dataframe
import pandas as pd
import re


# split data
from sklearn.model_selection import train_test_split

# preprocessing dan layer
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import LSTM,Dense,Embedding,Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam

# visualisasi plot
import matplotlib.pyplot as plt

! chmod 600 /content/kaggle.json

! KAGGLE_CONFIG_DIR=/content/ kaggle datasets download -d hgultekin/bbcnewsarchive

import zipfile
zip_file = zipfile.ZipFile('/content/bbcnewsarchive.zip', 'r')
zip_file.extractall('/tmp/')

df = pd.read_csv("/tmp/bbc-news-data.csv", sep='\t')
df.head()

# total data
df.shape

# Mengecek apakah ada nilai Null
df.isnull().sum()

# cek memory usage
print(df.info())

# Kategori
df.category.value_counts()

# Menghapus kolom yang tidak digunakan
df = df.drop(columns=['filename'])
df

#menggabungkan column title dan content
df['text'] = df['title'] + " " + df['content']
df

"""# DATA CLEANING"""

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize,sent_tokenize
from bs4 import BeautifulSoup
import re,string,unicodedata
from sklearn.metrics import classification_report,confusion_matrix,accuracy_score
from sklearn.model_selection import train_test_split
from string import punctuation
from nltk import pos_tag
from nltk.corpus import wordnet
import keras
from keras.preprocessing import text, sequence
import nltk
nltk.download('stopwords')

#Deleting Stopwords

stwd = set(stopwords.words('english'))
punctuation = list(string.punctuation)
stwd.update(punctuation)

# data cleaning
def strip_html(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()

#deleting square brackets
def remove_between_square_brackets(text):
    return re.sub('\[[^]]*\]', '', text)
#deleting URL's
def remove_url(text):
    return re.sub(r'http\S+', '', text)
#deleting stopwords dari text
def remove_stopwords(text):
    final_text = []
    for i in text.split():
        if i.strip().lower() not in stwd:
            final_text.append(i.strip())
    return " ".join(final_text)
#deleting noisy text
def denoise_text(text):
    text = strip_html(text)
    text = remove_between_square_brackets(text)
    text = remove_url(text)
    text = remove_stopwords(text)
    return text
#Apply function on review column
df['text']=df['text'].apply(denoise_text)

"""# Encoding and Splitting Data"""

# data category one-hot-encoding
category = pd.get_dummies(df.category)
new_cat = pd.concat([df, category], axis=1)
new_cat = new_cat.drop(columns='category')
new_cat.head(10)

# change dataframe value to numpy array
news = new_cat['text'].values
label = new_cat[['business', 'entertainment', 'politics', 'sport', 'tech']].values

news

label

"""# SPLIT DATASET"""

x_train,x_test,y_train,y_test = train_test_split(news, label,test_size = 0.2,shuffle=True)

"""# Tokenizer and Sequential Model with Embedding and LSTM"""

vocab_size = 10000
max_len = 200
trunc_type = "post"
oov_tok = ""

tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_tok)
tokenizer.fit_on_texts(x_train)

word_index = tokenizer.word_index

sequences_train = tokenizer.texts_to_sequences(x_train)
sequences_test = tokenizer.texts_to_sequences(x_test)
pad_train = pad_sequences(sequences_train, maxlen=max_len, truncating=trunc_type)
pad_test = pad_sequences(sequences_test, maxlen=max_len, truncating=trunc_type)

print(pad_test.shape)

pad_train

pad_test

# model
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(input_dim=vocab_size, output_dim=64, input_length=max_len),
    tf.keras.layers.LSTM(128),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(5, activation='softmax')
])
model.compile(optimizer='adam', metrics=['accuracy'], loss='categorical_crossentropy',)
model.summary()

# callback
class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy')>0.93 and logs.get('val_accuracy')>0.93):
      self.model.stop_training = True
      print("\n accuracy from training set and the validation set is fullfiled > 93%!")
callbacks = myCallback()

num_epochs = 50
history = model.fit(pad_train, y_train, epochs=num_epochs, 
                    validation_data=(pad_test, y_test), verbose=2, callbacks=[callbacks])

# plot of accuracy
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Accuracy Model')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train Process', 'Test Process'], loc='upper left')
plt.show()

# plot of loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Loss Model')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train Process', 'Test Process'], loc='upper left')
plt.show()