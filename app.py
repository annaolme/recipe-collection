from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('recipes.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS recipes
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     title TEXT NOT NULL,
                     category TEXT,
                     ingredients TEXT NOT NULL,
                     instructions TEXT NOT NULL,
                     prep_time TEXT,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db()
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    if search:
        recipes = conn.execute('SELECT * FROM recipes WHERE title LIKE ? ORDER BY created_at DESC',
                              ('%' + search + '%',)).fetchall()
    elif category:
        recipes = conn.execute('SELECT * FROM recipes WHERE category = ? ORDER BY created_at DESC',
                              (category,)).fetchall()
    else:
        recipes = conn.execute('SELECT * FROM recipes ORDER BY created_at DESC').fetchall()
    categories = conn.execute('SELECT DISTINCT category FROM recipes WHERE category IS NOT NULL').fetchall()
    conn.close()
    return render_template('index.html', recipes=recipes, categories=categories,
                         current_category=category, search=search)

@app.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
    conn = get_db()
    recipe = conn.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,)).fetchone()
    conn.close()
    if recipe is None:
        return redirect(url_for('index'))
    return render_template('recipe.html', recipe=recipe)

@app.route('/add', methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        title = request.form['title']
        category = request.form.get('category', '')
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        prep_time = request.form.get('prep_time', '')
        if title and ingredients and instructions:
            conn = get_db()
            conn.execute('INSERT INTO recipes (title, category, ingredients, instructions, prep_time) VALUES (?, ?, ?, ?, ?)',
                        (title, category, ingredients, instructions, prep_time))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/delete/<int:recipe_id>')
def delete_recipe(recipe_id):
    conn = get_db()
    conn.execute('DELETE FROM recipes WHERE id = ?', (recipe_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)
