FROM python:3.7

RUN pip install "feast[aws,redis]"

COPY feature_repo/feature_store.yaml feature_store.yaml

# Needed to reach online store within Docker network.
RUN sed -i 's/localhost:6379/redis:6379/g' feature_store.yaml
ENV FEAST_USAGE=False

CMD ["feast", "serve", "-h", "0.0.0.0"]