import json
import typesense

client = typesense.Client({
    'api_key': 'xyz',
    'nodes': [{
        'host': 'localhost',
        'port': '8108',
        'protocol': 'http'
    }],
    'connection_timeout_seconds': 2
})

# try:
#     client.collections['content'].delete()
# except typesense.exceptions.ObjectNotFound:
#     pass  

# index_schema = {
#     'name': 'content',
#     'fields': [
#         {'name': '_id', 'type': 'string', 'facet': True, 'searchable': True},
#         {'name': 'siteId', 'type': 'string', 'facet': True, 'searchable': True},
#         {'name': 'name', 'type': 'string', 'facet': True, 'searchable': True},
#         {'name': 'channel', 'type': 'string', 'facet': True, 'searchable': True},
#         {'name': 'details', 'type': 'string', 'facet': True, 'searchable': True},
#         {'name': 'language', 'type': 'string', 'facet': True, 'searchable': True},
#         {'name': 'content', 'type': 'string', 'facet': True, 'searchable': True},
#     ],
    # 'default_sorting_field': '_id'
# }

# client.collections.create(index_schema)

# Read data from the JSONL file line by line
with open('news17.json', 'r', errors='ignore') as file:
    val=json.load(file)
    c=0
    for v in val:
        # print(type(v))
        # print(v)
        v={"_id":v["_id"]["$oid"],"siteId":v["siteId"],"name":v["en"]["translatedTitle"],"channel":v["en"]["ChannelName"],"details":str(v["en"]),"language":v["en"]["languageCode"],"content":v["en"]["contentType"]}
        # ee
        try:
            c=c+1
            client.collections['content'].documents.create(v)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON at line: {e}")
    print(c)

      
# search_results = client.collections['content'].documents.search({
#     'q': '1',
#     'query_by': 'siteId',
# })

# for result in search_results['hits']:
#     print(result)

