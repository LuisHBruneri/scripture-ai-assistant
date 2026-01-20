# Stage 1: Build the Flutter Web App
FROM ghcr.io/cirruslabs/flutter:stable AS build

WORKDIR /app

# Copy pubspec files first for better caching
COPY pubspec.yaml pubspec.lock ./
RUN flutter pub get

# Copy the rest of the app source code
COPY . .

# Build for web
# --base-href / ensures correct routing if needed, usually default is /
RUN flutter build web --release

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy the build output from the previous stage
COPY --from=build /app/build/web /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
