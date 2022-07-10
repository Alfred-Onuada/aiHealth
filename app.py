# import required packages
from flask import Flask, request, jsonify ,render_template
from flask_cors import CORS
import pymongo
from pymongo.server_api import ServerApi
import urllib
import json

app = Flask(__name__)

# activate cors middleware
CORS(app)

DB_URI = "mongodb+srv://wiz-js:" + urllib.parse.quote("kY@79ZBJhg@Wa8D") + "@jobs-cluster.ats2ndt.mongodb.net/admin?retryWrites=true&w=majority"

try:
    DB_CLIENT = pymongo.MongoClient(DB_URI, serverSelectionTimeoutMS=5000, server_api= ServerApi('1'))

    diseasesDB = DB_CLIENT.get_database('diseasesDB')
    diseasesCollection = diseasesDB.get_collection('diseases')

    # html rendering routes
    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/symptoms')
    def symptoms():
        return render_template('symptoms.html')

    @app.route('/disease')
    def disease():
        return render_template('disease.html')

    @app.route('/common_symptoms')
    def common_symptoms():
        return render_template('common_symptoms.html')

    # api routes
    @app.route('/get_disease', methods=['GET'])
    def get_disease():
        symptoms = request.args.get('symptoms').split(',')

        if len(symptoms) == 0:
            return jsonify({ "status": 400 })
        
        Pipeline = [
            {
                "$match": {
                    "symptoms": { "$all": symptoms }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "symptoms": 0
                }
            }
        ]

        cursor = None

        try:
            cursor = diseasesCollection.aggregate(Pipeline)

            matchingDiseases = []

            while cursor._has_next():
                matchingDiseases.append(cursor.next())

            if len(matchingDiseases) == 0:
                return jsonify({ "status": 404 })

            return jsonify({ "status": 200, "matches": matchingDiseases })
        except:
            return jsonify({ "status": 500 })
        finally:
            if cursor:
                cursor.close()


        
    @app.route('/get_symptoms', methods=['GET'])
    def get_symptoms():
        diseaseToFind = request.args.get('disease')

        try:
            symptoms = diseasesCollection.find_one({ "disease": diseaseToFind }, { "_id": 0, "disease": 0 })

            if symptoms is None:
                return jsonify({ "status": 404 })
            else:
                return jsonify({ "status": 200, "symptoms": symptoms })
        except:
            return jsonify({ "status": 500 })



    @app.route('/get_disease_similarities', methods=['GET'])
    def get_disease_similarities():
        diseasesToCompare = request.args.get('diseases').split(",")

        Pipeline = [
            {
                '$match': {
                    'disease': {
                        '$in': diseasesToCompare
                    }
                }
            }, {
                '$group': {
                    '_id': None, 
                    'symptoms': {
                        '$push': '$symptoms'
                    }, 
                    'first_doc': {
                        '$first': '$symptoms'
                    }, 
                    'count': {
                        '$sum': 1
                    }
                }
            }, {
                '$match': {
                    '$expr': {
                        '$eq': [
                            '$count', len(diseasesToCompare)
                        ]
                    }
                }
            }, {
                '$addFields': {
                    'common_symptoms': {
                        '$reduce': {
                            'input': '$symptoms', 
                            'initialValue': '$first_doc', 
                            'in': {
                                '$setIntersection': [
                                    '$$this', '$$value'
                                ]
                            }
                        }
                    }
                }
            }, {
                '$project': {
                    '_id': 0, 
                    'first_doc': 0, 
                    'symptoms': 0
                }
            }
        ]

        cursor = None

        try:
            cursor = diseasesCollection.aggregate(Pipeline)

            if cursor._has_next():
                common_symptoms = cursor.next()

                if len(common_symptoms) == 0:
                    return jsonify({ "status": 404 })

                return jsonify({ "status": 200, "common_symptoms": common_symptoms })
            
            return jsonify({ "status": 404 })
        except Exception as e:
            print(e)
            return jsonify({ "status": 500 })
        finally:
            if cursor:
                cursor.close()
       


    @app.route("/get_suggestions", methods=['GET'])
    def get_suggestions():
        type = request.args.get('type')
        currentText = request.args.get('text')

        Pipeline = [
            {
                "$search": {
                    "index": "auto_suggestions_index",
                    "autocomplete": {
                        "query": currentText,
                        "path": type,
                        "fuzzy": {
                            "maxEdits": 2
                        }
                    }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "symptoms": 0
                }
            },
            {
                "$limit": 5
            }
        ]

        cursor = None
        try:
            cursor = diseasesCollection.aggregate(Pipeline)

            suggestions = []

            while cursor._has_next():
                suggestions.append(cursor.next())

            if len(suggestions) == 0:
                return jsonify({ "status": 404 })

            return jsonify({ "status": 200, "suggestions": suggestions })
        except Exception as e:
            print(e)
            return jsonify({ "status": 500 })
        finally:
            if cursor:
                cursor.close()

except Exception as e:
    print("Database connection failed")
    print(e)    

if __name__== "__main__":
     app.run(debug=True)
