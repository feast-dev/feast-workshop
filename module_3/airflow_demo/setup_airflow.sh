# Airflow needs a home. `~/airflow` is the default, but you can put it
# somewhere else if you prefer (optional)
export AIRFLOW_HOME=$(pwd)/airflow_home
export AIRFLOW__CORE__LOAD_EXAMPLES=False

# Cleanup previous state, if it exists
rm -rf $AIRFLOW_HOME

# Install Airflow using the constraints file
AIRFLOW_VERSION=2.4.0
PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
# For example: 3.7
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
# For example: https://raw.githubusercontent.com/apache/airflow/constraints-2.4.0/constraints-3.7.txt
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"

# Setup Feast dags
mkdir -p $AIRFLOW_HOME/dags
cp dag.py $AIRFLOW_HOME/dags

# Setup dbt dags
cd ../dbt/feast_demo
cp -R * $AIRFLOW_HOME
cd $AIRFLOW_HOME

# The Standalone command will initialise the database, make a user,
# and start all components for you.
airflow standalone

# Visit localhost:8080 in the browser and use the admin account details
# shown on the terminal to login.
