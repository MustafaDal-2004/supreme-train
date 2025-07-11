from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# Dummy data for boards and threads (replace with DB later)
boards = [
    'tech', 'random', 'gaming', 'movies', 'music', 'science', 'books', 'sports',
    'art', 'history', 'travel', 'food', 'fitness', 'programming', 'photography',
    'fashion', 'cars', 'finance', 'education', 'politics', 'space', 'nature',
    'memes', 'anime', 'diy', 'gardening', 'pets', 'comics', 'languages', 'health'
]

# Each thread is: id, board, title, created
threads = [
    (1, 'tech', 'Welcome to Tech Board', datetime.now()),
    (2, 'random', 'Random Chat', datetime.now()),
]

# Posts: id, thread_id, content, created
posts = [
    (1, 1, 'This is the first post on tech board!', datetime.now()),
    (2, 2, 'Randomness starts here!', datetime.now()),
]

# Combined index route with optional letter filter
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
    # Get search query from URL parameters (GET)
    search_query = request.args.get('q', '').lower()

    # Filter threads by board
    board_threads = [t for t in threads if t[1] == board]

    # If search query exists, filter threads by title containing search string (case-insensitive)
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
    new_id = max([p[0] for p in posts]) + 1 if posts else 1
    posts.append((new_id, thread_id, content, datetime.now()))
    return redirect(url_for('view_thread', board=board, thread_id=thread_id))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
