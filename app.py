from flask import Flask, render_template, request, redirect, url_for, abort, jsonify
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Config for file uploads
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Helper function to validate files
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Dummy data
boards = ['tech', 'random', 'gaming', 'movies', 'music', 'science', 'books', 'sports',
    'art', 'history', 'travel', 'food', 'fitness', 'programming', 'photography',
    'fashion', 'cars', 'finance', 'education', 'politics', 'space', 'nature',
    'memes', 'anime', 'diy', 'gardening', 'pets', 'comics', 'languages', 'health']

threads = [
    (1, 'tech', 'Welcome to Tech Board', datetime.now()),
    (2, 'random', 'Random Chat', datetime.now()),
]

# Each post: id, thread_id, content, image_path
posts = [
    (1, 1, 'This is the first post on tech board!', None),
    (2, 2, 'Randomness starts here!', None),
]

@app.route('/')
@app.route('/boards/<letter>/')
def index(letter=None):
    if letter and letter.isalpha() and len(letter) == 1:
        filtered_boards = [b for b in boards if b.lower().startswith(letter.lower())]
    else:
        filtered_boards = boards
    return render_template('index.html', boards=filtered_boards, letter=letter)

@app.route("/<board>/")
def board_view(board):
    search_query = request.args.get('q', '').lower()
    board_threads = [t for t in threads if t[1] == board]

    if search_query:
        board_threads = [t for t in board_threads if search_query in t[2].lower()]
    return render_template('board.html', board=board, threads=board_threads)

@app.route("/<board>/new", methods=['POST'])
def new_thread(board):
    title = request.form['title']
    new_id = max([t[0] for t in threads]) + 1 if threads else 1
    threads.append((new_id, board, title, datetime.now()))
    return redirect(url_for('board_view', board=board))

@app.route("/<board>/<int:thread_id>/")
def view_thread(board, thread_id):
    thread = next((t for t in threads if t[0] == thread_id), None)
    thread_posts = [p for p in posts if p[1] == thread_id]
    return render_template('thread.html', thread=thread, posts=thread_posts)

@app.route("/<board>/<int:thread_id>/reply", methods=['POST'])
def reply(board, thread_id):
    content = request.form['content']
    image = request.files.get('image')

    image_path = None
    if image and image.filename != '':
        if allowed_file(image.filename):
            ext = image.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{ext}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(unique_filename))

            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            image.save(save_path)

            image_path = f'uploads/{unique_filename}'
        else:
            abort(400, description="Invalid file type.")

    new_id = max([p[0] for p in posts]) + 1 if posts else 1
    posts.append((new_id, thread_id, content, image_path))

    return redirect(url_for('view_thread', board=board, thread_id=thread_id))

@app.errorhandler(413)
def file_too_large(e):
    return "File is too large (max 2MB).", 413

@app.route("/<board>/<int:thread_id>/posts")
def get_posts(board, thread_id):
    thread_posts = [p for p in posts if p[1] == thread_id]
    post_data = [
        {"id": p[0], "content": p[2], "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        for p in thread_posts
    ]
    return jsonify(post_data)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

