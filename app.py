import os
import hashlib
import boto3

from chalice import Chalice, Response, BadRequestError
from chalice import NotFoundError

app = Chalice(app_name='kurz')
app.debug = True

DDB = boto3.client('dynamodb')


@app.route('/', methods=['POST'])
def index():
    url = app.current_request.json_body.get('url', '')
    if not url:
        raise BadRequestError("Mussing URL")
    digest = hashlib.md5(url.encode('utf-8')).hexdigest()[:6]
    DDB.put_item(
                TableName=os.environ['APP_TABLE_NAME'],
                Item={'identifier': {'S': digest},
                      'url': {'S': url}})
    return {'shortened': digest}

@app.route('/{identifier}', methods=['GET'])
def retrieve(identifier):
    try:
        record = DDB.get_item(Key={'identifier': {'S': identifier}},
                              TableName=os.environ['APP_TABLE_NAME'])
    except Exception as e:
        raise NotFoundError(identifier)
    return Response(
                status_code=301,
                headers={'Location': record['Item']['url']['S']},
                body='')
# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
