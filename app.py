from flask import Flask, request
from flask.json import jsonify
from flask_pymongo import PyMongo
from pymongo.errors import BulkWriteError
from werkzeug.wrappers import Request


app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/todo_db"
mongodb_client = PyMongo(app)
db = mongodb_client.db


def oid_to_str(bson_object):
    bson_object['_id'] = str(bson_object['_id'])
    return bson_object


@app.route("/")
def home():
    todos = db.todos.find()
    return jsonify([oid_to_str(todo) for todo in todos])


@app.route("/add_one")
def add_one():
    db.todos.insert_one({'title': "todo title", 'body': "todo body"})
    return jsonify(message="success")


@app.route("/add_many")
def add_many():

    try:
        todo_many = db.todos.insert_many([
            {'_id': 1, 'title': "todo title one ", 'body': "todo body one "},
            {'_id': 8, 'title': "todo title two", 'body': "todo body two"},
            {'_id': 2, 'title': "todo title three", 'body': "todo body three"},
            {'_id': 9, 'title': "todo title four", 'body': "todo body four"},
            {'_id': 10, 'title': "todo title five", 'body': "todo body five"},
            {'_id': 5, 'title': "todo title six", 'body': "todo body six"},
        ], ordered=False)
    except BulkWriteError as e:

        return jsonify(message="duplicates encountered and ignored", details=e.details, inserted=e.details['nInserted'], duplicates=[x['op'] for x in e.details['writeErrors']])

    return jsonify(message="success", insertedIds=todo_many.inserted_ids)

@app.route("/get_todo/<int:todoId>")
def insert_one(todoId):
    todo = db.todos.find_one({"_id": todoId})
    return todo

@app.route("/replace_todo/<int:todoId>")
def replace_one(todoId):
    todo = db.todos.replace_one({'_id': todoId}, {'title' : "modified title"})
    return {'id': todo.raw_result}

@app.route("/update_todo/<int:todoId>")
def update_one(todoId):
    todo = db.todos.find_one_and_update({'_id': todoId}, {"$set": {'title' : "updated title"}})
    return todo

@app.route('/update_many')
def update_many():
    todo = db.todos.update_many({'title' : 'todo title two'}, {"$set": {'body' : 'updated body'}})
    return todo.raw_result

@app.route("/delete_todo/<int:todoId>")
def delete_one(todoId):
    todo = db.todos.find_one_and_delete({'_id': todoId})
    return todo

@app.route('/delete_many')
def delete_many():
    todo = db.todos.delete_many({'title' : 'todo title three'})
    return todo.raw_result


@app.route("/save_file", methods=['POST', 'GET'])
def save_file():
    upload_form = """<h1>Save file</h1>
                    <form method="POST" enctype="multipart/form-data">
                     <input type="file" name="file" id="file"><br><br>
                     <input type="submit">
                    </form>"""

    if request.method=='POST':
        if 'file' in request.files:
            file = request.files['file']
            mongodb_client.save_file(file.filename, file)
            return {"file name": file.filename}
    return upload_form


@app.route("/get_file/<filename>")
def get_file(filename):
    return mongodb_client.send_file(filename)


if __name__ == "__main__":
    app.run()
