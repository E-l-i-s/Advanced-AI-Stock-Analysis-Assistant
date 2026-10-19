# FinSight AI — Generative UI Dashboard (Frontend)

The frontend is a single-page app built with **React 19**, **TypeScript**, and **Vite**. It shows the **Thesys C1Chat** component, which renders the backend's generative UI replies (charts, tables, metric cards, and buttons) in a chat thread.

---

## ✨ Features

- **Chat with generative UI**: `C1Chat` sends messages to `/api/chat` and renders the streamed response.
- **Quick Inquiries bar**: Five sample-prompt chips across the top. Clicking one puts the prompt into the chat input (press Enter to send). If the input box can't be found, the prompt is copied to the clipboard instead. A short toast confirms which happened.
- **Dark theme**: A black background with light text, set through `ThemeProvider mode="dark"` and the styles in `App.css`.
- **Dev proxy**: Vite forwards `/api` requests to `http://localhost:8888`.

---

## 🛠️ Tech Stack

- **React 19** and **TypeScript 5.9**
- **Vite 7** (dev server and build)
- **Thesys GenUI SDK** (`@thesysai/genui-sdk`): `C1Chat`, `ThemeProvider`
- **Crayon UI** (`@crayonai/react-ui`, `@crayonai/react-core`)
- **ESLint 9** with TypeScript and React hooks plugins
- **CSS** (`App.css`)

---

## 🚀 Getting Started

The backend must be running on port 8888 for chat to work. See the backend README.

### 1. Install Dependencies

```bash
npm install
```

### 2. Start the Dev Server

```bash
npm run dev
```

The app runs at `http://localhost:3000`.

### 3. Other Scripts

| Script            | What it does                                              |
| :---------------- | :-------------------------------------------------------- |
| `npm run build`   | Type-checks with `tsc -b`, then builds to `dist/`         |
| `npm run preview` | Serves the production build locally                       |
| `npm run lint`    | Runs ESLint on the project                                |

---

## 🔗 Architecture & Proxy

- `vite.config.ts` sets the dev server port to `3000` and proxies `/api/*` to `http://localhost:8888`.
- `App.tsx` passes `apiUrl="/api/chat"` and `agentName="Stock Analysis Assistant"` to `C1Chat`.
- `vite.config.ts` aliases the `@thesysai/genui-sdk/dist/genui-sdk.css` import to the file in `node_modules`, because the package's `exports` map does not expose it.

## 📁 Files

- `src/main.tsx`: React entry point.
- `src/App.tsx`: quick-prompt bar and `C1Chat` setup.
- `src/App.css`: dark theme and chat layout overrides.
- `index.html`: page title, meta tags, and Inter/Outfit fonts.
- `vite.config.ts`: dev port and `/api` proxy.
- `eslint.config.js`, `tsconfig*.json`: lint and TypeScript configuration.
