# Cosual Frontend

A web application that transforms GitHub repos, raw code, or text descriptions into visual content -- architecture diagrams and cinematic video trailers.

Built with Vue 3, Tailwind CSS, and CodeMirror 6.

## Requirements

- Node.js 20.19+ or 22.12+
- npm 10+
- A running instance of the Cosual backend API

## Setup

1. Clone the repository:

```sh
git clone <repo-url>
cd cosual-frontend
```

2. Install dependencies:

```sh
npm install
```

3. Copy the environment file and configure the API base URL:

```sh
cp .env.example .env
```

Edit `.env` and set `VITE_API_BASE_URL` to your backend URL (defaults to `http://127.0.0.1:8000`).

4. Start the development server:

```sh
npm run dev
```

5. Build for production:

```sh
npm run build
```

6. Preview the production build:

```sh
npm run preview
```

## Docker

Build and run using Docker:

```sh
docker build -t cosual-frontend .
docker run -p 8080:80 cosual-frontend
```

To set the API base URL at build time:

```sh
docker build --build-arg VITE_API_BASE_URL=https://api.example.com -t cosual-frontend .
```

The container serves the app on port 80 using nginx.

## Project Structure

```
src/
  main.js               Entry point
  main.css              Global styles, CSS variables, Tailwind config
  App.vue               Root component with conditional nav
  router/index.js       Routes and navigation guard
  api/client.js         Axios instance and API methods
  stores/
    history.js          Local history tracking via localStorage
    generate.js         Generation form state and polling
  views/
    LandingView.vue     Intro page with animated title
    GenerateView.vue    Main form for creating content
    StatusView.vue      Polling status and result display
    HistoryView.vue     Grid of past generations
    HistoryDetailView.vue  Detail view with revision timeline
  components/
    AppNav.vue          Top navigation bar
    CodeEditor.vue      CodeMirror 6 editor wrapper
    StyleChips.vue      Single-select style preset chips
    AspectRatioPicker.vue  Aspect ratio selector
    PlatformPicker.vue  Platform selector (LinkedIn, Instagram, TikTok)
    CaptionBox.vue      Caption display with copy-to-clipboard
    RevisionChat.vue    Revision input with polling
    StatusBadge.vue     Colored status indicator
    ShareLinkedIn.vue   LinkedIn share button
```

## Environment Variables

| Variable             | Description                  | Default                   |
|----------------------|------------------------------|---------------------------|
| VITE_API_BASE_URL    | Backend API base URL         | http://127.0.0.1:8000    |

## How It Works

1. Enter a text description, GitHub URL, or paste raw code.
2. Choose output type (image or video), visual style, aspect ratio, and target platform.
3. Submit to generate visual content via the backend API.
4. View results, copy the generated caption, or share directly to LinkedIn.
5. Browse past generations in the history view. Revise image outputs with follow-up instructions.

All generation history is tracked locally in the browser using localStorage. There are no user accounts or server-side sessions.

Sharing is handled by opening the LinkedIn share dialog directly via URL -- no third-party sharing libraries are required.

## Tech Stack

- Vue 3 (Composition API, script setup)
- Vue Router 4
- Pinia
- Tailwind CSS 4
- Axios
- CodeMirror 6

## License

See LICENSE file for details.
