FROM postgres:16-alpine

COPY init/ /docker-entrypoint-initdb.d/

ENV POSTGRES_DB=vault_db
ENV POSTGRES_USER=vault_user
ENV POSTGRES_PASSWORD=vault_password

EXPOSE 5432