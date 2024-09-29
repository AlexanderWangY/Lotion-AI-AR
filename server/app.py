from flask import Flask, jsonify, request
from image_processing import extract_png_text
from sentiment_processing import get_likely_class_from_notes, get_likely_class_from_sentence, get_topics_gpt
# from database_actions import get_classes, upload_note
from mongo_actions import get_classes, upload_note, create_user, add_class, grab_notes, find_notes_with_topics
app = Flask(__name__)


@app.route('/')
def home():
    return "Shellhacks 2024 Backend. Written by Hugo and Alex L."


@app.route('/api/upload', methods=['POST'])
def upload():
    data = request.get_json()
    image_data = data["image"] #base 64 png data
    user_id = data["userId"]
    # Process into pure text
    text = extract_png_text(image_data)

    # Possible Classes
    user_classes = get_classes(user_id)

    # Using the Text, process into a class, and topics
    likely_class = get_likely_class_from_notes(text, user_classes)

    topics = get_topics_gpt(text, likely_class)

    topics = topics.split(", ")

    upload_note(user_id, likely_class, image_data, topics)

    # Upload to appropriate class folder in database, with the topics attached

    return jsonify({"class": f"{likely_class}",
                    "topics": f"{topics}",
                    "text": text})


@app.route('/api/query', methods=['post'])
def query():
    data = request.get_json()
    
    text = data["text"] 
    user_id = data["userId"]

    user_classes = get_classes(user_id)

    # Using the Text, process into a class, and topics
    likely_class = get_likely_class_from_sentence(text, user_classes)
    
    topics = get_topics_gpt(text, likely_class)

    topics = topics.split(", ")

    results = find_notes_with_topics(user_id, likely_class, topics)

    # Get top 5 related topics based on the class. Run sentiment comparison on class notes, and choose 5 most related

    return jsonify(results)


@app.route('/api/create_user', methods = ['post'])
def create_new_user():
    # needs user id
    data = request.get_json()
    user_id = data["userId"]
    create_user(user_id)
    return jsonify({"message": f"{user_id} created"})


@app.route('/api/add_classes', methods = ['post'])
def add_classes():
    data = request.get_json()
    user_id = data["userId"]
    classes_to_add = data["classes"]
    for n in classes_to_add:
        add_class(user_id, n)
    # needs user id
    # needs list of strings, representing classes
    return jsonify({"message": "added class"})


@app.route('/api/get_subjects', methods=['post'])
def get_subjects():
    data = request.get_json()
    user_id = data["userId"]
    user_classes = get_classes(user_id)
    return jsonify({"classes": f"{user_classes}"})


@app.route('/api/get_notes', methods=['post'])
def get_notes():
    data = request.get_json()
    user_id = data["userId"]
    requested_class = data["class"]
    result = grab_notes(user_id, requested_class)
    return jsonify({"note_list": result})

@app.route("/api/ar_video_recognition", methods=['post'])
def ar_video_request():
    data = request.get_json()
    user_id = data["userId"]
    image_data = data["image"]

    text = extract_png_text(image_data)

    likely_class = get_likely_class_from_sentence(text)

    topics = get_topics_gpt(text, likely_class)

    topics = topics.split(", ")

    results = find_notes_with_topics(user_id, likely_class, topics)

    return jsonify(results)


    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
