FROM python:3.13-slim

WORKDIR /app

RUN pip install poetry

# Install dependencies for Chrome and Chromedriver
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    libx11-dev \
    libxcomposite1 \
    libxrandr2 \
    libxss1 \
    libgdk-pixbuf2.0-0 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libnspr4 \
    libnss3 \
    xdg-utils \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable

# Install Chromedriver
RUN wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip -P /tmp && \
    unzip /tmp/chromedriver_linux64.zip -d /usr/local/bin && \
    rm /tmp/chromedriver_linux64.zip

# Set up the environment for poetry
COPY pyproject.toml poetry.lock ./
COPY . .

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

EXPOSE 8000

CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
