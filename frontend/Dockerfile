# frontend/Dockerfile

# ---- Base Stage ----
# Use an official Node.js runtime as a parent image (LTS version recommended)
# Alpine versions are smaller
FROM node:20-alpine AS base

# Set working directory
WORKDIR /app

# Install necessary dependencies for builds if needed (e.g., python, make, g++)
# RUN apk add --no-cache libc6-compat python3 make g++

# ---- Dependencies Stage ----
FROM base AS deps
# Copy package.json and lock file
COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./
# Install dependencies based on the lock file
# Use frozen-lockfile to ensure exact dependencies are installed
RUN \
  if [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
  elif [ -f package-lock.json ]; then npm ci; \
  elif [ -f pnpm-lock.yaml ]; then yarn global add pnpm && pnpm i --frozen-lockfile; \
  else echo "Lockfile not found." && exit 1; \
  fi


# ---- Builder Stage ----
# Build the Next.js application
FROM base AS builder
WORKDIR /app
# Copy dependencies from the 'deps' stage
COPY --from=deps /app/node_modules ./node_modules
# Copy the rest of the application code
COPY . .

# Explicitly copy package.json and lock file again for the build script check
COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./

# Set environment variable for the build process using the build-time argument
ENV NEXT_PUBLIC_API_BASE_URL=ai-concierge-backend:5000

# Set NEXT_TELEMETRY_DISABLED to 1 to disable telemetry during build
ENV NEXT_TELEMETRY_DISABLED 1

# Build the Next.js application
# This command will vary based on your package manager
RUN \
  if [ -f yarn.lock ]; then yarn build; \
  elif [ -f package-lock.json ]; then npm run build; \
  elif [ -f pnpm-lock.yaml ]; then pnpm build; \
  else echo "Lockfile not found." && exit 1; \
  fi

# ---- Runner Stage (Final Image) ----
# Use a minimal Node.js image for the final stage
FROM base AS runner
WORKDIR /app

# Set environment variable for Node.js environment to production
ENV NODE_ENV production
# Disable telemetry
ENV NEXT_TELEMETRY_DISABLED 1

# Create a non-root user for security
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy necessary files from the builder stage
# Leverage Next.js standalone output for smaller image size
# Ensure `output: 'standalone'` is set in `next.config.mjs`
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
# Copy next.config.js if needed by standalone output (usually not, but safe to include)
# COPY --from=builder --chown=nextjs:nodejs /app/next.config.mjs ./next.config.mjs

# Change ownership of the app directory
# RUN chown -R nextjs:nodejs /app

# Switch to the non-root user
USER nextjs

# Expose the port the app runs on (default 3000)
EXPOSE 3000

# Set the default port environment variable (used by Next.js)
ENV PORT 3000
# Set HOSTNAME if needed, 0.0.0.0 makes it accessible from outside the container
ENV HOSTNAME 0.0.0.0

# Command to run the application using the standalone server.js
# This assumes `output: 'standalone'` is enabled in next.config.mjs
CMD ["node", "server.js"]

# --- Alternative Runner Stage (If NOT using standalone output) ---
# FROM base AS runner-legacy
# WORKDIR /app
# ENV NODE_ENV production
# ENV NEXT_TELEMETRY_DISABLED 1
# RUN addgroup --system --gid 1001 nodejs
# RUN adduser --system --uid 1001 nextjs
# COPY --from=builder --chown=nextjs:nodejs /app/public ./public
# COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
# COPY --from=builder --chown=nextjs:nodejs /app/node_modules ./node_modules
# COPY --from=builder --chown=nextjs:nodejs /app/package.json ./package.json
# USER nextjs
# EXPOSE 3000
# ENV PORT 3000
# ENV HOSTNAME 0.0.0.0
# CMD ["npm", "start"] # Or yarn start / pnpm start
