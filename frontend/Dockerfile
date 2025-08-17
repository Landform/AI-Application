# my-ai-log-viewer/frontend/Dockerfile
# Stage 1: Build the React application
FROM node:18-alpine AS build

WORKDIR /app

# Set the PATH to include node_modules/.bin first
ENV PATH /app/node_modules/.bin:$PATH

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Ensure executables have correct permissions
RUN find /app/node_modules/.bin -type f -exec chmod +x {} \;

# Copy the rest of the frontend code
COPY . .

# Build the React app using the standard npm command
RUN npm run build

# Stage 2: Serve the application with Nginx
FROM nginx:alpine

# Remove default nginx config to avoid conflicts with our custom one
RUN rm /etc/nginx/conf.d/default.conf

# Copy the custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built React app into Nginx's public directory
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80 - Nginx will listen on this port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]