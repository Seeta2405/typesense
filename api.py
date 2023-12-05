from flask import Flask, jsonify, request
from flask_cors import CORS 
import json
import typesense
# from typesense import Client
# from typesense.exceptions import HTTPError


app = Flask(__name__)
CORS(app) 

client = typesense.Client({
    'api_key': 'xyz',
    'nodes': [{
        'host': 'localhost',
        'port': '8108',
        'protocol': 'http'
    }],
    'connection_timeout_seconds': 2
})

collection_schema = {
    'name': 'content',
    'fields': [
        {'name': '_id', 'type': 'string', 'facet': True,'searchable': True},
        {'name': 'siteId', 'type': 'string', 'facet': True, 'searchable': True},
        {'name': 'name', 'type': 'string', 'facet': True,'searchable': True},
        {'name': 'details', 'type': 'string', 'facet': True,'searchable': True},
        {'name': 'channel', 'type': 'string', 'facet': True, 'searchable': True},
        {'name': 'language', 'type': 'string', 'facet': True, 'searchable': True},
        {'name': 'content', 'type': 'string', 'facet': True, 'searchable': True},
    ],
}

# try:
#     client.collections['content'].delete()
# except typesense.exceptions.ObjectNotFound:
#     pass  

# client.collections.create(collection_schema)

# Create a Record API
@app.route('/api/create_record', methods=['POST'])
def create_record():
    data = request.json

    document = {
        "_id": str(data["_id"]["$oid"]),
        "siteId": data["siteId"],
        "name": data["en"]["translatedTitle"],
        "details": str(data["en"]),
        "channel": str(data["en"]["ChannelName"]),
        "language": str(data["en"]["languageCode"]),
        "content": str(data["en"]["contentType"])
    }
    try:
        client.collections['content'].documents.create(document)
        return jsonify({"message": "Record created successfully!"})
    except json.JSONDecodeError as e:
        return jsonify({"message": f"Error decoding JSON: {e}"}), 400
    except Exception as e:
        return jsonify({"message": f"Error creating record: {e}"}), 500


# GET API to retrieve all records
@app.route('/api/get_records', methods=['GET'])
def get_records():
    try:
        # Retrieve all records from Typesense
        result = client.collections['content'].documents.search({'q': '*', 'per_page': 10})  # You can adjust 'per_page' as needed
        total_records = result['found']

        records = result['hits']

        response = {
            "total_records": total_records,
            "records": records
        }

        return jsonify(response)
    except typesense.exceptions.ObjectNotFound:
        return jsonify({"message": "Collection not found"}), 404
    except Exception as e:
        return jsonify({"message": f"Error retrieving records: {e}"}), 500


# API route to search by name
@app.route('/api/search_by_name', methods=['GET'])
def search_by_name():
    name_query = request.args.get('name', default='', type=str)

    if not name_query:
        return jsonify({"message": "Please provide a 'name' parameter"}), 400

    try:
        # Perform a search by name
        search_results = client.collections['content'].documents.search({
            'q': name_query,
            'query_by': 'name',
        })

        # Extract the number of records matched
        num_matched_records = search_results['found']

        # Extract the hits (matched records)
        matched_records = search_results['hits']

        # Construct the response
        response_data = {
            "num_matched_records": num_matched_records,
            "matched_records": matched_records
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"message": f"Error searching by name: {e}"}), 500
    

# API route to search by _id
@app.route('/api/search_by_id/<string:_id>', methods=['GET'])
def search_by_id(_id):
    try:
        search_results = client.collections['content'].documents.search({
            'q': _id,
            'query_by': '_id',
        })

        num_matched_records = search_results['found']
        matched_records = search_results['hits']

        response_data = {
            "num_matched_records": num_matched_records,
            "matched_records": matched_records
        }

        return jsonify(response_data)
    except Exception as e:
        return jsonify({"message": f"Error searching by _id: {e}"}), 500

    
# DELETE API to delete a record by _id
@app.route('/api/delete_record/<string:record_id>', methods=['DELETE'])
def delete_record(record_id):
    try:
        client.collections['content'].documents[record_id].delete()
        return jsonify({"message": f"Record with ID {record_id} deleted successfully"})
    except typesense.exceptions.ObjectNotFound:
        return jsonify({"message": f"Record with ID {record_id} not found"}), 404
    except Exception as e:
        return jsonify({"message": f"Error deleting record: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
