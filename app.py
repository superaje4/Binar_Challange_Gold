import re
import pandas as pd
import sqlite3

from flask import Flask, jsonify, request, render_template, redirect, url_for
from data_cleansing import processing_text

from flasgger import Swagger
from flasgger import swag_from

from data_reading_and_writing import create_table, insert_to_table, read_table

# create flask object
app = Flask(__name__, template_folder='templates')

swagger_config = {
    "headers": [],
    "specs": [{"endpoint":"docs", "route": '/docs.json'}],
    "static_url_path": "/flasgger_static",
    "swagger_ui":True,
    "specs_route":"/docs/"
}

swagger = Swagger(app,
                  config = swagger_config
                 )

TABLE_NAME = "tweet_cleaning"

@app.route('/', methods=['GET', "POST"])
def page_utama():
    if request.method == 'POST':
        insert = request.form['inputText']
        if insert == "1":
            return redirect(url_for("input_string_processing"))
        elif insert == "2":
            return redirect(url_for("input_file_processing"))
        elif insert == "3":
            return redirect(url_for("read_database"))
    else:
        return render_template("index_2.html")


@app.route('/text-processing',methods=['GET', 'POST'])
def input_string_processing():
    if request.method == 'POST':
        previous_text=request.form['inputText']
        cleaned_text=processing_text(previous_text)
        json_response={'previous_text': previous_text,
                       'cleaned_text': cleaned_text
                      }
        json_response=jsonify(json_response)
        return json_response
    else:
        return render_template("input_processing.html")

@app.route('/file-processing',methods=['GET', 'POST'])
def input_file_processing():
    if request.method == 'POST':
        input_file = request.files['inputFile']
        df = pd.read_csv(input_file, encoding='latin1')
        if("Tweet" in df.columns):
            list_of_tweets = df['Tweet'] #yang dari CSV
            list_of_cleaned_tweet = df['Tweet'].apply(lambda x: processing_text(x)) #ini yang hasil cleaning-an

            create_table()
            for previous_text, cleaned_text in zip(list_of_tweets, list_of_cleaned_tweet): # disini di-looping barengan
                insert_to_table(value_1=previous_text, value_2=cleaned_text)
            
            json_response={'list_of_tweets': list_of_tweets[0],
                           'list_of_cleaned_tweet': list_of_cleaned_tweet[0]
                          }
            json_response=jsonify(json_response)
            return json_response
        else:
            json_response={'ERROR_WARNING': "NO COLUMNS 'Tweet' APPEAR ON THE UPLOADED FILE"}
            json_response = jsonify(json_response)
            return json_response
        return json_response
    else:
        return render_template("file_processing.html")

@app.route('/read-database',methods=['GET', 'POST'])
def read_database():
    if request.method == "POST":
        global showed_index
        global showed_keywords
        showed_index=request.form['inputIndex']
        showed_keywords = request.form['inputKeywords']
        if len(showed_index)>0:
            return redirect(url_for("describe_database_index"))
        elif len(showed_keywords)>0:
            return redirect(url_for("describe_database_keyword"))
        else:
            print("CCCCCCCC")
            json_response={'ERROR_WARNING': "INDEX OR KEYWORDS IS NONE"}
            json_response = jsonify(json_response)
            return json_response
    else:
        return render_template("read_database.html")

@app.route('/describe_database',methods=['GET','POST'])
def describe_database_index():
    if request.method=='POST':
        page=request.form["inputText"]
        if page=="1":
            print("AAA")
            result_from_reading_database = read_table(target_index=showed_index)
            previous_text=result_from_reading_database[0].decode('latin1')
            cleaned_text=result_from_reading_database[1].decode('latin1')
            json_response={'Index': showed_index,
                           'Previous_text': previous_text,
                           'Cleaned_text': cleaned_text

                          }
            json_response = jsonify(json_response)
            return json_response
        elif page=="2":
            print("BBBBBBBBB")
            result_from_reading_database = read_table(target_index=showed_index)
            previous_text=result_from_reading_database[0].decode('latin1')
            cleaned_text=result_from_reading_database[1].decode('latin1')
            json_response={'showed_keywords': showed_index,
                           'previous_text_length':len(" ".join(previous_text)),
                           'number_of_words' : len(previous_text),
                           'cleaned_text_length': len(" ".join(cleaned_text)),
                           'number_of_words': len(cleaned_text)
                           }
            json_response = jsonify(json_response)
            return json_response
    else:
        return render_template("describe_database_index.html")


@app.route('/describe_database_keyword',methods=['GET','POST'])
def describe_database_keyword():
    if request.method=='POST':
        page=request.form["inputText"]
        if page=="1":
            results = read_table(target_keywords=showed_keywords)
            json_response={'showed_keywords': showed_keywords,
                           'previous_text':[result.decode("latin1") for result in results[0]],
                           'cleaned_text': [result.decode("latin1") for result in results[1]]
                          }
            json_response = jsonify(json_response)
            return json_response
        elif page=="2":
            results = read_table(target_keywords=showed_keywords)
            previous_text=[result.decode("latin1") for result in results[0]]
            cleaned_text=[result.decode("latin1") for result in results[1]]
            json_response={'showed_keywords': showed_keywords,
                           'previous_text_length': len(" ".join(previous_text)),
                           'number_of_words': len(previous_text),
                           'cleaned_text_length': len(" ".join(cleaned_text)),
                           'number_of_words': len(cleaned_text)
                          }
            json_response=jsonify(json_response)
            return json_response
    else:
        return render_template("describe_database_keyword.html")

if __name__ == '__main__':
    app.run(debug=True)
