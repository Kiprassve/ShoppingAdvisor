# Naudojame oficialų Python atvaizdą. 'slim' versija užima mažiau vietos.
FROM python:3.11-slim

# Nustatome darbinį katalogą konteineryje
WORKDIR /app

# Nukopijuojame priklausomybių failą į konteinerį
COPY requirements.txt .

# Įdiegiame visas Python bibliotekas
RUN pip install --no-cache-dir -r requirements.txt

# Nukopijuojame visą tavo projekto turinį (app.py, Crawler aplanką ir t.t.)
COPY . .

# Pasakome Docker, kad naudosime 5000 prievadą
EXPOSE 5000

# Paleidžiame Flask aplikaciją
CMD ["python", "app.py"]