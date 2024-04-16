from flask import (
    Flask,
    jsonify,
    request,
    render_template,
)
from flasgger import Swagger
from datetime import datetime
from get_features import (
    get_onboarding_features,
    get_onboarding_score,
    get_daily_features,
    get_daily_score,
)
from ml import make_risk_decision

app = Flask(__name__)
swagger = Swagger(app)


@app.route("/")
def onboarding_page():
    return render_template("index.html")


@app.route("/home")
def home_page():
    return render_template("home.html")


@app.route("/onboarding-risk-features/", methods=["POST"])
def onboarding_features():
    """Example endpoint returning features by id
    This is using docstrings for specifications.
    ---
    parameters:
      - name: state
        type: string
        in: query
        required: true
        default: NJ

      - name: ssn
        type: string
        in: query
        required: true
        default: 123-45-6789

      - name: dl
        type: string
        in: query
        required: true
        default: some-dl-number

      - name: dob
        type: string
        in: query
        required: true
        default: 12-23-2000
    responses:
      200:
        description: A JSON of features
        schema:
          id: OnboardingFeatures
          properties:
            is_gt_18_years_old:
              type: array
              items:
                schema:
                  id: value
                  type: number
            is_valid_state:
              type: array
              items:
                schema:
                  id: value
                  type: number
            is_previously_seen_ssn:
              type: array
              items:
                schema:
                  id: value
                  type: number
            is_previously_seen_dl:
              type: array
              items:
                schema:
                  id: value
                  type: number
    """
    r = request.args
    feature_vector = get_onboarding_features(
        r.get("state"), r.get("ssn"), r.get("dl"), r.get("dob")
    )
    return jsonify(feature_vector)


if __name__ == "__main__":
    app.run(debug=True)
