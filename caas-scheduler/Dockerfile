FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install ALL dependencies (including devDependencies for TypeScript build)
RUN npm install

# Copy source files
COPY tsconfig.json ./
COPY src/ ./src/

# Build TypeScript
RUN npm run build

# Remove devDependencies to reduce image size
RUN npm prune --production

EXPOSE 3001

# Run the compiled JavaScript
CMD ["node", "dist/index.js"]
