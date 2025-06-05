FROM python:3.13-slim

# Środowiskowe zmienne optymalizujące kontener
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalacja zależności systemowych (jeśli potrzebujesz crona – aktualnie zakomentowane)
#RUN apt-get update  \
#    && apt-get install -y cron  \
#    && apt-get clean  \
#    && rm -rf /var/lib/apt/lists/*

# Tworzenie katalogów wymaganych do działania aplikacji
RUN mkdir -p /code/tsl_crldownloader/data &&  \
    mkdir -p /var/log  \
    && touch /var/log/django_cron.log /var/log/cron.log \

# VOLUME pozwala zachować dane między restartami kontenera
# VOLUME /code/tsl_crldownloader/data

# Ustaw katalog roboczy
WORKDIR /code

# Kopiuj i instaluj zależności (cache warstwa pip)
COPY requirements.txt .
RUN pip install --upgrade pip  \
    && pip install --no-cache-dir -r requirements.txt

# Skopiuj cały projekt
COPY . .

# Nadaj uprawnienia do skryptu wejściowego (na wszelki wypadek) - Zapewnij możliwość wykonania entrypointa
RUN chmod +x ./entrypoint.sh

EXPOSE 8000

# Uruchom skrypt jako punkt wejścia - Ustawiamy entrypoint jako główny proces
ENTRYPOINT ["./entrypoint.sh"]
