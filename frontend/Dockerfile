# frontend/Dockerfile

########################################
# 1) Build-Stage: Node & Vite Build
########################################
FROM node:18-alpine AS build

# Arbeitsverzeichnis
WORKDIR /app

# Abhängigkeiten kopieren & installieren
COPY package*.json ./
RUN npm ci

# Quellcode kopieren und bauen
COPY . .
RUN npm run build

########################################
# 2) Production-Stage: Nginx
########################################
FROM nginx:stable-alpine

# Vorherige Inhalte löschen
RUN rm -rf /usr/share/nginx/html/*

# Aus der Build-Stage die statischen Dateien übernehmen
COPY --from=build /app/dist /usr/share/nginx/html

# Port 80 freigeben
EXPOSE 80

# Nginx im Vordergrund starten
CMD ["nginx", "-g", "daemon off;"]
