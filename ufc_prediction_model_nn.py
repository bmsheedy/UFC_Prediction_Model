"""
---UFC Prediction Model---
-----------------------------------------------------------------------------------------------------------------------
Utilizes database collected by the asychronous ufc webscraper.
Processes data and places key statistics into datasets.
Builds a neural network using Keras to achieve upwards of 70% accuracy at current. 
-----------------------------------------------------------------------------------------------------------------------
---Created by Brandon Sheedy---
"""

import pandas as pd
import time
import csv
import numpy as np
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense


def build_name_dict(seq, key):
    return dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq))


def data_cleaner():
    # Processing data collected from the web scraper.
    fighter_data = pd.read_csv('fighter_data.csv')
    fight_data = pd.read_csv('fight_data.csv', encoding="ISO-8859-1")

    fighter_data_dict = fighter_data.to_dict('records')
    fight_data_dict = fight_data.to_dict('records')

    dict_by_name = build_name_dict(fighter_data_dict, key="name")

    # Collecting key data from each fighter from every fight (subject to change).
    for fight in fight_data_dict:
        red_fighter = dict_by_name.get(fight['RED Fighter'])
        red_good = True
        blue_good = True
        if red_fighter['height (in)'] != '--' and red_fighter['reach (in)'] != '--' and red_fighter['age'] != '--' and red_fighter['Sig. Strikes Landed per min.'] != '0':
            fight['red height'] = red_fighter['height (in)']
            fight['red reach'] = red_fighter['reach (in)']
            fight['red weight'] = red_fighter['weight (lbs)']
            fight['red age'] = red_fighter['age']
            fight['red sig str landed per min'] = red_fighter['Sig. Strikes Landed per min.']
            fight['red str acc'] = red_fighter['Striking Accuracy (%)']
            fight['red sig str absorbed per min'] = red_fighter['Sig. Strikes Absorbed per min.']
            fight['red str def'] = red_fighter['Striking Defense (%)']
            fight['red td avg'] = red_fighter['TD Avg. per 15 min']
            fight['red td acc'] = red_fighter['Takedown Accuracy (%)']
            fight['red td def'] = red_fighter['Takedown Defense (%)']
            fight['red sub att avg'] = red_fighter['Sub. Attempt Avg. per 15 min (%)']
        else:
            red_good = False

        if red_good:
            blue_fighter = dict_by_name.get(fight['BLUE Fighter'])
            if blue_fighter['height (in)'] != '--' and blue_fighter['reach (in)'] != '--' and blue_fighter['age'] != '--' and blue_fighter['Sig. Strikes Landed per min.'] != '0':
                fight['blue height'] = blue_fighter['height (in)']
                fight['blue reach'] = blue_fighter['reach (in)']
                fight['blue weight'] = blue_fighter['weight (lbs)']
                fight['blue age'] = blue_fighter['age']
                fight['blue sig str landed per min'] = blue_fighter['Sig. Strikes Landed per min.']
                fight['blue str acc'] = blue_fighter['Striking Accuracy (%)']
                fight['blue sig str absorbed per min'] = blue_fighter['Sig. Strikes Absorbed per min.']
                fight['blue str def'] = blue_fighter['Striking Defense (%)']
                fight['blue td avg'] = blue_fighter['TD Avg. per 15 min']
                fight['blue td acc'] = blue_fighter['Takedown Accuracy (%)']
                fight['blue td def'] = blue_fighter['Takedown Defense (%)']
                fight['blue sub att avg'] = blue_fighter['Sub. Attempt Avg. per 15 min (%)']
            else:
                blue_good = False

        # Winner of each fight (key for training the model).
        if red_good and blue_good:
            if fight['Winner'] == fight['RED Fighter']:
                fight['Winner ID'] = 0
            else:
                fight['Winner ID'] = 1

    fight_data_dict[:] = [x for x in fight_data_dict if len(x) > 16]

    keys = fight_data_dict[0].keys()
    with open('fight_data_updated.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(fight_data_dict)


def create_neural_network_model():
    
    # Preparing the dataset.
    data_frame = pd.read_csv('fight_data_updated.csv', encoding="ISO-8859-1")
    dataset = data_frame.values

    x = dataset[:, 4:28]
    y = dataset[:, 28]

    x = np.asarray(x).astype(np.float32)
    y = np.asarray(y).astype(np.float32)

    print(x)
    print(y)
    
    # Normalizing data.
    min_max_scaler = preprocessing.MinMaxScaler()
    x_scale = min_max_scaler.fit_transform(x)

    print(x_scale)

    # Splitting data into training and testing sets.
    x_train, x_val_and_test, y_train, y_val_and_test = train_test_split(x_scale, y, test_size=0.3)
    x_val, x_test, y_val, y_test = train_test_split(x_val_and_test, y_val_and_test, test_size=0.5)
    print(x_train.shape, x_val.shape, x_test.shape, y_train.shape, y_val.shape, y_test.shape)

    # Model architecture.
    model = Sequential([
        Dense(256, activation='relu', input_shape=(24,)),
        Dense(256, activation='relu'),
        Dense(1, activation='sigmoid'),
    ])

    # Compilation.
    model.compile(optimizer='sgd',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    # Training the model with validation.
    model.fit(x_train, y_train, batch_size=32, epochs=200, validation_data=(x_val, y_val))

    # Model evaluation, prints accuracy.
    model.evaluate(x_test, y_test)[1]


if __name__ == "__main__":
    start_time = time.time()

    data_cleaner()
    # Call custom analytics function here.
    create_neural_network_model()
    
    print(time.time() - start_time)
