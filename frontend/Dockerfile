# my-ai-log-viewer/frontend/Dockerfile (FINAL VERSION WITH LOGGING FIX)

# --- Stage 1: Build the React application ---
# Use a Debian-based Node image for better compatibility
FROM node:18-bullseye-slim AS build

WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# --- Stage 2: Serve the application with Nginx ---
FROM nginx:alpine

# Copy the custom (now simplified) Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built React app from the 'build' stage
COPY --from=build /app/dist /usr/share/nginx/html

# --- NEW FIX ---
# Symlink Nginx log files to Docker's standard output/error streams.
# This is a more robust way to capture logs than using directives in nginx.conf.
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

# We can also add back the chown command, as it's good practice even if it wasn't the root cause.
RUN chown -R nginx:nginx /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]