#!/bin/bash

# Ustawienia kontenera
CONTAINER_NAME="sqlserver"
SA_PASSWORD="Database!2021"
LOCAL_CSV_DIR="/home/artem_dychenko/Documents/HD_labs/fake-data-generator/generated_data/"  # ścieżka do katalogu z plikami CSV na komputerze
CONTAINER_CSV_DIR="/home/"  # Ścieżka wewnątrz kontenera

# Sprawdzenie, czy kontener już istnieje
if [ $(docker ps -a -q -f name=$CONTAINER_NAME | wc -l) -gt 0 ]; then
    echo "Kontener $CONTAINER_NAME już istnieje. Usuwam go..."
    docker rm -f $CONTAINER_NAME
fi

# Uruchomienie nowego kontenera z zamontowanym katalogiem
echo "Uruchamiam kontener SQL Server..."
docker run -e 'ACCEPT_EULA=Y' -e "SA_PASSWORD=$SA_PASSWORD" --name $CONTAINER_NAME \
    -p 1433:1433 \
    -v "$LOCAL_CSV_DIR:$CONTAINER_CSV_DIR" \
    -d mcr.microsoft.com/mssql/server:2019-latest

echo "Kontener $CONdocTAINER_NAME uruchomiony."
echo "CSV pliki są dostępne wewnątrz kontenera pod: $CONTAINER_CSV_DIR"
