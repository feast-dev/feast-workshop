FROM python:3.8

RUN pip install "feast[redis,postgres,snowflake]"

COPY feature_repo/feature_store.yaml feature_store.yaml

# Needed to reach online store and registry within Docker network.
RUN sed -i 's/localhost:6379/redis:6379/g' feature_store.yaml
RUN sed -i 's/127.0.0.1:55001/registry:5432/g' feature_store.yaml
ENV FEAST_USAGE=False

CMD ["feast", "serve", "-h", "0.0.0.0"]