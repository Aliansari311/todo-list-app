from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps

app = Flask(__name__)
app.secret_key = 'mySecretKey123'   # session data ko sign karne ke liye


# ---- helper: login check ko decorator bana diya, taake har route mein
# ---- copy-paste na karna pade ----
def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    return wrapper


def get_task_list():
    # session mein tasks list hamesha maujood ho, warna empty bana do
    if 'tasks' not in session:
        session['tasks'] = []
    return session['tasks']


def find_task(task_id):
    for t in get_task_list():
        if t['id'] == task_id:
            return t
    return None


@app.route('/')
@app.route('/filter/<filter_type>')
@login_required
def index(filter_type='all'):
    tasks = get_task_list()

    if filter_type == 'pending':
        shown_tasks = [t for t in tasks if t['status'] == 'Pending']
    elif filter_type == 'completed':
        shown_tasks = [t for t in tasks if t['status'] == 'Completed']
    else:
        shown_tasks = tasks

    return render_template('index.html', tasks=shown_tasks,
                            username=session['username'],
                            filter_type=filter_type)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        entered_name = request.form['username'].strip()
        session['username'] = entered_name
        session['tasks'] = []
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_task():
    if request.method == 'POST':
        tasks = get_task_list()

        # naya id purani list ke max id se +1 rakh diya (len+1 se
        # thora zyada safe hai agar beech mein koi task delete ho chuki ho)
        new_id = max([t['id'] for t in tasks], default=0) + 1

        new_task = {
            'id': new_id,
            'title': request.form['title'],
            'category': request.form['category'],
            'priority': request.form['priority'],
            'deadline': request.form['deadline'],
            'status': 'Pending'
        }
        tasks.append(new_task)
        session['tasks'] = tasks
        return redirect(url_for('index'))

    return render_template('add_task.html')


@app.route('/complete/<int:task_id>')
@login_required
def complete_task(task_id):
    task = find_task(task_id)
    if task:
        task['status'] = 'Completed'
        session['tasks'] = get_task_list()
    return redirect(url_for('index'))


@app.route('/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    remaining = [t for t in get_task_list() if t['id'] != task_id]
    session['tasks'] = remaining
    return redirect(url_for('index'))


@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = find_task(task_id)

    if request.method == 'POST' and task:
        task['title'] = request.form['title']
        task['category'] = request.form['category']
        task['priority'] = request.form['priority']
        task['deadline'] = request.form['deadline']
        session['tasks'] = get_task_list()
        return redirect(url_for('index'))

    return render_template('edit_task.html', task=task)


if __name__ == '__main__':
    app.run(debug=True)
