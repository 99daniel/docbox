# frontend/Dockerfile

########################################
# 1) Build-Stage mit Node & Vite
########################################
FROM node:18-alpine AS build
WORKDIR /app

# Dependencies installieren
COPY package*.json ./
RUN npm ci

# Quellcode kopieren & bauen
COPY . .
RUN npm run build

########################################
# 2) Production-Stage mit Nginx
########################################
FROM nginx:stable-alpine

# Vorherige Dateien löschen
RUN rm -rf /usr/share/nginx/html/*

# Bau-Ergebnis übernehmen
COPY --from=build /app/dist /usr/share/nginx/html

# HTTP-Port
EXPOSE 80

# Nginx im Vordergrund starten
CMD ["nginx", "-g", "daemon off;"]
