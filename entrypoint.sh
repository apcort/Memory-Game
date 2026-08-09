#!/bin/sh
# Script de inicialización: espera a la base de datos, aplica migraciones, recolecta estáticos y arranca Django.
set -e

while ! nc -z "${DB_HOST:-db}" "${DB_PORT:-5432}"; do
  sleep 0.5
done
echo "Base de datos disponible."

python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "Iniciando servidor Django"
exec python manage.py runserver 0.0.0.0:8000
