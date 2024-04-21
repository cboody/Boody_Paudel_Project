"""===============================================================================================
This code is the web application using Flask. Natural Language Processing is used for text analysis,
TF-IDF to generate a match score for user-input against each entry in the database. The database that
is used is the one created from code in scrapping_for_faculty_database.py. Flask takes input from
html files to create an interactive webpage.

19 April 2024
==============================================================================================="""


from flask import Flask, g, render_template, request, redirect, url_for
from scripts.analysis_script import pre_process_bio, vectorizer, cosine_similarity
import sqlite3

DATABASE = "faculty_database.db"
app = Flask(__name__)

def get_db():
    """-----------------------------------------------------------------------------
        Check for existing database connection
        Create new connection if there is none
        Returns database connection
    ------------------------------------------------------------------------------"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext # This tells function to happen when Flask is done with the database
def close_connection(exception):
    """-----------------------------------------------------------------------------
        Check for existing database connection
        Closes database connection if exists
    ------------------------------------------------------------------------------"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    """-----------------------------------------------------------------------------
            Returns the index.html template as homepage
    ------------------------------------------------------------------------------"""
    return render_template('index.html')

@app.route('/submit_form', methods=['POST'])
def submit_form():
    """-----------------------------------------------------------------------------
        Retrieves the data submitted by the user in html form and redirects to the 'show_result' route.

        Returns:
        A redirect response to the 'show_result' route with the form data as URL parameters.
    ------------------------------------------------------------------------------"""
    name = request.form.get('name')
    qualification = request.form.get('qualification')
    looking_for = request.form.get('looking_for')
    research = request.form.get('research')
    return redirect(url_for('show_result', name=name, qualification=qualification,
                            looking_for=looking_for, research=research))

@app.route('/result')
def show_result():
    """-----------------------------------------------------------------------------------------
    Give result page after processing user-input from index page and computing similarity scores.

    This function retrieves user inputs of user name and research interests statement.
    Accesses the 'Faculty' database to fetch faculty names and biographies. Using text preprocessing and
    TF-IDF vectorization, it calculates the cosine similarity between the user's research interest and each
    faculty member's biography. It returns the faculty members whose research interests most closely align
    with the user's, sorted by similarity score. A score of 1 means that the texts are identical. A score of 0 means
    there is nothing in common.

    The results and user-input information are then passed to Jinja template for rendering results.

    Parameters:
        - Extracts query parameters: 'name' and 'research'
          from the request form.

    Returns:
        - Rendered template ('result.html') with the following context:
            - name (str): The user's name.
            - research (str): The user's research interest.
            - results (list of dicts): A list containing dictionaries for each recommended faculty member,
              including their name and similarity score.
            - professor_dict (dict): A dictionary with faculty names as keys and biographies as values.
            - entry_results (int): The number of entries in the results.

    Raises:
        - sqlite3.Error: If there's an issue executing database operations.
        - Exception: For other unforeseen issues that may occur during processing.
    ---------------------------------------------------------------------------"""
    name = request.args.get('name')
    research = request.args.get('research')

    # Connect to database and fetch professor's bio from the database
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT name, biography FROM Faculty")
    entries = cur.fetchall()

    ################################### Analysis chunk starts #########################################
    # Create a dictionary with variable names as keys and research biographies as values
    professor_dict = {}
    for entry in entries:
        prof_name, prof_bio = entry
        professor_dict[prof_name] = prof_bio

    # Research statement of the student is pulled from the form
    student_bio = (research)

    # Create lemmatized token for student and make them a string
    student_token = pre_process_bio(student_bio)

    # Preparing document corpus using the token from professors and from user input
    docs = [student_token] + [pre_process_bio(prof_bio) for prof_name, prof_bio in professor_dict.items()]

    # Ensure each document is a string before passing to vectorizer
    docs = [doc if isinstance(doc, str) else ' '.join(doc) for doc in docs]
    tfidf_matrix = vectorizer.fit_transform(docs)

    # Calculating cosine similarities
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # Storing everything in results
    results = []
    counter = 0
    for i, (prof_name, prof_bio) in enumerate(professor_dict.items()):
        score = cosine_similarities[i]
        if score > 0.02:
            score = round(score, 3)
            results.append({
                "professor": prof_name,
                "similarity_score": score
            })

    results = sorted(results, key=lambda x: x["similarity_score"], reverse=True)
    entry_results = len(results)

    ################################### Analysis chunk ends #########################################

    # Returns the result.html template with all the information that needs to displayed in result.html
    return render_template('result.html', name=name, research=research, results=results,
                           professor_dict=professor_dict, entry_results=entry_results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
