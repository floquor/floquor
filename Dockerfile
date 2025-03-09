FROM node:22.14 AS frontend-builder
WORKDIR /app

RUN npm install -g pnpm

COPY floquor-frontend /app/
RUN rm -rf /app/node_modules && \
    rm -rf /app/.next

RUN pnpm install
RUN pnpm build

FROM python:3.13.2-alpine3.21
WORKDIR /app

COPY floquor /app/
COPY --from=frontend-builder /app/out /app/static

RUN pip install -r requirements.txt && \
    pip install -r plugins/llm/requirements.txt

ENV PATH="/app/venv/bin:$PATH"

EXPOSE 8000

CMD ["python", "main.py"]
