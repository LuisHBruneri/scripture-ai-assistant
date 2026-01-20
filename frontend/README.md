# Scriptura AI Assistant App 📱

The official frontend for the Theological AI Agent. Built with Flutter to provide a beautiful, readable, and responsive interface for theological study.

## ✨ App Features
- **Parchment & Burgundy Theme**: A classic, book-like aesthetic designed for reading comfort.
- **Streaming Chat**: Responses appear in real-time, typed out just like a conversation.
- **Rich Text Support**: Full Markdown rendering for bold, italics, headers, and blockquotes.
- **Source Citation**: Automatically lists the Bible verses or books used to generate the answer.
- **History Management**: Automatically saves your chat history offline (using Hive) so you never lose a conversation.
- **Cross-Platform**: Runs smoothly on Android, iOS, and Web.

## 🚀 Getting Started

### Prerequisites
- Flutter SDK installed
- The backend running at `http://localhost:8001` (see root README)

### Run Locally (Classic)
```bash
# Get dependencies
flutter pub get

# Run on emulator or device
flutter run
```

### Run via Docker (Web)
To run the full stack including the frontend as a Web App:
```bash
docker-compose up --build
```
Access at `http://localhost:3000`.

### Connecting to Backend
By default, the app looks for the backend at:
- **Web (Docker)**: Use relative path (handled by Nginx).
- **Mobile (Emulator)**: `http://10.0.2.2:8001`.
- **iOS Simulator**: `http://localhost:8001`.

Change this logic in `lib/services/api_service.dart` if needed.

## 📦 Project Structure
- `lib/screens`: Main UI screens (ChatScreen).
- `lib/widgets`: Reusable UI components (Typingindicator).
- `lib/services`: API communication logic.
- `lib/models`: Data models for Messages.

## 🛠️ Troubleshooting
**Error: Connection Refused**
- Ensure your Docker backend is running.
- If on Android Emulator, check if you are using the correct localhost alias (`10.0.2.2`).
