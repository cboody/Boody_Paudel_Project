# Boody_Paudel_Project
This is the repository for Dr. Gribskov to view our Biocomputing Spring 2024 project

ACADEMIC MATCH MAKER
by: Samrat Paudel and Christina Boody

DESCRIPTION: This program is a Flask web application that gives the user a form to enter their name and research
statement. Then, it will compare the research statement to a database of faculty biographies scraped from the Purdue
University Biological Sciences Department Faculty website. TF-IDF algorithm is used to assign a weight to each word in
the documents based on how often the word appears. There is a list of words that we customized to not be considered.
After clicking the submission button, the user is shown a results page that shows the user input, and then the results
below. The results include a statement of the number of faculty they had a score above the specified threshold
(can be adjusted depending on how strict you want the search to be, and we can optimize it over time). Below this, the
faculty names and biographies are in score-order.

INSTALLATION: Clone this git repository:(https://github.com/cboody/Boody_Paudel_Project.git)

DEPENDENCIES REQUIRED: nltk, scikit-learn, beautifulsoup4, Flask, SQLite3.

HOW TO USE: Once the git repository is cloned, you will first need to run 'scraping_for_faculty_database.py' to create
the database 'faculty_database.db'. The output will show you the names of faculty members that duplicate entries were
avoided for. You don't need to do anything with this information, it is there to confirm no duplication. Then,
run 'web_app.py' and click on the 2nd development server link if using computer (type in 1st one if using phone
browser). Lastly, enter your name and research statement where prompted, and click the submission button. Your results
will be shown. A score of '1' means the text is identical and a score of '0' mean there is nothing in common. The
highest scoring matches will be shown first.
