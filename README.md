# stock analysis assistant

## Features

- **Interactive Generative UI**: Renders real-time interactive charts, buttons, valuation forms, and metrics directly within the chat stream.
- **Live Backend Health Monitor**: Automatically checks backend connectivity and API key status on launch.
- **Quick Inquiries Bar**: One-click prompt inspiration chips (e.g., Comparing tickers, Balance sheets, News feeds, Historical charts) with clipboard copy feedback.
- **Dark Mode UI**: Sleek, institutional-grade dark interface styling with glassmorphism and subtle gradients.
- **Local Dev Proxy**: Configured Vite proxy routing `/api` calls directly to `http://localhost:8888`.

---

## Getting Started

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Development Server
```bash
npm run dev
```
The app will launch at `http://localhost:3000`.

### 3. Build for Production
```bash
npm run build
```
Generates optimized production assets in the `dist/` directory.

---

## Architecture & Proxy Configuration

The frontend communicates with the backend via Vite's proxy configured in `vite.config.ts`:
- Requests to `/api/*` are automatically forwarded to `http://localhost:8888`.
- Server-Sent Events (SSE) stream tokens directly into the `C1Chat` component.
