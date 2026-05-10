FROM astral/uv:python3.13-bookworm-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PYTHONPATH=/app/src \
	UV_LINK_MODE=copy

WORKDIR /app

COPY . .

RUN uv sync --no-dev --no-cache

CMD ["uv", "run", "uvicorn", "{{ cookiecutter.package_name }}.asgi:app", "--host", "{{ cookiecutter.prod_host }}", "--port", "{{ cookiecutter.prod_port }}"]
