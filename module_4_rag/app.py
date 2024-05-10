from flask import (
    Flask,
    jsonify,
    request,
    render_template,
)
from flasgger import Swagger
from datetime import datetime

app = Flask(__name__)
swagger = Swagger(app)


@app.route("/get_documents")
def get_documents():
    """Example endpoint returning features by id
    This is using docstrings for specifications.
    ---
    parameters:
      - name: state
        type: string
        in: query
        required: true
        default: NJ
    responses:
      200:
        description: A JSON of documents
        schema:
          id: Document ID
          properties:
            is_gt_18_years_old:
              type: array
              items:
                schema:
                  id: value
                  type: number
    """
    question = request.form["question"]
    documents = store.get_online_documents(query)
    return render_template("documents.html", documents=documents)


@app.route("/")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)
