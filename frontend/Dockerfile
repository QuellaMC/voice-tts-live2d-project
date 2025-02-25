FROM node:18-alpine

WORKDIR /app

# Install dependencies with fallback options
COPY package.json package-lock.json* ./
RUN npm ci || npm install || npm install --legacy-peer-deps

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 3000

# Development mode
CMD ["npm", "run", "dev"] 