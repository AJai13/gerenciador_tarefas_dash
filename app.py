from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taskmanager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    tasks_created = db.relationship('Task', backref='creator', lazy=True, foreign_keys='Task.creator_id')
    tasks_assigned = db.relationship('Task', backref='assignee', lazy=True, foreign_keys='Task.assignee_id')

    def __repr__(self):
        return f'<User {self.username}>'

# Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pendente')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return f'<Task {self.title}>'

# Routes for authentication
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validation
        if password != confirm_password:
            flash('As senhas não coincidem', 'danger')
            return redirect(url_for('register'))
        
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('Nome de usuário ou email já cadastrado', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('login'))
        except:
            flash('Ocorreu um erro. Tente novamente.', 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login falhou. Verifique seu nome de usuário e senha.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('login'))

# Routes for task management
@app.route('/')
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Faça login para acessar o dashboard', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    personal_tasks = Task.query.filter_by(assignee_id=user_id).all()
    created_tasks = Task.query.filter_by(creator_id=user_id).all()
    all_tasks = Task.query.all()
    users = User.query.all()
    
    # Count tasks by status
    pending_count = Task.query.filter_by(assignee_id=user_id, status='pendente').count()
    in_progress_count = Task.query.filter_by(assignee_id=user_id, status='em andamento').count()
    completed_count = Task.query.filter_by(assignee_id=user_id, status='concluída').count()
    
    return render_template('dashboard.html', 
                          personal_tasks=personal_tasks, 
                          created_tasks=created_tasks,
                          all_tasks=all_tasks,
                          users=users,
                          pending_count=pending_count,
                          in_progress_count=in_progress_count,
                          completed_count=completed_count)

@app.route('/tasks', methods=['GET'])
def tasks():
    if 'user_id' not in session:
        flash('Faça login para acessar as tarefas', 'warning')
        return redirect(url_for('login'))
    
    status_filter = request.args.get('status')
    user_id = session['user_id']
    
    if status_filter and status_filter != 'all':
        tasks = Task.query.filter_by(assignee_id=user_id, status=status_filter).all()
    else:
        tasks = Task.query.filter_by(assignee_id=user_id).all()
        
    users = User.query.all()
    return render_template('tasks.html', tasks=tasks, users=users, current_filter=status_filter)

@app.route('/task/new', methods=['GET', 'POST'])
def new_task():
    if 'user_id' not in session:
        flash('Faça login para criar tarefas', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        status = request.form['status']
        assignee_id = request.form['assignee_id']
        
        if not assignee_id:
            flash('É necessário atribuir a tarefa a um usuário', 'danger')
            users = User.query.all()
            return render_template('new_task.html', users=users)
        
        new_task = Task(
            title=title,
            description=description,
            status=status,
            creator_id=session['user_id'],
            assignee_id=assignee_id
        )
        
        try:
            db.session.add(new_task)
            db.session.commit()
            flash('Tarefa criada com sucesso!', 'success')
            return redirect(url_for('tasks'))
        except Exception as e:
            flash(f'Ocorreu um erro ao criar a tarefa: {str(e)}', 'danger')
    
    users = User.query.all()
    return render_template('new_task.html', users=users)

@app.route('/task/<int:task_id>', methods=['GET'])
def view_task(task_id):
    if 'user_id' not in session:
        flash('Faça login para visualizar tarefas', 'warning')
        return redirect(url_for('login'))
    
    task = Task.query.get_or_404(task_id)
    return render_template('view_task.html', task=task)

@app.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id):
    if 'user_id' not in session:
        flash('Faça login para editar tarefas', 'warning')
        return redirect(url_for('login'))
    
    task = Task.query.get_or_404(task_id)
    
    # Check if user has permission to edit (creator or assignee)
    if task.creator_id != session['user_id'] and task.assignee_id != session['user_id']:
        flash('Você não tem permissão para editar esta tarefa', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']
        task.status = request.form['status']
        assignee_id = request.form['assignee_id']
        
        if not assignee_id:
            flash('É necessário atribuir a tarefa a um usuário', 'danger')
            users = User.query.all()
            return render_template('edit_task.html', task=task, users=users)
            
        task.assignee_id = assignee_id
        
        try:
            db.session.commit()
            flash('Tarefa atualizada com sucesso!', 'success')
            return redirect(url_for('view_task', task_id=task.id))
        except Exception as e:
            flash(f'Ocorreu um erro ao atualizar a tarefa: {str(e)}', 'danger')
    
    users = User.query.all()
    return render_template('edit_task.html', task=task, users=users)

@app.route('/task/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    if 'user_id' not in session:
        flash('Faça login para excluir tarefas', 'warning')
        return redirect(url_for('login'))
    
    task = Task.query.get_or_404(task_id)
    
    # Check if user has permission to delete (only creator can delete)
    if task.creator_id != session['user_id']:
        flash('Você não tem permissão para excluir esta tarefa', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        db.session.delete(task)
        db.session.commit()
        flash('Tarefa excluída com sucesso!', 'success')
        return redirect(url_for('tasks'))
    except Exception as e:
        flash(f'Ocorreu um erro ao excluir a tarefa: {str(e)}', 'danger')
        return redirect(url_for('view_task', task_id=task.id))

# Create the database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
